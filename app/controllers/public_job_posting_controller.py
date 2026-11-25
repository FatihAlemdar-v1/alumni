from datetime import date

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.models import job_posting as job_posting_model
from app.views.public_job_posting_view import render_job_posting_detail, render_job_postings


class PublicJobPostingController:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/job-postings", tags=["JobPosting"])
        self.router.add_api_route("", self.list, methods=["GET"], response_class=HTMLResponse)
        self.router.add_api_route("/{posting_id}", self.get, methods=["GET"], response_class=HTMLResponse)

    def list(self, request: Request) -> HTMLResponse:
        postings = [
            item
            for item in job_posting_model.get_job_postings()
            if item["is_active"] and (item["deadline"] is None or date.fromisoformat(item["deadline"]) >= date.today())
        ]
        return HTMLResponse(render_job_postings(postings, request.state.user))

    def get(self, request: Request, posting_id: int) -> HTMLResponse:
        posting = job_posting_model.get_job_posting(posting_id)
        if not posting["is_active"] or (
            posting["deadline"] is not None
            and date.fromisoformat(posting["deadline"]) < date.today()
        ):
            raise HTTPException(status_code=404, detail="Job posting not found")
        return HTMLResponse(render_job_posting_detail(posting, request.state.user))
