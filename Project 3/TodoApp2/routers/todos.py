from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import Field, BaseModel
from models2 import Todos
from database2 import SessionsLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status 
from .auth import get_current_user_id

router = APIRouter()

def get_db():
    db = SessionsLocal()
    try:
        yield db
    finally:
        db.close()


db_depencency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user_id)]


class TodoModel(BaseModel):
    title : str = Field(min_length=3, max_length=100)
    description : str = Field(min_length=3, max_length=10000)
    priority: int = Field(gt=0) 
    complete :bool

    class Config:
        json_schema_extra = {
            'example' :  {
                "title": "go to the store",
                "priority": 6,
                "description": "get eggs",
                "complete": False
            },
        }




@router.get('/read_todos/', status_code=status.HTTP_200_OK)
async def read_todos(user: user_dependency, db: db_depencency):
    if user is None:
        raise HTTPException(status_code=402, detail="User is Unauthourized")
    
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_depencency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=402, detail="User is Unauthourized")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.id).first()
    

    if todo_model:
        return todo_model
    
    raise HTTPException(status_code=202, detail="The database is empty")

@router.post('/todo/add_todo', status_code=status.HTTP_201_CREATED)
async def add_todo(user: user_dependency, db: db_depencency, TodoData: TodoModel):
    if user is None:
        raise HTTPException(status_code=401 , detail="User has Not been Authourised yet")
    todo_model = Todos(**TodoData.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()

@router.put('/update_todo/{todo_id}', status_code=status.HTTP_202_ACCEPTED)
async def update_entry(user: user_dependency, db: db_depencency, todo_params: TodoModel, todo_id: int = Path(gt=0)):
    my_data = db.query(Todos).filter(Todos.id == todo_id).\
        filter(Todos.owner_id == user.get('id')).first()

    if user is None:
        raise HTTPException(status_code=401 , detail="User has Not been Authourised yet")
    
    if my_data is None:
        raise HTTPException(status_code=404, detail=f"No Data with id: {todo_id, my_data}")
    
    my_data.title = todo_params.title
    my_data.complete = todo_params.complete
    my_data.priority = todo_params.priority
    my_data.description = todo_params.description

    db.commit()


@router.delete('/delete_todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_entry(user: user_dependency, db: db_depencency, todo_id: int = Path(gt=0)):
    
    todo_data = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    
    if todo_data is None:
        raise HTTPException(status_code=404, detail="ID Not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()