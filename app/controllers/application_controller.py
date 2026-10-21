from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.models import application as application_model
from app.models.application import ApplicationStatus, ApplicationUpdate
from app.views.application_view import render_application_detail, render_application_list


class ApplicationController:
    """Independent controller: manages applications under /applications through HTML views."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/applications", tags=["Application"])
        self.router.add_api_route("", self.list, methods=["GET"])
        self.router.add_api_route("", self.create, methods=["POST"])
        self.router.add_api_route("/{application_id}", self.get, methods=["GET"])
        self.router.add_api_route("/{application_id}/status", self.update_status, methods=["POST"])
        self.router.add_api_route("/{application_id}/delete", self.delete, methods=["POST"])

    def list(self) -> HTMLResponse:
        """GET /applications -> renders applications table."""
        applications = application_model.get_applications()
        return HTMLResponse(render_application_list(applications))

    def create(
        self,
        user_id: int = Form(...),
        job_posting_id: int = Form(...),
        cover_letter: str | None = Form(None),
    ) -> RedirectResponse:
        """POST /applications -> create an application."""
        letter = cover_letter.strip() if cover_letter and cover_letter.strip() else None
        created = application_model.create_application(user_id=user_id, job_posting_id=job_posting_id, cover_letter=letter)
        return RedirectResponse(url=f"/applications/{created['id']}", status_code=303)

    def get(self, application_id: int) -> HTMLResponse:
        """GET /applications/{id} -> renders detail."""
        application = application_model.get_application(application_id)
        return HTMLResponse(render_application_detail(application))

    def update_status(
        self,
        application_id: int,
        status: ApplicationStatus = Form(...),
    ) -> RedirectResponse:
        """POST /applications/{id}/status -> update status."""
        application_model.update_application(application_id, ApplicationUpdate(status=status))
        return RedirectResponse(url=f"/applications/{application_id}", status_code=303)

    def delete(self, application_id: int) -> RedirectResponse:
        """POST /applications/{id}/delete -> withdraw application."""
        application_model.delete_application(application_id)
        return RedirectResponse(url="/applications", status_code=303)
