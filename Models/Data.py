# Models/Data.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from Models.Data import Base, engine
from Models.Timesheet import Timesheet

# SQLite database URL
DATABASE_URL = "sqlite:///./time_logging.db"

# SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is the database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

Base.metadata.create_all(bind=engine)