# Helper/GetRole.py
from fastapi import Depends, HTTPException
from jose import jwt
from Service.Security import SECRET_KEY, ALGORITHM
from fastapi import Header, HTTPException, Depends

def get_current_token(authorization: str = Header(None)):
    """
    Extracts the JWT token from the Authorization header.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    # Expect the header to look like: "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    return parts[1]


def get_current_user_role(token: str = Depends(get_current_token)):
    """
    Decode the JWT and extract the user's role.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("role")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_company(token: str = Depends(get_current_token)):
    """
    Decode the JWT and extract the user's company.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("company")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def admin_required(token: str = Depends(get_current_token)):
    """
    Check if the user has the admin role.
    Raise an HTTPException if not.
    """
    role = get_current_user_role(token)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges are required.")