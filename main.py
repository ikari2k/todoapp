from fastapi import FastAPI


import models
from database import engine

from api import (
    auth as auth_api,
    todos as todos_api,
    admin as admin_api,
    users as users_api,
)
from routers import todos as todos_router, auth as auth_router
from starlette.staticfiles import StaticFiles

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


app.include_router(auth_api.router)
app.include_router(auth_router.router)
app.include_router(todos_api.router)
app.include_router(todos_router.router)
app.include_router(admin_api.router)
app.include_router(users_api.router)
