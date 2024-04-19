from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from api.auth import login_for_access_token
from database import SessionLocal

router = APIRouter()

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class LoginForm:
    def __init__(self, request: Request) -> None:
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self) -> None:
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


@router.get("/auth/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/auth/", response_class=HTMLResponse)
async def login(request: Request, db: db_dependency):
    try:
        login_form = LoginForm(request)
        await login_form.create_oauth_form()

        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
        token = (await login_for_access_token(form_data=login_form, db=db))[
            "access_token"
        ]

        await set_cookie(response=response, token=token)

        return response

    except HTTPException:
        return templates.TemplateResponse(
            "login.html", {"request": request, "msg": "Unknown Error"}
        )
    except ValueError:
        return templates.TemplateResponse(
            "login.html", {"request": request, "msg": "Incorrect Username of Password"}
        )


@router.get("/auth/logout/")
async def logout(request: Request):
    response = templates.TemplateResponse(
        "login.html", {"request": request, "msg": "Logout Successful"}
    )
    response.delete_cookie(key="access_token")
    return response


@router.get("/auth/register/", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


async def set_cookie(response: Response, token: str):
    response.set_cookie(key="access_token", value=token, httponly=True)
