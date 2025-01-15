#Controllers/UserController.py
from Models import User, UserDTO
from Service.Security import get_password_hash, verify_password, create_access_token
from Models.Data import SessionLocal
from fastapi import HTTPException

class UserController:
    def create_user(self, username: str, email: str, password: str, role: str, company: str):
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
    def update_user_by_email(self, email: str, username: str = None, new_email: str = None, password: str = None,
                             role: str = None):
        with SessionLocal() as db:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            if username:
                user.username = username
            # Optionally allow email updates
            if new_email:
                # Check if new_email is already taken
                if db.query(User).filter(User.email == new_email).first():
                    raise HTTPException(status_code=400, detail="Email already in use")
                user.email = new_email
            if password:
                user.password = get_password_hash(password)  # from Security.py
            if role:
                user.role = role

            db.commit()
            db.refresh(user)
            return UserDTO.from_user(user)

    def delete_user(self, user_id: int):
        with SessionLocal() as db:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            db.delete(user)
            db.commit()
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
