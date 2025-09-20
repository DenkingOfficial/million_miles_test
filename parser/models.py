from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Boolean,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True)
    encar_id = Column(String(50), unique=True, nullable=False, index=True)
    manufacturer = Column(String(100), index=True)
    model = Column(String(200), index=True)
    badge = Column(String(200))
    badge_detail = Column(String(200))
    transmission = Column(String(50))
    fuel_type = Column(String(100))
    year = Column(Float)
    form_year = Column(String(10))
    mileage = Column(Float, index=True)
    price = Column(Float, index=True)
    separation = Column(JSON)
    trust = Column(JSON)
    service_mark = Column(JSON)
    condition = Column(JSON)
    photo = Column(String(500))
    photos = Column(JSON)
    service_copy_car = Column(String(50))
    sales_status = Column(String(50))
    sell_type = Column(String(50))
    buy_type = Column(JSON)
    powerpack = Column(Text)
    ad_words = Column(Text)
    hotmark = Column(String(100))
    office_city_state = Column(String(100), index=True)
    office_name = Column(String(200))
    dealer_name = Column(String(100))
    modified_date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_seen_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True, index=True)


class ParseSession(Base):
    __tablename__ = "parse_sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    status = Column(String(50), default="running")
    total_cars_found = Column(Integer, default=0)
    new_cars_added = Column(Integer, default=0)
    cars_updated = Column(Integer, default=0)
    cars_removed = Column(Integer, default=0)
    error_message = Column(Text)
