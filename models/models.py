<<<<<<< HEAD
=======
models.py

>>>>>>> 68175c670b8e573bfef8f6f0beca6246581e9c68
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")  # user ya developer
    created_at = Column(DateTime, default=datetime.utcnow)
    apis = relationship("API", back_populates="developer")
    subscriptions = relationship("Subscription", back_populates="user")

class API(Base):
    __tablename__ = "apis"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    base_url = Column(String, nullable=False)
    price_monthly = Column(Float, default=0.0)
    developer_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    developer = relationship("User", back_populates="apis")
    subscriptions = relationship("Subscription", back_populates="api")
    usage_logs = relationship("UsageLog", back_populates="api")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    api_id = Column(Integer, ForeignKey("apis.id"))
    api_key = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="subscriptions")
    api = relationship("API", back_populates="subscriptions")

class UsageLog(Base):
    __tablename__ = "usage_logs"
    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("apis.id"))
    api_key = Column(String)
    endpoint = Column(String)
    status_code = Column(Integer)
    response_time = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    api = relationship("API", back_populates="usage_logs")