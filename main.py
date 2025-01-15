# main.py
import redis
from fastapi import FastAPI, HTTPException, Depends
from jose import jwt
from pydantic import BaseModel
from Controllers.TimesheetController import TimesheetController
from Helper.GetRole import admin_required, get_current_token, get_current_user_role, get_current_user_company
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from Controllers.UserController import UserController
from Models import UserDTO, User
from Models.Data import SessionLocal
from Service.Logging import logger
from datetime import date
from Service.Security import SECRET_KEY, ALGORITHM

app = FastAPI()
user_controller = UserController()
timesheet_controller = TimesheetController()


# Pydantic Models for Request Validation
class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str

class TimeLogCreateRequest(BaseModel):
    date: date
    hours: float
    description: str = None

class UserUpdateRequest(BaseModel):
    username: str = None
    email: str = None
    password: str = None
    role: str = None
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
logger = logger.getLogger("myapp")
def get_current_user(token: str = Depends(get_current_token)):
    """
    Returns the user object from the database corresponding to the JWT.
    Raises HTTP 401 if invalid or user not found.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        with SessionLocal() as db:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
@app.setup("startup")
async def startup():
    # Replace aioredis usage with redis.asyncio
    redis_client = redis.Redis(host="localhost", port=6379, db=0)
    await FastAPILimiter.init(redis_client)
@app.get("/", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def read_root():
    logger.info("Root endpoint accessed.")
    return {"message": "Hello World"}
@app.post("/login", response_model=TokenResponse, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def login(request: LoginRequest):
    """
    Authenticates the user, returning a JWT if successful.
    """
    token_data = user_controller.authenticate_user(
        email=request.email,
        password=request.password
    )
    return TokenResponse(**token_data)
@app.post("/users", response_model=dict, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def create_user(request: UserCreateRequest, token: str = Depends(admin_required)):
    """
    Route to create a new user (Admin-only).
    """
    user_dto = user_controller.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
        role=request.role,
        company=request.company
    )
    return user_dto.__dict__

@app.get("/users/{user_id}", response_model=dict, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def get_user(user_id: int):
    """
    Route to retrieve a user by ID.
    """
    user_dto = user_controller.get_user(user_id=user_id)
    return user_dto.__dict__


@app.put("/users/{user_id}", response_model=dict, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def update_user(user_id: int, request: UserUpdateRequest):
    """
    Route to update an existing user.
    """
    user_dto = user_controller.update_user(
        user_id=user_id,
        username=request.username,
        email=request.email,
        password=request.password,

    )
    return user_dto.__dict__
@app.get("/users", response_model=list, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def get_users(
    role: str = Depends(user_controller.get_current_user_role),
    company: str = Depends(user_controller.get_current_user_company),
):
    """
    Get all users, restricted by role and company.
    """
    users = user_controller.get_users_by_role(role=role, company=company)
    return [UserDTO.from_user(user) for user in users]

@app.post("/time-logs", response_model=dict, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def log_time_entry(
    request: TimeLogCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Any valid user can log their own time.
    """
    timesheet_dto = timesheet_controller.create_timesheet(
        user_id=current_user.user_id,
        date=request.date,
        hours=request.hours,
        description=request.description,
    )
    return timesheet_dto.__dict__


@app.get("/time-logs/me", response_model=list, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def get_my_time_logs(
    current_user: User = Depends(get_current_user)
):
    """
    Return all time logs for the currently authenticated user.
    """
    logs = timesheet_controller.get_timesheets_for_user(current_user.user_id)
    return [log.__dict__ for log in logs]


@app.get("/time-logs/company", response_model=list, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def get_company_time_logs(
    role: str = Depends(get_current_user_role),
    company: str = Depends(get_current_user_company)
):
    """
    Manager: see logs for their company.
    Admin: see logs for all companies or whichever logic you prefer.
    Normal user: not allowed.
    """
    if role == "manager":
        # Return logs for manager's company
        return [log.__dict__ for log in timesheet_controller.get_timesheets_for_company(company)]
    elif role == "admin":
        # Admin can see logs for ANY company; you may want a param or show them all
        # For simplicity, let's show everything:
        from Models.Data import SessionLocal
        from Models.Timesheet import Timesheet
        with SessionLocal() as db:
            all_logs = db.query(Timesheet).all()
        return [TimesheetController().get_timesheets_for_user(log.user_id)[0].__dict__ for log in all_logs]
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view company logs")


@app.get("/time-logs/company/total", response_model=dict, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def get_company_total_time(
    role: str = Depends(get_current_user_role),
    company: str = Depends(get_current_user_company)
):
    """
    Manager: total hours for their company.
    Admin: total hours for all companies (or whichever logic you want).
    """
    if role == "manager":
        total = timesheet_controller.get_total_hours_for_company(company)
        return {"company": company, "total_hours": total}
    elif role == "admin":
        total = timesheet_controller.get_total_hours_for_all()
        return {"company": "All Companies", "total_hours": total}
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view total hours")