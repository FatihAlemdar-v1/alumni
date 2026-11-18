import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from app.controllers.announcement_controller import AnnouncementController
from app.controllers.api_announcement_controller import ApiAnnouncementController
from app.controllers.api_application_controller import ApiApplicationController
from app.controllers.api_job_posting_controller import ApiJobPostingController
from app.controllers.api_user_controller import ApiUserController
from app.controllers.application_controller import ApplicationController
from app.controllers.job_posting_controller import JobPostingController
from app.controllers.user_controller import UserController

app = FastAPI(title="Alumni Tracking System")

TEMPLATES_DIR = Path(__file__).parent / "templates"
INDEX_HTML = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
ABOUT_HTML = (TEMPLATES_DIR / "about.html").read_text(encoding="utf-8")
NOT_FOUND_HTML = (TEMPLATES_DIR / "404.html").read_text(encoding="utf-8")

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("alumni_logger")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    formatter = logging.Formatter("%(message)s")
    file_handler = logging.FileHandler(LOGS_DIR / "error.log", encoding="utf-8")
    stream_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


@app.middleware("http")
async def system_logger_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        process_time_ms = round((time.perf_counter() - start_time) * 1000)
        current_time = time.strftime("%H:%M:%S")
        logger.info(
            f"{current_time} {request.method} {request.url.path} "
            f"{status.HTTP_500_INTERNAL_SERVER_ERROR} {process_time_ms}ms"
        )
        raise

    process_time_ms = round((time.perf_counter() - start_time) * 1000)
    current_time = time.strftime("%H:%M:%S")
    logger.info(
        f"{current_time} {request.method} {request.url.path} "
        f"{response.status_code} {process_time_ms}ms"
    )
    return response


@app.exception_handler(404)
async def not_found_guardian(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error_code": "RESOURCE_MISSING",
                "reason": f"'{request.url.path}' yolunda aradığınız veri mezun sisteminde bulunamadı.",
            },
        )
    return HTMLResponse(content=NOT_FOUND_HTML, status_code=status.HTTP_404_NOT_FOUND)


@app.exception_handler(500)
async def internal_error_guardian(request: Request, exc: Exception):
    logger.error(f"CRITICAL SYSTEM ERROR at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "SYSTEM_FAULT",
            "reason": "Sunucu tarafında beklenmeyen bir hata oluştu. Mühendislerimiz bilgilendirildi.",
        },
    )

user_controller = UserController()
api_user_controller = ApiUserController()
app.include_router(user_controller.router)
app.include_router(api_user_controller.router)

announcement_controller = AnnouncementController()
api_announcement_controller = ApiAnnouncementController()
app.include_router(announcement_controller.router)
app.include_router(api_announcement_controller.router)

job_posting_controller = JobPostingController()
api_job_posting_controller = ApiJobPostingController()
app.include_router(job_posting_controller.router)
app.include_router(api_job_posting_controller.router)
app.include_router(api_job_posting_controller.nested_router)

application_controller = ApplicationController()
api_application_controller = ApiApplicationController()
app.include_router(application_controller.router)
app.include_router(api_application_controller.router)
app.include_router(api_application_controller.user_router)
app.include_router(api_application_controller.posting_router)


@app.get("/", response_class=HTMLResponse)
def read_root():
    return INDEX_HTML


@app.get("/about", response_class=HTMLResponse)
def read_about():
    return ABOUT_HTML


@app.get("/hello")
def read_hello():
    return "Hello, World!"


@app.get("/hello/{name}")
def read_hello_name(name: str):
    return f"Hello, {name.capitalize()}!"


@app.get("/sum/{number1}/{number2}")
def read_sum(number1: int, number2: int):
    return number1 + number2


@app.get("/api/health")
def read_health():
    return {"status": "ok"}


@app.get("/api/swagger", include_in_schema=False)
def read_swagger():
    return RedirectResponse(url="/docs")
