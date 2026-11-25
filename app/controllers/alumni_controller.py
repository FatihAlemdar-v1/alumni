from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.models import user as user_model
from app.views.alumni_view import render_alumni_directory


class AlumniController:
    def __init__(self) -> None:
        self.router = APIRouter(tags=["Alumni"])
        self.router.add_api_route("/alumni", self.list, methods=["GET"], response_class=HTMLResponse)

    def list(self, request: Request) -> HTMLResponse:
        return HTMLResponse(render_alumni_directory(user_model.get_users(), request.state.user))
