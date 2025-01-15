#Models/User.py
from sqlalchemy import Column, Integer, String, ForeignKey
from Models.Data import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")  # "user", "manager", "admin"
    company = Column(String, nullable=True)  # Company name or ID
