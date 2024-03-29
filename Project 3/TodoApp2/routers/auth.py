from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database2 import SessionsLocal
from sqlalchemy.orm import Session
from starlette import status 
from typing import Annotated
from models2 import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = 'fsbfdbdb44848fbfbfbdgngntd5bfb4fbf54'
ALGORITHM = 'HS256'


crypto_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2bearer = OAuth2PasswordBearer(tokenUrl='auth/validate_user')

class UsersModel(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionsLocal()
    try:
        yield db
    finally:
        db.close()


db_depencency = Annotated[Session, Depends(get_db)]



@router.post('/add_user', status_code=status.HTTP_201_CREATED)
async def add_user_data(db: db_depencency, users_request: UsersModel):
    user_data = Users(
        email=users_request.email,
        username=users_request.username,
        first_name=users_request.first_name,
        last_name = users_request.last_name,
        hashed_password = crypto_context.hash(users_request.password),
        role = users_request.role,
        is_active = True
    )

    db.add(user_data)
    db.commit()

def create_access_token(usename: str, user_id: int, role: str, time_duration: timedelta):
    encode = {'sub': usename, 'id': user_id, 'role': role}
    exp = datetime.now() + time_duration
    encode.update({'exp': exp})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def validate_user_data(username, password, db):
    userdata = db.query(Users).filter(Users.username == username).first()
    if not userdata:
        return False
    if not crypto_context.verify(password, userdata.hashed_password):
        return False
    return userdata

def get_current_user_id(token: Annotated[str, Depends(oauth2bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id :int = payload.get('id')
        user_role :str = payload.get('role')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could Not Validate Credentials')
        
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could Not Validate Credentials')




@router.post('/validate_user/', response_model=Token)
async def validate_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_depencency):
    users = validate_user_data(form_data.username, form_data.password, db)
    if not users:
        return 'Failed Authourization'
    token = create_access_token(users.username, users.id, users.role, timedelta(minutes=10))
    return {'access_token': token, 'token_type': 'bearer'}