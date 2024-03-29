from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import Field, BaseModel
from models2 import Users
from database2 import SessionsLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status 
from .auth import get_current_user_id
from passlib.context import CryptContext

router = APIRouter(
    prefix='/users',
    tags=['users']
)

class UserVerifications(BaseModel):
    old_password: str
    new_password: str = Field(min_length=3)

    class Config:
        json_schema_extra = {
            'example': {
                'old_password': 'oldjames',
                'new_password': 'newjames'
            }
        }

class PhoneNumber(BaseModel):
    # user_id: int = Field(gt=0)
    phone_number: int

    class Config:
        json_schema_extra = {
            'example': {
                'phone_number': '9xxxxxxxxx'
            }
        }


def get_db():
    db = SessionsLocal()
    try:
        yield db
    finally:
        db.close()


db_depencency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user_id)]
crypto_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.get('/get_user')
async def get_user_data(user: user_dependency, db: db_depencency):
    if user is None:
        raise HTTPException(status_code=402, detail="Unauthourized")
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put('/change_password/')
async def change_user_password(user: user_dependency, db: db_depencency, new_data: UserVerifications):
    if user is None:
        raise HTTPException(status_code=402, detail="Unauthourized")
    
    user_data = db.query(Users).filter(Users.id == user.get('id')).first()
    
    if not crypto_context.verify(new_data.old_password, user_data.hashed_password):
        raise HTTPException(status_code=402, detail="Unauthourized")
    
    user_data.hashed_password = crypto_context.hash(new_data.new_password)
    db.add(user_data)
    db.commit()

@router.put('/update_phone_number/')
async def update_number(user: user_dependency, db: db_depencency, user_data: PhoneNumber):
    if user is None:
        raise HTTPException(status_code=402, detail="Unauthourized")
    
    user_row = db.query(Users).filter(Users.id == user.get('id')).first()
    user_row.phone_number = user_data.phone_number
    
    db.add(user_row)
    
    db.commit()


    

