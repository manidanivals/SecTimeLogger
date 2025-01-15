#Controllers/UserController.py
from sqlalchemy.orm import Session
from Models import User, UserDTO
from Service.Security import get_password_hash, verify_password, create_access_token
from Models.Data import SessionLocal
from fastapi import HTTPException

class UserController:
    def create_user(self, username: str, email: str, password: str, role: str, company: str):
        """
        Create a new user and manage the session internally.
        """
        with SessionLocal() as db:  # Open a new session
            # Check if email or username already exists
            if db.query(User).filter((User.email == email) | (User.username == username)).first():
                raise HTTPException(status_code=400, detail="Email or username already exists")

            # Hash the password
            hashed_password = get_password_hash(password)

            # Create a new user
            new_user = User(username=username, email=email, password=hashed_password, role=role, company=company)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            return new_user

    def authenticate_user(self, email: str, password: str):
        """
        Authenticate a user and manage the session internally.
        """
        with SessionLocal() as db:  # Open a new session
            user = db.query(User).filter(User.email == email).first()
            if not user or not verify_password(password, user.password):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            # Create and return an access token
            access_token = create_access_token({"sub": user.email, "role": user.role, "company": user.company})
            return {"access_token": access_token, "token_type": "bearer"}

    def get_users_by_role(self, role: str, company: str = None):
        """
        Retrieve users based on role and company.
        """
        with SessionLocal() as db:  # Open a new session
            if role == "manager":
                return db.query(User).filter(User.company == company).all()
            elif role == "admin":
                return db.query(User).all()
            else:
                raise HTTPException(status_code=403, detail="Unauthorized access")
