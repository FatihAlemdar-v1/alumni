from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pydantic import ValidationError

from app.security import (
    LoginData,
    RegisterData,
    authenticate_user,
    cookie_secure,
    create_access_token,
    ensure_auth_configured,
    register_user,
    token_ttl_minutes,
)
from app.views.auth_view import render_auth_form


class AuthController:
    def __init__(self) -> None:
        self.router = APIRouter(tags=["Authentication"])
        self.router.add_api_route("/register", self.register_page, methods=["GET"], response_class=HTMLResponse)
        self.router.add_api_route("/register", self.register_form, methods=["POST"], response_class=HTMLResponse)
        self.router.add_api_route("/login", self.login_page, methods=["GET"], response_class=HTMLResponse)
        self.router.add_api_route("/login", self.login_form, methods=["POST"], response_class=HTMLResponse)
        self.router.add_api_route("/logout", self.logout, methods=["POST"])
        self.router.add_api_route("/api/auth/register", self.register_api, methods=["POST"])
        self.router.add_api_route("/api/auth/login", self.login_api, methods=["POST"])
        self.router.add_api_route("/api/auth/logout", self.logout_api, methods=["POST"])
        self.router.add_api_route("/api/auth/me", self.me, methods=["GET"])

    def register_page(self) -> HTMLResponse:
        return HTMLResponse(render_auth_form(register=True))

    def register_form(
        self,
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        graduation_year: int = Form(...),
        department: str = Form(...),
        password: str = Form(...),
    ) -> HTMLResponse:
        try:
            ensure_auth_configured()
            data = RegisterData(
                name=f"{first_name.strip()} {last_name.strip()}".strip(),
                email=email.strip(),
                graduation_year=graduation_year,
                department=department.strip(),
                password=password,
            )
            user = register_user(data)
        except ValidationError as error:
            return HTMLResponse(render_auth_form(True, str(error)), status_code=422)
        except HTTPException as error:
            return HTMLResponse(render_auth_form(True, str(error.detail)), status_code=error.status_code)
        response = RedirectResponse("/", status_code=303)
        self._set_cookie(response, create_access_token(user["id"]))
        return response

    def login_page(self, request: Request) -> HTMLResponse:
        return HTMLResponse(
            render_auth_form(register=False, next_url=request.query_params.get("next", "/"))
        )

    def login_form(
        self,
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        next: str = Form("/"),
    ) -> HTMLResponse:
        try:
            data = LoginData(email=email.strip(), password=password)
        except ValidationError as error:
            return HTMLResponse(render_auth_form(False, str(error)), status_code=422)
        user = authenticate_user(data)
        if user is None:
            return HTMLResponse(render_auth_form(False, "E-posta veya şifre hatalı."), status_code=401)
        destination = request.query_params.get("next", next)
        if not destination.startswith("/") or destination.startswith("//"):
            destination = "/"
        response = RedirectResponse(destination, status_code=303)
        self._set_cookie(response, create_access_token(user["id"]))
        return response

    def register_api(self, data: RegisterData) -> JSONResponse:
        ensure_auth_configured()
        user = register_user(data)
        token = create_access_token(user["id"])
        response = JSONResponse({"user": user, "access_token": token, "token_type": "bearer"})
        self._set_cookie(response, token)
        return response

    def login_api(self, data: LoginData) -> JSONResponse:
        user = authenticate_user(data)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token = create_access_token(user["id"])
        response = JSONResponse({"user": user, "access_token": token, "token_type": "bearer"})
        self._set_cookie(response, token)
        return response

    def logout(self) -> RedirectResponse:
        response = RedirectResponse("/", status_code=303)
        response.delete_cookie("access_token", httponly=True, samesite="lax", secure=cookie_secure())
        return response

    def logout_api(self) -> JSONResponse:
        response = JSONResponse({"message": "Logged out"})
        response.delete_cookie("access_token", httponly=True, samesite="lax", secure=cookie_secure())
        return response

    def me(self, request: Request) -> dict:
        return {"user": request.state.user}

    @staticmethod
    def _set_cookie(response: Response, token: str) -> None:
        response.set_cookie(
            "access_token",
            token,
            httponly=True,
            secure=cookie_secure(),
            samesite="lax",
            max_age=60 * token_ttl_minutes(),
            path="/",
        )
