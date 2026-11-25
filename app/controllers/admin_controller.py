from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.models import job_posting as job_posting_model
from app.models.job_posting import JobPostingCreate, JobPostingUpdate
from app.security import admin_counts, delete_admin_user, list_admin_users, update_user_role
from app.views.admin_view import render_admin_dashboard, render_admin_job_postings


class AdminController:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/admin", tags=["Administration"])
        self.router.add_api_route("", self.dashboard, methods=["GET"], response_class=HTMLResponse)
        self.router.add_api_route("/users/{user_id}/role", self.change_role, methods=["POST"])
        self.router.add_api_route("/users/{user_id}/delete", self.delete_user, methods=["POST"])
        self.router.add_api_route("/job-postings", self.job_postings, methods=["GET"], response_class=HTMLResponse)
        self.router.add_api_route("/job-postings", self.create_job_posting, methods=["POST"])
        self.router.add_api_route(
            "/job-postings/{posting_id}/active", self.set_job_posting_active, methods=["POST"]
        )
        self.router.add_api_route(
            "/job-postings/{posting_id}/delete", self.delete_job_posting, methods=["POST"]
        )

    def dashboard(self, request: Request) -> HTMLResponse:
        return HTMLResponse(
            render_admin_dashboard(admin_counts(), list_admin_users(), request.state.user)
        )

    def change_role(self, user_id: int, role: str = Form(...)) -> RedirectResponse:
        update_user_role(user_id, role)
        return RedirectResponse("/admin", status_code=303)

    def delete_user(self, request: Request, user_id: int) -> RedirectResponse:
        delete_admin_user(user_id, request.state.user["id"])
        return RedirectResponse("/admin", status_code=303)

    def job_postings(self, request: Request) -> HTMLResponse:
        return HTMLResponse(
            render_admin_job_postings(job_posting_model.get_job_postings(), request.state.user)
        )

    def create_job_posting(
        self,
        title: str = Form(...),
        company: str = Form(...),
        location: str | None = Form(None),
        employment_type: str = Form(...),
        description: str | None = Form(None),
    ) -> RedirectResponse:
        try:
            data = JobPostingCreate(
                title=title.strip(),
                company=company.strip(),
                location=location.strip() if location else None,
                employment_type=employment_type,
                description=description.strip() if description else None,
                posted_by_user_id=None,
            )
        except ValidationError as error:
            raise HTTPException(status_code=422, detail=error.errors(include_url=False)) from error
        job_posting_model.create_job_posting(data)
        return RedirectResponse("/admin/job-postings", status_code=303)

    def set_job_posting_active(
        self, posting_id: int, is_active: bool = Form(...)
    ) -> RedirectResponse:
        job_posting_model.partial_update_job_posting(
            posting_id, JobPostingUpdate(is_active=is_active)
        )
        return RedirectResponse("/admin/job-postings", status_code=303)

    def delete_job_posting(self, posting_id: int) -> RedirectResponse:
        job_posting_model.delete_job_posting(posting_id)
        return RedirectResponse("/admin/job-postings", status_code=303)
