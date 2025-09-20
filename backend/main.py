from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

import src.models as models
import src.schemas as schemas
from src.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Encar Парсер", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173","http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Encar Парсер API"}

@app.get("/cars", response_model=List[schemas.CarSummary])
def get_cars(
    manufacturer: Optional[str] = Query(None),
    fuel_type: Optional[str] = Query(None),
    transmission: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_year: Optional[float] = Query(None),
    max_year: Optional[float] = Query(None),
    office_city_state: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(models.Car).filter(models.Car.is_active == True)
    
    if manufacturer:
        query = query.filter(models.Car.manufacturer.ilike(f"%{manufacturer}%"))
    if fuel_type:
        query = query.filter(models.Car.fuel_type.ilike(f"%{fuel_type}%"))
    if transmission:
        query = query.filter(models.Car.transmission.ilike(f"%{transmission}%"))
    if min_price is not None:
        query = query.filter(models.Car.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Car.price <= max_price)
    if min_year is not None:
        query = query.filter(models.Car.year >= min_year)
    if max_year is not None:
        query = query.filter(models.Car.year <= max_year)
    if office_city_state:
        query = query.filter(models.Car.office_city_state.ilike(f"%{office_city_state}%"))

    cars = query.offset(offset).limit(limit).all()
    return cars

@app.get("/cars/{car_id}", response_model=schemas.Car)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(
        models.Car.id == car_id,
        models.Car.is_active == True
    ).first()
    
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    
    return car

@app.get("/cars/filters/options")
def get_filter_options(db: Session = Depends(get_db)):
    manufacturers = db.query(models.Car.manufacturer).distinct().filter(
        models.Car.manufacturer.isnot(None),
        models.Car.is_active == True
    ).all()
    
    fuel_types = db.query(models.Car.fuel_type).distinct().filter(
        models.Car.fuel_type.isnot(None),
        models.Car.is_active == True
    ).all()
    
    transmissions = db.query(models.Car.transmission).distinct().filter(
        models.Car.transmission.isnot(None),
        models.Car.is_active == True
    ).all()
    
    cities = db.query(models.Car.office_city_state).distinct().filter(
        models.Car.office_city_state.isnot(None),
        models.Car.is_active == True
    ).all()
    
    from sqlalchemy import func
    price_range = db.query(
        func.min(models.Car.price),
        func.max(models.Car.price)
    ).filter(
        models.Car.price.isnot(None),
        models.Car.is_active == True
    ).first()
    
    year_range = db.query(
        func.min(models.Car.year),
        func.max(models.Car.year)
    ).filter(
        models.Car.year.isnot(None),
        models.Car.is_active == True
    ).first()
    
    return {
        "manufacturers": [m[0] for m in manufacturers if m[0]],
        "fuel_types": [f[0] for f in fuel_types if f[0]],
        "transmissions": [t[0] for t in transmissions if t[0]],
        "cities": [c[0] for c in cities if c[0]],
        "price_range": {
            "min": price_range[0] if price_range[0] else 0,
            "max": price_range[1] if price_range[1] else 0
        },
        "year_range": {
            "min": int(year_range[0]) if year_range[0] else 2000,
            "max": int(year_range[1]) if year_range[1] else 2025
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
