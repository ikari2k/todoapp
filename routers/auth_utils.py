from typing import Dict

from fastapi import HTTPException
from starlette import status
from starlette.responses import RedirectResponse

from api.auth import get_current_user


async def get_user_model_based_on_token(token) -> Dict | RedirectResponse:
    try:
        user = await get_current_user(token)
    except HTTPException:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return user
