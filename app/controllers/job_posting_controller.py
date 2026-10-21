from datetime import date

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.models import application as application_model
from app.models import job_posting as job_posting_model
from app.models.job_posting import JobPostingCreate, JobPostingUpdate
from app.views.job_posting_view import (
    render_job_posting_detail,
    render_job_posting_edit_form,
    render_job_posting_list,
)


class JobPostingController:
    """Independent controller: full CRUD for job postings under /job-postings, managed through the HTML view layer."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/job-postings", tags=["JobPosting"])
        self.router.add_api_route("", self.list, methods=["GET"])
        self.router.add_api_route("", self.create, methods=["POST"])
        self.router.add_api_route("/{posting_id}", self.get, methods=["GET"])
        self.router.add_api_route("/{posting_id}/edit", self.edit_form, methods=["GET"])
        self.router.add_api_route("/{posting_id}/edit", self.update, methods=["POST"])
        self.router.add_api_route("/{posting_id}/delete", self.delete, methods=["POST"])

    def list(self) -> HTMLResponse:
        """GET /job-postings -> renders the job postings table and create form."""
        postings = job_posting_model.get_job_postings()
        return HTMLResponse(render_job_posting_list(postings))

    def create(
        self,
        title: str = Form(...),
        company: str = Form(...),
        location: str = Form(...),
        employment_type: str = Form(...),
        description: str = Form(...),
        application_url: str | None = Form(None),
        deadline: str | None = Form(None),
        posted_by_user_id: str | None = Form(None),
    ) -> RedirectResponse:
        """POST /job-postings -> create new posting from form."""
        try:
            deadline_date = date.fromisoformat(deadline) if deadline else None
            user_id = int(posted_by_user_id) if posted_by_user_id and posted_by_user_id.strip() else None
            app_url = application_url.strip() if application_url and application_url.strip() else None

            payload = JobPostingCreate(
                title=title,
                company=company,
                location=location,
                employment_type=employment_type,
                description=description,
                application_url=app_url,
                deadline=deadline_date,
                posted_by_user_id=user_id,
            )
            created = job_posting_model.create_job_posting(payload)
        except (ValidationError, HTTPException, ValueError) as err:
            raise HTTPException(status_code=422, detail=str(err)) from err

        return RedirectResponse(url=f"/job-postings/{created['id']}", status_code=303)

    def get(self, posting_id: int) -> HTMLResponse:
        """GET /job-postings/{id} -> renders details and applications for this posting."""
        posting = job_posting_model.get_job_posting(posting_id)
        applications = application_model.get_applications(job_posting_id=posting_id)
        return HTMLResponse(render_job_posting_detail(posting, applications))

    def edit_form(self, posting_id: int) -> HTMLResponse:
        """GET /job-postings/{id}/edit -> edit form."""
        posting = job_posting_model.get_job_posting(posting_id)
        return HTMLResponse(render_job_posting_edit_form(posting))

    def update(
        self,
        posting_id: int,
        title: str = Form(...),
        company: str = Form(...),
        location: str = Form(...),
        employment_type: str = Form(...),
        description: str = Form(...),
        application_url: str | None = Form(None),
        deadline: str | None = Form(None),
        is_active: str = Form("true"),
        posted_by_user_id: str | None = Form(None),
    ) -> RedirectResponse:
        """POST /job-postings/{id}/edit -> update posting."""
        try:
            deadline_date = date.fromisoformat(deadline) if deadline else None
            user_id = int(posted_by_user_id) if posted_by_user_id and posted_by_user_id.strip() else None
            app_url = application_url.strip() if application_url and application_url.strip() else None
            active_bool = is_active.lower() == "true"

            payload = JobPostingUpdate(
                title=title,
                company=company,
                location=location,
                employment_type=employment_type,
                description=description,
                application_url=app_url,
                deadline=deadline_date,
                is_active=active_bool,
                posted_by_user_id=user_id,
            )
            job_posting_model.update_job_posting(posting_id, payload)
        except (ValidationError, HTTPException, ValueError) as err:
            raise HTTPException(status_code=422, detail=str(err)) from err

        return RedirectResponse(url=f"/job-postings/{posting_id}", status_code=303)

    def delete(self, posting_id: int) -> RedirectResponse:
        """POST /job-postings/{id}/delete -> delete posting."""
        job_posting_model.delete_job_posting(posting_id)
        return RedirectResponse(url="/job-postings", status_code=303)
