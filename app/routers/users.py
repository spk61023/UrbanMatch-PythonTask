import bcrypt
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import database
from models import User, UserBase
from routers.auth import get_current_user
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from schemas import UserCreate, UserUpdate

router = APIRouter()


# create user
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

# get user by id
@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(database.get_session)):
	user = db.query(User).filter(User.id == user_id).first()
	return {"user": user}

# get all users
@router.get("/users")
def get_all_users(db: Session = Depends(database.get_session)):
    users = db.query(User).all()
    return {"users": users}

# update user by id
@router.put("/users/{user_id}")
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(database.get_session), current_user: User = Depends(get_current_user)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user_update.password:
            user.password = bcrypt.hashpw(user_update.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        if user_update.first_name:
            user.first_name = user_update.first_name
        if user_update.last_name:
            user.last_name = user_update.last_name
        if user_update.phone_number:
            user.phone_number = user_update.phone_number
        if user_update.city:
            user.city = user_update.city
        if user_update.gender:
            user.gender = user_update.gender
        if user_update.age:
            user.age = user_update.age
        if user_update.interests:
                if user.interests is None:
                    user.interests = []
                user.interests = list(set(user.interests).union(set(user_update.interests)))      
        db.commit()
        db.refresh(user)
        
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
	
# delete all users
@router.delete("/users")
def delete_users(db: Session = Depends(database.get_session)):
	users = db.query(User).all()
	for user in users:
		db.delete(user)
	db.commit()
	return {"message": "All users deleted"}

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
    
# matchmaking api that will return a list of users who's interests match the current user's interests
@router.get("/matchmaking")
async def matchmaking(current_user: User = Depends(get_current_user), db: Session = Depends(database.get_session)):
    """
    Matchmaking function that retrieves a list of users who have common interests with the current user.
    Parameters:
    - current_user (User): The current user object.
    - db (Session): The database session object.
    Returns:
    - dict: A dictionary containing a list of users who have common interests with the current user.
    Raises:
    - HTTPException: If the current user is not found or if there is an internal server error.
    """
    try:
        user_id = current_user.id
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_interests = set(user.interests)
        matches = []

        all_users = db.query(User).filter(User.id != user_id).all()
        for other_user in all_users:
            other_interests = set(other_user.interests)
            common_interests = user_interests & other_interests
            if common_interests:
                matches.append(other_user)
        
        # if there's no matches for the user
        if not matches:
            return {
                    "message": "No matches found for the user"
                }
        return {
            "users": matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))