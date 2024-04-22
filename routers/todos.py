from typing import Annotated

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from api.todos import (
    TodoRequest,
    read_all,
    read_todo,
    create_todo,
    update_todo,
    delete_todo,
    complete_todo,
)
from database import SessionLocal
from routers.auth_utils import get_user_model_based_on_request

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
    user = await get_user_model_based_on_request(request)

    todo_model = await read_all(user, db)

    return templates.TemplateResponse(
        "home.html", {"request": request, "todos": todo_model, "user": user}
    )


@router.get("/todos/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_user_model_based_on_request(request)

    return templates.TemplateResponse(
        "add-todo.html", {"request": request, "user": user}
    )


@router.post("/todos/add-todo", response_class=HTMLResponse)
async def create_todo_by_user(
    request: Request,
    db: db_dependency,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
):
    user = await get_user_model_based_on_request(request)

    todo_request = TodoRequest(
        title=title, description=description, priority=priority, complete=False
    )
    await create_todo(user, db, todo_request)
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/todos/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_as_user(request: Request, todo_id: int, db: db_dependency):
    user = await get_user_model_based_on_request(request)

    todo_model = await read_todo(user, db, todo_id)

    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": todo_model, "user": user}
    )


@router.post("/todos/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_as_user_and_commit(
    request: Request,
    db: db_dependency,
    todo_id: int,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
):
    user = await get_user_model_based_on_request(request)

    todo_request = TodoRequest(
        title=title, description=description, priority=priority, complete=False
    )
    await update_todo(user, db, todo_request, todo_id)
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/todos/delete/{todo_id}", response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int, db: db_dependency):
    user = await get_user_model_based_on_request(request)

    todo_model = await read_todo(user, db, todo_id)

    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    await delete_todo(user, db, todo_id)

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/todos/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo_as_user(request: Request, todo_id: int, db: db_dependency):
    user = await get_user_model_based_on_request(request)

    await complete_todo(user, db, todo_id)

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
