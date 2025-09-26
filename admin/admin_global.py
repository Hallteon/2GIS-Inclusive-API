from typing import Union

from sqladmin.authentication import AuthenticationBackend

from starlette.requests import Request
from starlette.responses import RedirectResponse
from passlib.context import CryptContext

from admin.admin_models.models_admin import *
from settings import config_parameters
from fastapi import status


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        if username != config_parameters.ADMIN_USERNAME:
            return False

        if not pwd_context.verify(password, config_parameters.ADMIN_HASHED_PASSWORD):
            return False

        request.session.update({"user": {'username': username,
                                         'password_hash': config_parameters.ADMIN_HASHED_PASSWORD}})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Union[bool, RedirectResponse]:
        user = request.session.get("user")

        if not user:
            # Перенаправляем на страницу входа
            return RedirectResponse(
                request.url_for("admin:login"),
                status_code=status.HTTP_302_FOUND
            )

        return True


admin_models = []