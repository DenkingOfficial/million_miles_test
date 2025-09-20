from celery_app import celery_app
from tasks import test_task

def monitor_celery():
    print("Celery Worker Monitor")
    print("=" * 50)
    print("1. Testing Celery connectivity...")
    try:
        result = test_task.delay()
        response = result.get(timeout=10)
        print(f"Test task result: {response}")
    except Exception as e:
        print(f"Test task failed: {e}")
        return
    
    print("\n2. Checking worker status...")
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            print(f"Active workers: {list(stats.keys())}")
            for worker, stat in stats.items():
                print(f"   {worker}: {stat.get('total', 'N/A')} tasks processed")
        else:
            print("No active workers found")
    except Exception as e:
        print(f"Failed to get worker status: {e}")
    
    print("\n3. Checking scheduled tasks...")
    try:
        inspect = celery_app.control.inspect()
        scheduled = inspect.scheduled()
        if scheduled:
            for worker, tasks in scheduled.items():
                print(f"{worker}: {len(tasks)} scheduled tasks")
        else:
            print("No scheduled tasks")
    except Exception as e:
        print(f"Failed to get scheduled tasks: {e}")

if __name__ == "__main__":
    monitor_celery()
