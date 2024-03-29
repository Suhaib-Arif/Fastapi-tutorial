from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from pydantic import BaseModel
from database2 import SessionsLocal
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from typing import Annotated, Optional
from models2 import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.exc import IntegrityError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None
    
    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get('email')
        self.password = form.get('password')

SECRET_KEY = 'fsbfdbdb44848fbfbfbdgngntd5bfb4fbf54'
ALGORITHM = 'HS256'

templates = Jinja2Templates(directory='templates')



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


@router.get('/', response_class=HTMLResponse)
async def authentication_page(request: Request):
    msg = ''
    return templates.TemplateResponse('login.html', {'request': request, 'msg':msg })


@router.get('/register', response_class=HTMLResponse)
async def authentication_page(request: Request):
    
    return templates.TemplateResponse('register.html', {'request': request})

@router.post('/register', response_class=HTMLResponse)
async def register_user(request: Request, db: db_depencency, email:str = Form(...), username:str=Form(...), 
                        firstname:str = Form(...), lastname:str= Form(...), password:str = Form(...), 
                        password2:str=Form(...)):
    validation1 = db.query(Users).filter(Users.email == email).first()
    
    validation2 = db.query(Users).filter(Users.username == username).first()
    
    if password != password2 or validation1 is not None or validation2 is not None:
        msg = "Invalid registration"
        return templates.TemplateResponse('register.html', {'request': request, 'msg': msg})
    
    model = Users()
    model.username = username
    model.email = email
    model.hashed_password = crypto_context.hash(password)
    model.first_name = firstname
    model.last_name = lastname

    try:
        db.add(model)
    except IntegrityError as e:
        msg = "Invalid registration: " + e
        return templates.TemplateResponse('register.html', {'request': request, 'msg': msg})
    
    db.commit()
    msg = "Registration Successful"
    return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})




    




def create_access_token(usename: str, user_id: int, role: str, time_duration: timedelta):
    encode = {'sub': usename, 'id': user_id, 'role': role}
    exp = datetime.now() + time_duration
    encode.update({'exp': exp})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user_id(request: Request):
    try:

        token = request.cookies.get('access_token')
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id :int = payload.get('id')
        user_role :str = payload.get('role')

        if username is None or user_id is None:
            raise None
        
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could Not Validate Credentials')



def validate_user_data(username, password, db):
    userdata = db.query(Users).filter(Users.username == username).first()
    if not userdata:
        return False
    if not crypto_context.verify(password, userdata.hashed_password):
        return False
    return userdata


@router.post('/validate_user/', response_model=Token)
async def validate_user(response : Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_depencency):
    users = validate_user_data(form_data.username, form_data.password, db)
    if not users:
        return False
    token = create_access_token(users.username, users.id, users.role, timedelta(minutes=60))
    response.set_cookie(key='access_token', value=token, httponly=True)

    return True

@router.get('/logout')
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse('login.html', {'request': request, 'msg': msg})
    response.delete_cookie(key='access_token')
    return response


@router.post('/', response_class=HTMLResponse)
async def login(request: Request, db: db_depencency):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse('/todo', status_code=status.HTTP_302_FOUND)

        validate_user_cookies = await validate_user(response, form_data=form, db =db)
        if not validate_user_cookies:
            msg = "Invalid user data"
            return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})

        return response
    
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})

