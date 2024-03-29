from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import Field, BaseModel
from models2 import Todos
from database2 import SessionsLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status 
from .auth import get_current_user_id

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db = SessionsLocal()
    try:
        yield db
    finally:
        db.close()


db_depencency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user_id)]

@router.get('/read_all', status_code=status.HTTP_200_OK)
async def show_all(user: user_dependency, db: db_depencency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=402, detail="User is Not Authourized")
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_depencency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()

    db.commit()
