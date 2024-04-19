from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from api.auth import login_for_access_token, create_user, CreateUserRequest
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


@router.post("/auth/register/", response_class=HTMLResponse)
async def register_user(
    request: Request,
    db: db_dependency,
    email: str = Form(...),
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    phone: str = Form(...),
):
    if password != password2:
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": "Passwords do not match"}
        )
    user_request = CreateUserRequest(
        email=email,
        username=username,
        first_name=firstname,
        last_name=lastname,
        password=password,
        role="standard",
        phone_number=phone,
    )

    try:
        await create_user(db=db, create_user_request=user_request)
    except HTTPException:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "msg": "Username/email already exists"},
        )

    return templates.TemplateResponse(
        "login.html", {"request": request, "msg": "User successfully created"}
    )


async def set_cookie(response: Response, token: str):
    response.set_cookie(key="access_token", value=token, httponly=True)
