import re
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, JSON
from sqlalchemy import Integer
from typing import List, Optional
from enum import Enum
import bcrypt

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class UserBase(SQLModel):
    username: Optional[str] = None
    password: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    city: str
    gender: GenderEnum
    age: Optional[int] = None
    full_name: Optional[str] = None
    interests: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))    

    def set_password(self, password: str) -> None:
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def verify_valid_email(self) -> bool:
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_pattern, self.email) is not None
    
    def set_full_name(self) -> None:
        self.full_name = f"{self.first_name} {self.last_name}"

    def set_user_name(self) -> None:
        self.username = f"{self.email}"

    def set_interests(self, interests: List[str]) -> None:
        self.interests = interests

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True, autoincrement=True))


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None