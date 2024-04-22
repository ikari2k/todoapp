from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from api.auth import get_current_user
from api.users import change_password, UserVerification
from database import SessionLocal

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
    token = request.cookies.get("access_token")
    if token is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user = await get_current_user(token)

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
    password: str = Form(...),
    password2: str = Form(...),
    db=db_dependency,
):
    token = request.cookies.get("access_token")
    if token is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user = await get_current_user(token)
    user_verification = UserVerification(password=password, new_password=password2)
    await change_password(user, db, user_verification)

    return templates.TemplateResponse(
        "change-user-password.html",
        {"request": request, "user": user, "msg": "Password updated"},
    )
