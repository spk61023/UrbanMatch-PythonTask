from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from db import database
from models import User, Token, TokenData
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import secrets
from datetime import datetime, timedelta

router = APIRouter()
db = database.init_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"

@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_session)):
	try:
		user = db.query(User).filter(User.username == form_data.username).first()
		if not user or not user.verify_password(form_data.password):
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Incorrect username or password",
				headers={"WWW-Authenticate": "Bearer"},
			)
		access_token_expires = timedelta(minutes=30)
		access_token = create_access_token(
			data={"sub": user.username}, expires_delta=access_token_expires
		)
		return {"access_token": access_token, "token_type": "bearer"}
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail= f"An error occurred during login, {e}",
			headers={"WWW-Authenticate": "Bearer"},
		)
    
def get_user(db: Session, username: str):
	try:
		return db.query(User).filter(User.username == username).first()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="An error occurred while retrieving the user",
			headers={"WWW-Authenticate": "Bearer"},
		)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt