from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Session

import models


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: models.UserSchema):
    db_user = models.User(
        username=user.username, 
        password=user.password,
        full_name=user.full_name,
        npm=user.npm,
        client_id=user.client_id,
        client_secret=user.client_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_token(db: Session, access_token: str, refresh_token: str , owner: models.User, time_created: TIMESTAMP):
    db_token = models.Token(
        access_token=access_token,
        refresh_token=refresh_token,
        owner = owner,
        owner_id=owner.user_id,
        time_created=time_created
    )
    db.query(models.Token).filter(models.Token.owner_id == owner.user_id).delete()
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def update_token(db:Session, token_id: int):
    db.query(models.Token).filter(models.Token.token_id == token_id).update()
    return None

def get_tokens(db: Session, skip: int = 0, limit: int = 100):
    db.query(models.Token).filter(models.Token.owner_id == None).delete()
    return db.query(models.Token).offset(skip).limit(limit).all()

def get_token_by_access_token(db: Session, access_token:str):
    return db.query(models.Token).filter(models.Token.access_token==access_token).first()

def delete_token(db: Session, access_token:str):
    return db.query(models.Token).filter(models.Token.access_token==access_token).delete()