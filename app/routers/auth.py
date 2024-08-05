from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from db import database
from models import User, Token, TokenData
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import secrets
from datetime import datetime, timedelta
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

"""
This module contains the authentication routes for the FastAPI application.
Functions:
- login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_session)): 
	Handles the login functionality. Verifies the user's credentials and returns an access token.
- get_user(db: Session, username: str): 
	Retrieves a user from the database based on the provided username.
- get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_session)): 
	Retrieves the current user based on the provided access token.
- create_access_token(data: dict, expires_delta: timedelta = None): 
	Creates an access token with the provided data and expiration time.
"""


# Login route
@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_session)):
	"""
	Endpoint for user authentication and login.

	Parameters:
	- form_data (OAuth2PasswordRequestForm): The form data containing the username and password for login.
	- db (Session): The database session.

	Returns:
	- Token: The access token and token type.

	Raises:
	- HTTPException: If the username or password is incorrect or if an error occurs during login.
	"""
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
	"""
	Retrieve a user from the database by their username.

	Args:
		db (Session): The database session.
		username (str): The username of the user to retrieve.

	Returns:
		User: The user object if found, None otherwise.

	Raises:
		HTTPException: If an error occurs while retrieving the user.
	"""
	try:
		return db.query(User).filter(User.username == username).first()
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="An error occurred while retrieving the user",
			headers={"WWW-Authenticate": "Bearer"},
		)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_session)):
	"""
	Get the current user based on the provided token.

	Parameters:
	- token (str): The authentication token.
	- db (Session): The database session.

	Returns:
	- user: The current user.

	Raises:
	- HTTPException: If the credentials cannot be validated.
	"""
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
	"""
	Generates an access token using the provided data and expiration delta.

	Parameters:
		data (dict): The data to be encoded in the access token.
		expires_delta (timedelta, optional): The expiration delta for the access token. If not provided, a default expiration of 15 minutes will be used.

	Returns:
		str: The generated access token.

	"""
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.now() + expires_delta
	else:
		expire = datetime.now() + timedelta(minutes=15)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt