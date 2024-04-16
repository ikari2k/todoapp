from typing import Annotated

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from api.todos import (
    read_by_user,
    create_todo_as_admin,
    TodoRequest,
    read_todo_as_admin,
    update_todo_as_admin,
)
from sqlalchemy.orm import Session

from database import SessionLocal

from starlette import status
from starlette.responses import RedirectResponse

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
    todo_model = await read_by_user(db)
    return templates.TemplateResponse(
        "home.html", {"request": request, "todos": todo_model}
    )


@router.get("/todos/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})


@router.post("/todos/add-todo", response_class=HTMLResponse)
async def create_todo(
    db: db_dependency,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
):
    todo_request = TodoRequest(
        title=title, description=description, priority=priority, complete=False
    )
    await create_todo_as_admin(db, todo_request)
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/todos/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: db_dependency):

    todo_model = await read_todo_as_admin(db, todo_id)

    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": todo_model}
    )


@router.post("/todos/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(
    db: db_dependency,
    todo_id: int,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
):
    todo_request = TodoRequest(
        title=title, description=description, priority=priority, complete=False
    )
    await update_todo_as_admin(db, todo_request, todo_id)
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
