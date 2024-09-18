from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

from .. import schemas
from .. import database, utils, oauth2
from ..models import *
from datetime import datetime, timedelta

from ..config import settings

ACCESS_TOKEN_EXPIRE_TIME = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

def create_user(user_credentials: schemas.UserCreate, db: Session = Depends(database.get_db)):
    
    hashed_password = utils.hash(user_credentials.password)
    
    user = db.query(User).filter(User.username == user_credentials.username).first()
    
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already exist")
        
    email = db.query(User).filter(User.email == user_credentials.email).first()
    
    if email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already exist")
        
    new_user = User(username=user_credentials.username, email=user_credentials.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    
    user = db.query(User).filter(User.username == user_credentials.username).first()
    
    if not user or not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"invalid credentials")

        
    access_token, access_token_expires_at = oauth2.create_access_token(data={"user_id": user.id})
    
    refresh_token, refresh_token_expires_at = oauth2.create_refresh_token(data={"user_id": user.id})
    
    token = Token(token= refresh_token,
                  user_id = user.id,
                  expires_at = refresh_token_expires_at,
                  created_at=datetime.utcnow()
                  )
    
    db.add(token)
    db.commit()
    db.refresh(token)
    
    return {"access_token": access_token,
            "access_token_expires_at": access_token_expires_at,
            "refresh_token": refresh_token,
            "refresh_token_expires_at": refresh_token_expires_at,
            "token_type": "bearer"}
    

def verify_user_token(token: str, db: Session):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is required"
        )
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token_data = oauth2.verify_access_token(token, credentials_exception)
    except JWTError:
        raise credentials_exception
    
    stored_token = db.query(Token).filter(Token.token == token).first()
    
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == token_data['id']).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return {
        "user_id": user.id,
        "username": user.username
    }
    

def perform_logout(authorization: str, db: Session):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required"
        )
        
    token = authorization(" ")[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is required"
        )
    
    try:
        token_data = oauth2.verify_access_token(token, credentials_exception=None)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
        
    stored_token = db.query(Token).filter(Token.token == token).first()
    
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
        
    db.delete(stored_token)
    db.commit()
    
    return {
        "detail": "Successfully logged out"
    }