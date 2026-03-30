from sqlmodel import SQLModel, Field
from typing import Optional

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    price: float
    published_year: int

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    role: str = "user"  

class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "user"
