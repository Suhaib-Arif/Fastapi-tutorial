from fastapi import APIRouter, Depends, HTTPException, Path, Request, Form
from pydantic import Field, BaseModel
from models2 import Todos, Users
from database2 import SessionsLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse 
from .auth import get_current_user_id

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix='/todo',
    tags=['todo']
)

templates = Jinja2Templates(directory='templates')

def get_db():
    db = SessionsLocal()
    try:
        yield db
    finally:
        db.close()


db_depencency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user_id)]

@router.get('/', response_class=HTMLResponse)
async def read_all_todo(request: Request, db : db_depencency):
    user = get_current_user_id(request)

    if user is None:
        return RedirectResponse('/auth', status_code=status.HTTP_302_FOUND)

    todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
    return templates.TemplateResponse('home.html', {'request': request, 'user': user, 'todos': todos})


@router.get('/add-todo', response_class=HTMLResponse)
async def add_todo(request: Request):

    user = get_current_user_id(request)

    if user is None:
        return RedirectResponse('/auth', status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse('add-todo.html', {'request': request, 'user': user})


@router.post('/add-todo', response_class=HTMLResponse)
async def create_todo(request: Request,db: db_depencency, title: str =  Form(...)
                      , description: str = Form(...), priority: int = Form(...)):
    
    user = get_current_user_id(request)

    if user is None:
        return RedirectResponse('/auth', status_code=status.HTTP_302_FOUND)

    todos = Todos()
    todos.title = title
    todos.description = description
    todos.priority = priority
    todos.owner_id = user.get('id')
    todos.complete = False

    db.add(todos)
    db.commit()
    return RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)



@router.get('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: db_depencency):
    
    user = get_current_user_id(request)

    if user is None:
        return RedirectResponse('/auth', status_code=status.HTTP_302_FOUND)
    
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    return templates.TemplateResponse('edit-todo.html', {'request': request, 'user': user, "todo": todo})



@router.post('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int, db: db_depencency, title: str =  Form(...), 
                           description: str = Form(...), priority: int = Form(...)):
    
    user = get_current_user_id(request)

    if user is None:
        return RedirectResponse('/auth', status_code=status.HTTP_302_FOUND)

    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    todo.title = title
    todo.description = description
    todo.priority = priority

    db.add(todo)
    db.commit()

    return RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)


@router.get('/delete/{todo_id}')
async def delete_todo(request: Request, db: db_depencency, todo_id: int):

    user = get_current_user_id(request)

    if user is None:
        return RedirectResponse('/auth', status_code=status.HTTP_302_FOUND)


    todo_data = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()

    if todo_data is None:
        return RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
    return RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)



@router.get('/complete/{todo_id}', response_class=HTMLResponse)
async def complete_task(request: Request, db: db_depencency, todo_id: int):

    user = get_current_user_id(request)

    if user is None:
        return RedirectResponse('/auth', status_code=status.HTTP_302_FOUND)

    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    todo.complete = not todo.complete

    db.add(todo)
    db.commit()

    return RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)