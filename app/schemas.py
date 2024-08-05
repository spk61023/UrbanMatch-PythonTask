import re
from typing import List, Optional
from pydantic import BaseModel

from models import GenderEnum


# Create User
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


# Update User
class UserUpdate(BaseModel):
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    interests: Optional[List[str]] = None
