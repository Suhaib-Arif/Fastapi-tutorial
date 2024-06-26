from fastapi import FastAPI
import models2
from database2 import engine
from routers import auth, todos, admin, users
from starlette.staticfiles import StaticFiles

app = FastAPI()

models2.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory='static'), name='static')

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
