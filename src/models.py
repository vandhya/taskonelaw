from datetime import datetime
from pydantic import BaseModel
from database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    full_name = Column(String)
    npm = Column(Integer)
    client_id = Column(String)
    client_secret = Column(String)
    token = relationship("Token", back_populates="owner", uselist=False)

class UserSchema(BaseModel):
    user_id: int
    username: str
    password: str
    full_name: str
    npm: int
    client_id: str
    client_secret:str


    class Config:
        orm_mode = True

class Token(Base):
    __tablename__ = "tokens"

    token_id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, unique=True)
    refresh_token = Column(String, unique=True)
    token_type = Column(String, default="Bearer")
    time_created = Column(TIMESTAMP)
    owner_id = Column(Integer, ForeignKey('users.user_id'))
    owner = relationship("User", back_populates="token")

class TokenSchema(BaseModel):
    token_id: int
    access_token: str
    refresh_token: str
    token_type: str
    time_created: datetime
    owner_id: int


    class Config:
        orm_mode = True