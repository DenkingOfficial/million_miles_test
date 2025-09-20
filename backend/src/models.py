from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSON
import datetime
from .database import Base

class Car(Base):
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True, index=True)
    encar_id = Column(String, index=True)
    manufacturer = Column(String)
    model = Column(String)
    badge = Column(String)
    badge_detail = Column(String)
    transmission = Column(String)
    fuel_type = Column(String)
    year = Column(Float)
    form_year = Column(String)
    mileage = Column(Float)
    price = Column(Float)
    separation = Column(JSON)
    trust = Column(JSON)
    service_mark = Column(JSON)
    condition = Column(JSON)
    photo = Column(String)
    photos = Column(JSON)
    service_copy_car = Column(String)
    sales_status = Column(String)
    sell_type = Column(String)
    buy_type = Column(JSON)
    powerpack = Column(String)
    ad_words = Column(String)
    hotmark = Column(String)
    office_city_state = Column(String)
    office_name = Column(String)
    dealer_name = Column(String)
    modified_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    last_seen_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
