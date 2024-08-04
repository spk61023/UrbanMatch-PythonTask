from datetime import datetime
import re
from typing import List, Optional
import bcrypt
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import overlap
from db import database
from models import GenderEnum, User, UserBase
from routers.auth import get_current_user
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from models import GenderEnum

router = APIRouter()

# schemas.py


class UserCreate(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    password: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    city: str
    gender: GenderEnum
    age: int
    interests: List[str]

    def verify_valid_email(self) -> bool:
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_pattern, self.email) is not None


@router.post("/users/", response_model=UserBase)
async def create_user(user: UserCreate, session: Session = Depends(database.get_session)):
    existing_user = session.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        if not user.verify_valid_email():
            raise HTTPException(status_code=400, detail="Invalid email address")
        
        # Create user instance
        db_user = User(
            username=user.email,
            password=bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone_number=user.phone_number,
            city=user.city,
            gender=user.gender,
            age=user.age,
            full_name=f"{user.first_name} {user.last_name}",
            interests=user.interests
        )
        
        # Add to the session and commit
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        
        return db_user
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(database.get_session)):
	user = db.query(User).filter(User.id == user_id).first()
	return {"user": user}

# get all users
@router.get("/users")
def get_all_users(db: Session = Depends(database.get_session)):
    users = db.query(User).all()
    return {"users": users}

# view user from loggedin user
# @router.get("/users")
async def get_my_profile(db: Session = Depends(database.get_session), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    user = db.query(User).filter(User.id == user_id).first()   
    return {
        "user": user
    }
	
# delete all users
# @router.delete("/users")
# def delete_users(db: Session = Depends(database.get_session)):
# 	users = db.query(User).all()
# 	for user in users:
# 		db.delete(user)
# 	db.commit()
# 	return {"message": "All users deleted"}

# delete user by id
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_session)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return JSONResponse(content={"message": "User deleted"}, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
# Let's create a matchmaking algorithm that will return a list of users who's interests match the current user's interests
@router.get("/matchmaking")
async def matchmaking(current_user: User = Depends(get_current_user), db: Session = Depends(database.get_session)):
    try:
        user_id = current_user.id
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Subquery to find users with at least one matching interest
        common_interest_users = db.query(User).filter(
            User.id != user_id,
            User.interests.overlap(user.interests)
        ).all()
        
        return {
            "users": common_interest_users
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))