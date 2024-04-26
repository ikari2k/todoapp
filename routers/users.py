from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from api.users import change_password, UserVerification
from app.db.database import get_db
from routers.auth_utils import get_user_model_based_on_token

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"description": "Not Found"}}
)

templates = Jinja2Templates(directory="templates")

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/change-password", response_class=HTMLResponse)
async def edit_user_view(request: Request):
    token = request.cookies.get("access_token")

    if token is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user = await get_user_model_based_on_token(token)

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
    token = request.cookies.get("access_token")

    if token is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user = await get_user_model_based_on_token(token)
    user_verification = UserVerification(password=password, new_password=password2)
    await change_password(user, db, user_verification)

    return templates.TemplateResponse(
        "change-user-password.html",
        {"request": request, "user": user, "msg": "Password updated"},
    )
