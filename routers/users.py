from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from api.users import change_password, UserVerification
from database import SessionLocal
from routers.auth_utils import get_user_model_based_on_request

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"description": "Not Found"}}
)

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/change-password", response_class=HTMLResponse)
async def edit_user_view(request: Request):
    user = await get_user_model_based_on_request(request)

    return templates.TemplateResponse(
        "change-user-password.html",
        {
            "request": request,
            "user": user,
        },
    )


@router.post("/change-password", response_class=HTMLResponse)
async def user_password_change(
    request: Request,
    db: db_dependency,
    password: str = Form(...),
    password2: str = Form(...),
):
    user = await get_user_model_based_on_request(request)
    user_verification = UserVerification(password=password, new_password=password2)
    await change_password(user, db, user_verification)

    return templates.TemplateResponse(
        "change-user-password.html",
        {"request": request, "user": user, "msg": "Password updated"},
    )
