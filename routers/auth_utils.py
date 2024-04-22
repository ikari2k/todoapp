from starlette import status
from starlette.responses import RedirectResponse
from fastapi import Request, HTTPException
from api.auth import get_current_user
from typing import Dict


async def get_user_model_based_on_request(request: Request) -> Dict | RedirectResponse:
    token = request.cookies.get("access_token")
    if token is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    try:
        user = await get_current_user(token)
    except HTTPException:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return user
