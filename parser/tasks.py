import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone

from celery_app import celery_app
from database import get_db_session, create_tables
from models import Car, ParseSession
from parser import EncarParser

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_json_data(data, filename):
    filepath = Path(f"/app/{filename}")
    logger.info(f"Saving data to {filepath}")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"Successfully saved {len(data.get('cars', []))} cars to {filename}")

def load_previous_cars():
    filepath = Path("/app/current_cars.json")
    logger.info(f"Loading previous cars from {filepath}")
    
    if not filepath.exists():
        logger.info("No previous cars file found - this might be the first run")
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        cars = {car['encar_id']: car for car in data.get('cars', [])}
        logger.info(f"Loaded {len(cars)} previous cars")
        return cars
    except Exception as e:
        logger.error(f"Failed to load previous cars: {e}")
        return {}

def calculate_differences(current_cars, previous_cars):
    logger.info(f"Calculating differences between {len(current_cars)} current and {len(previous_cars)} previous cars")
    
    current_ids = set(current_cars.keys())
    previous_ids = set(previous_cars.keys())
    
    new_car_ids = current_ids - previous_ids
    new_cars = [current_cars[car_id] for car_id in new_car_ids]
    
    removed_car_ids = previous_ids - current_ids
    
    updated_cars = []
    common_ids = current_ids & previous_ids
    
    logger.info(f"Found {len(new_car_ids)} new cars, {len(removed_car_ids)} removed cars, checking {len(common_ids)} for updates")
    
    for car_id in common_ids:
        current_car = current_cars[car_id]
        previous_car = previous_cars[car_id]
        
        fields_to_compare = ['price', 'mileage', 'sales_status', 'modified_date', 'office_city_state', 'office_name', 'dealer_name']
        
        has_changes = False
        changes = {}
        
        for field in fields_to_compare:
            current_value = current_car.get(field)
            previous_value = previous_car.get(field)
            
            if current_value != previous_value:
                has_changes = True
                changes[field] = {'old': previous_value, 'new': current_value}
        
        if has_changes:
            current_car['changes'] = changes
            updated_cars.append(current_car)
    
    logger.info(f"Found {len(updated_cars)} updated cars")
    return new_cars, updated_cars, removed_car_ids

