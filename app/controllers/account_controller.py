from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.models import application as application_model
from app.models import job_posting as job_posting_model
from app.models.job_posting import JobPostingBase
from app.security import ProfileData, update_profile
from app.views.auth_view import render_my_applications, render_my_job_postings, render_profile


class AccountController:
    def __init__(self) -> None:
        self.router = APIRouter(tags=["Account"])
        self.router.add_api_route("/profile", self.profile, methods=["GET"], response_class=HTMLResponse)
        self.router.add_api_route("/profile", self.save_profile, methods=["POST"], response_class=HTMLResponse)
        self.router.add_api_route("/my-applications", self.my_applications, methods=["GET"], response_class=HTMLResponse)
        self.router.add_api_route("/my-applications", self.apply, methods=["POST"])
        self.router.add_api_route("/my-applications/{application_id}/delete", self.withdraw, methods=["POST"])
        self.router.add_api_route("/my-job-postings", self.my_job_postings, methods=["GET"], response_class=HTMLResponse)
        self.router.add_api_route("/my-job-postings", self.create_job_posting, methods=["POST"])
        self.router.add_api_route("/my-job-postings/{posting_id}/delete", self.delete_job_posting, methods=["POST"])

    def profile(self, request: Request) -> HTMLResponse:
        return HTMLResponse(render_profile(request.state.user))

    def save_profile(
        self,
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        graduation_year: int = Form(...),
        department: str = Form(...),
    ) -> HTMLResponse:
        try:
            user = update_profile(
                request.state.user["id"],
                ProfileData(name=name.strip(), email=email.strip(), graduation_year=graduation_year,
                            department=department.strip()),
            )
        except ValidationError as error:
            return HTMLResponse(render_profile(request.state.user, str(error)), status_code=422)
        except HTTPException as error:
            return HTMLResponse(render_profile(request.state.user, str(error.detail)), status_code=error.status_code)
        return HTMLResponse(render_profile(user, saved=True))

    def my_applications(self, request: Request) -> HTMLResponse:
        records = application_model.get_applications(user_id=request.state.user["id"])
        return HTMLResponse(render_my_applications(records, request.state.user))

    def apply(
        self,
        request: Request,
        job_posting_id: int = Form(...),
        cover_letter: str | None = Form(None),
    ) -> RedirectResponse:
        application_model.create_application(
            request.state.user["id"], job_posting_id, cover_letter.strip() if cover_letter else None
        )
        return RedirectResponse("/my-applications", status_code=303)

    def withdraw(self, request: Request, application_id: int) -> RedirectResponse:
        application_model.delete_application(application_id, user_id=request.state.user["id"])
        return RedirectResponse("/my-applications", status_code=303)

    def my_job_postings(self, request: Request) -> HTMLResponse:
        records = job_posting_model.get_job_postings(user_id=request.state.user["id"])
        return HTMLResponse(render_my_job_postings(records, request.state.user))

    def create_job_posting(
        self,
        request: Request,
        title: str = Form(...),
        company: str = Form(...),
        location: str | None = Form(None),
        employment_type: str = Form(...),
        description: str | None = Form(None),
    ) -> RedirectResponse:
        posting = JobPostingBase(
            title=title.strip(), company=company.strip(),
            location=location.strip() if location else None,
            employment_type=employment_type,
            description=description.strip() if description else None,
        )
        job_posting_model.create_job_posting_for_user(request.state.user["id"], posting)
        return RedirectResponse("/my-job-postings", status_code=303)

    def delete_job_posting(self, request: Request, posting_id: int) -> RedirectResponse:
        job_posting_model.delete_job_posting(posting_id, user_id=request.state.user["id"])
        return RedirectResponse("/my-job-postings", status_code=303)
