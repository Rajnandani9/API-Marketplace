<<<<<<< HEAD
import os
=======
db.py

>>>>>>> 68175c670b8e573bfef8f6f0beca6246581e9c68
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

<<<<<<< HEAD
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./marketplace.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
=======
DATABASE_URL = "sqlite:///./marketplace.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
>>>>>>> 68175c670b8e573bfef8f6f0beca6246581e9c68

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()