@celery_app.task(bind=True, name='tasks.parse_encar_data')
def parse_encar_data(self):
    logger.info("Starting Encar data parsing task")
    
    try:
        logger.info("Creating database tables if they don't exist")
        create_tables()
        logger.info("Database tables ready")
        
        logger.info("Initializing parser")
        parser = EncarParser()
        
        logger.info("Starting data parsing from Encar API")
        parse_result = asyncio.run(parser.parse_all_configurations())
        
        if parse_result.error_message:
            logger.error(f"Parsing failed: {parse_result.error_message}")
            return {
                'status': 'failed', 
                'error': parse_result.error_message, 
                'session_id': parse_result.session_id
            }
        
        logger.info(f"Parsing completed successfully in {parse_result.duration_seconds:.2f} seconds")
        logger.info(f"Found {parse_result.total_cars_found} total unique cars")
        
        current_cars = {car['encar_id']: car for car in parse_result.new_cars}
        
        with get_db_session() as db_session:
            logger.info("Creating parse session record")
            parse_session = ParseSession(
                session_id=parse_result.session_id,
                started_at=datetime.now(timezone.utc),
                status='running'
            )
            db_session.add(parse_session)
            db_session.flush()
            
            logger.info("Checking for existing cars in database")
            existing_cars = {car.encar_id: car for car in db_session.query(Car).filter(Car.is_active == True).all()}
            is_first_run = len(existing_cars) == 0
            
            logger.info(f"Database currently has {len(existing_cars)} active cars")
            
            if is_first_run:
                logger.info("First run detected - adding all cars as new")
                
                new_count = 0
                for car_data in current_cars.values():
                    try:
                        car = Car(**car_data)
                        db_session.add(car)
                        new_count += 1
                        
                        if new_count % 1000 == 0:
                            logger.info(f"Added {new_count} cars so far...")
                            
                    except Exception as e:
                        logger.error(f"Failed to add car {car_data.get('encar_id')}: {e}")
                
                updated_count = 0
                removed_count = 0
                
                logger.info(f"Added {new_count} new cars to database")
                
                save_json_data({
                    'session_id': parse_result.session_id,
                    'timestamp': datetime.now().isoformat(),
                    'total_cars': len(current_cars),
                    'cars': list(current_cars.values())
                }, "current_cars.json")
                
            else:
                logger.info("Incremental update - calculating differences")
                
                previous_cars = load_previous_cars()
                new_cars, updated_cars, removed_car_ids = calculate_differences(current_cars, previous_cars)
                
                logger.info(f"Changes summary:")
                logger.info(f"  New cars: {len(new_cars)}")
                logger.info(f"  Updated cars: {len(updated_cars)}")
                logger.info(f"  Removed cars: {len(removed_car_ids)}")
                
                logger.info("Adding new cars to database")
                new_count = 0
                for car_data in new_cars:
                    try:
                        car = Car(**car_data)
                        db_session.add(car)
                        new_count += 1
                        
                        if new_count % 100 == 0:
                            logger.info(f"Added {new_count}/{len(new_cars)} new cars...")
                            
                    except Exception as e:
                        logger.error(f"Failed to add new car {car_data.get('encar_id')}: {e}")
                
                logger.info("Updating existing cars in database")
                updated_count = 0
                for car_data in updated_cars:
                    try:
                        car = db_session.query(Car).filter(Car.encar_id == car_data['encar_id']).first()
                        if car:
                            for field, value in car_data.items():
                                if field != 'changes' and hasattr(car, field):
                                    setattr(car, field, value)
                            car.last_seen_at = datetime.now(timezone.utc)
                            updated_count += 1
                            
                            if updated_count % 100 == 0:
                                logger.info(f"Updated {updated_count}/{len(updated_cars)} cars...")
                                
                    except Exception as e:
                        logger.error(f"Failed to update car {car_data.get('encar_id')}: {e}")
                
                logger.info("Marking removed cars as inactive")
                removed_count = 0
                for encar_id in removed_car_ids:
                    try:
                        car = db_session.query(Car).filter(Car.encar_id == encar_id).first()
                        if car and car.is_active:
                            car.is_active = False
                            removed_count += 1
                            
                            if removed_count % 100 == 0:
                                logger.info(f"Removed {removed_count}/{len(removed_car_ids)} cars...")
                                
                    except Exception as e:
                        logger.error(f"Failed to remove car {encar_id}: {e}")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if new_cars:
                    logger.info(f"Saving {len(new_cars)} new cars to file")
                    save_json_data({
                        'session_id': parse_result.session_id, 
                        'timestamp': timestamp, 
                        'cars': new_cars
                    }, f"new_cars_{timestamp}.json")
                
                if updated_cars:
                    logger.info(f"Saving {len(updated_cars)} updated cars to file")
                    save_json_data({
                        'session_id': parse_result.session_id, 
                        'timestamp': timestamp, 
                        'cars': updated_cars
                    }, f"updated_cars_{timestamp}.json")
                
                if removed_car_ids:
                    logger.info(f"Saving {len(removed_car_ids)} removed car IDs to file")
                    save_json_data({
                        'session_id': parse_result.session_id, 
                        'timestamp': timestamp, 
                        'car_ids': list(removed_car_ids)
                    }, f"removed_cars_{timestamp}.json")
                
                logger.info("Saving complete current dataset")
                save_json_data({
                    'session_id': parse_result.session_id,
                    'timestamp': timestamp,
                    'total_cars': len(current_cars),
                    'cars': list(current_cars.values())
                }, "current_cars.json")
            
            logger.info("Updating parse session with final results")
            parse_session.completed_at = datetime.now(timezone.utc)
            parse_session.status = 'completed'
            parse_session.total_cars_found = parse_result.total_cars_found
            parse_session.new_cars_added = new_count
            parse_session.cars_updated = updated_count
            parse_session.cars_removed = removed_count
            
            logger.info("Committing all changes to database")
            db_session.commit()
        
        result = {
            'status': 'completed',
            'session_id': parse_result.session_id,
            'total_cars_found': parse_result.total_cars_found,
            'new_cars_added': new_count,
            'cars_updated': updated_count,
            'cars_removed': removed_count,
            'duration_seconds': parse_result.duration_seconds,
            'is_first_run': is_first_run
        }
        
        logger.info("Task completed successfully!")
        logger.info(f"Final summary: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Task failed with error: {e}", exc_info=True)
        return {'status': 'failed', 'error': str(e)}

@celery_app.task(name='tasks.test_task')
def test_task():
    """Simple test task to verify Celery is working"""
    logger.info("Test task started")
    
    try:
        with get_db_session() as db_session:
            result = db_session.execute("SELECT 1").scalar()
            logger.info(f"Database connection test: {result}")
        
        import time
        time.sleep(2)
        
        logger.info("Test task completed successfully")
        return {
            'status': 'success',
            'message': 'Test task completed',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Test task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }
