from typing import Annotated

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import models
from api.todos import read_by_user
from sqlalchemy.orm import Session

from database import SessionLocal
import logging as logger


router = APIRouter()

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/todos", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: db_dependency):
    todos = await read_by_user(db)
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})


@router.get("/todos/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    #
    return templates.TemplateResponse("add-todo.html", {"request": request})


@router.get("/todos/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int):
    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo_id": todo_id}
    )
