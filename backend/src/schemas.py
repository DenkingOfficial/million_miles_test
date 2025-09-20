from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class CarBase(BaseModel):
    encar_id: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    badge: Optional[str] = None
    badge_detail: Optional[str] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    year: Optional[float] = None
    form_year: Optional[str] = None
    mileage: Optional[float] = None
    price: Optional[float] = None
    separation: Optional[List[str]] = None
    trust: Optional[List[str]] = None
    service_mark: Optional[List[str]] = None
    condition: Optional[List[str]] = None
    photo: Optional[str] = None
    photos: Optional[List[Any]] = None
    service_copy_car: Optional[str] = None
    sales_status: Optional[str] = None
    sell_type: Optional[str] = None
    buy_type: Optional[List[str]] = None
    powerpack: Optional[str] = None
    ad_words: Optional[str] = None
    hotmark: Optional[str] = None
    office_city_state: Optional[str] = None
    office_name: Optional[str] = None
    dealer_name: Optional[str] = None
    modified_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    is_active: Optional[bool] = True

class Car(CarBase):
    id: int
    
    class Config:
        from_attributes = True

class CarSummary(BaseModel):
    id: int
    encar_id: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    badge: Optional[str] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    year: Optional[float] = None
    mileage: Optional[float] = None
    price: Optional[float] = None
    photo: Optional[str] = None
    office_city_state: Optional[str] = None
    dealer_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class CarFilters(BaseModel):
    manufacturer: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_year: Optional[float] = None
    max_year: Optional[float] = None
    office_city_state: Optional[str] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0
