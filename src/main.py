from datetime import datetime, timedelta
from secrets import token_hex
from typing import List
from fastapi import FastAPI, Form, Depends, HTTPException, Request, Response, status
import crud
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def root():
    return {'Name': 'Arllivandhya Dani','NPM':'1906398521'}


@app.post('/oauth/token')
def request_token(
        response:Response,
        username: str = Form(...),
        password: str = Form(...),
        token_type: str = Form(...),
        client_id: str = Form(...),
        client_secret: str = Form(...),
        db: Session = Depends(get_db)):

    user = crud.get_user_by_username(db=db,username=username)
    if user and user.password == password and user.client_id == client_id and user.client_secret == client_secret:
        access_token = token_hex(40)
        refresh_token = token_hex(40)
        time_created = datetime.now()
        expires_in = timedelta(minutes=5).seconds
        crud.create_token(db=db,access_token=access_token, refresh_token=refresh_token, owner=user, time_created=time_created)
        return {'access_token':access_token,'expires_in':expires_in,'token_type':token_type,'scope':'null','refresh_token':refresh_token}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {'error':'invalid request','error_description':'ada kesalahan masbro!'}

@app.post('/oauth/resource')
def oauth_resource(response:Response, request:Request, db: Session = Depends(get_db)):
    authorization = request.headers.get('Authorization')
    if authorization:
        token_type, access_token = authorization.split(' ')
    token = crud.get_token_by_access_token(db=db,access_token=access_token)
    if token:
        user = token.owner

    if token_type != "Bearer" or access_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'error':'unauthorized','error_description':'anda butuh bearer token masbro'}
    if token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'error':'unauthorized','error_description':'Token Salah masbro'}
    
    expires = (datetime.now() - token.time_created).total_seconds()
    if expires > 300:
        crud.delete_token(db=db,access_token=access_token)
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'error':'unauthorized','error_description':'masa berlaku token habis masbro'}
    return {'access_token':access_token,'client_id':user.client_id,'user_id':user.username,'full_name':user.full_name,'npm':user.npm,'expires':expires, 'refresh_token':token.refresh_token}


@app.post("/users/", response_model=models.UserSchema)
def register(user: models.UserSchema, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=user.username)
    if user:
        raise HTTPException(
            status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[models.UserSchema])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/tokens/", response_model=List[models.TokenSchema])
def get_tokens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tokens = crud.get_tokens(db, skip=skip, limit=limit)
    return tokens