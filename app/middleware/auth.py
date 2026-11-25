from urllib.parse import quote

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from sqlalchemy import text

from app.database.connection import get_engine
from app.security import decode_access_token, get_auth_user, is_admin


def _public_request(request: Request) -> bool:
    path = request.url.path
    if path in {
        "/", "/about", "/alumni", "/hello", "/api/health", "/api/swagger", "/docs",
        "/openapi.json", "/redoc", "/register", "/login", "/logout",
        "/api/auth/register", "/api/auth/login", "/api/auth/logout",
    } or path.startswith("/hello/") or path.startswith("/sum/"):
        return True
    if path.endswith("/edit"):
        return False
    if request.method not in {"GET", "HEAD"}:
        return False
    parts = [part for part in path.split("/") if part]
    return (
        path in {"/announcements", "/job-postings", "/api/job-postings", "/api/announcements"}
        or (
            len(parts) == 2
            and parts[1].isdigit()
            and parts[0] in {"announcements", "job-postings"}
        )
        or (
            len(parts) == 3
            and parts[0] == "api"
            and parts[1] in {"announcements", "job-postings"}
            and parts[2].isdigit()
        )
    )


def _is_admin_only(request: Request) -> bool:
    path = request.url.path
    if path == "/admin" or path.startswith("/admin/") or path == "/users" or path.startswith("/users/"):
        return True
    if path == "/api/users":
        return True
    if path.startswith("/api/users/"):
        parts = [part for part in path.split("/") if part]
        if len(parts) <= 3 or parts[3] not in {"applications", "job-postings"}:
            return True
    if path.startswith("/announcements") or path.startswith("/api/announcements"):
        return request.method not in {"GET", "HEAD"} or path.endswith("/edit")
    if path == "/applications" or path.startswith("/applications/"):
        return True
    if path == "/api/applications" and request.method == "GET":
        return True
    if path.startswith("/api/applications/") and request.method == "PATCH":
        return True
    if path.startswith("/api/job-postings/") and "/applications" in path and request.method != "POST":
        return True
    return False


def _owner_matches(table: str, row_id: int, user_id: int) -> bool:
    query = {
        "applications": "SELECT user_id FROM applications WHERE id = :id",
        "job_postings": "SELECT posted_by_user_id FROM job_postings WHERE id = :id",
    }[table]
    with get_engine().connect() as conn:
        owner_id = conn.execute(text(query), {"id": row_id}).scalar_one_or_none()
    return owner_id == user_id


def _resource_permission(request: Request, user: dict) -> bool:
    path = request.url.path
    user_id = user["id"]
    admin = is_admin(user)
    parts = [part for part in path.split("/") if part]

    if len(parts) >= 3 and parts[:2] == ["api", "users"] and parts[2].isdigit():
        if int(parts[2]) != user_id and not admin:
            return False

    app_id: int | None = None
    if parts[:2] == ["api", "applications"] and len(parts) == 3 and parts[2].isdigit():
        app_id = int(parts[2])
    elif parts[0] == "applications" and len(parts) >= 2 and parts[1].isdigit():
        app_id = int(parts[1])
    elif len(parts) >= 5 and parts[:2] == ["api", "job-postings"] and parts[3] == "applications":
        if len(parts) == 5 and parts[4].isdigit():
            app_id = int(parts[4])
        if request.method == "GET" and not admin:
            return False
    if app_id is not None and not admin and not _owner_matches("applications", app_id, user_id):
        return False

    posting_id: int | None = None
    if path.startswith("/api/job-postings/") and request.method in {"PUT", "PATCH", "DELETE"}:
        try:
            posting_id = int(parts[2])
        except (IndexError, ValueError):
            return True
    elif path.startswith("/job-postings/") and request.method in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        try:
            posting_id = int(parts[1])
        except (IndexError, ValueError):
            return True
    if posting_id is not None and not admin and not _owner_matches("job_postings", posting_id, user_id):
        return False
    return True


async def auth_middleware(request: Request, call_next) -> Response:
    token = request.cookies.get("access_token")
    if not token:
        authorization = request.headers.get("authorization", "")
        if authorization.lower().startswith("bearer "):
            token = authorization[7:].strip()

    user = None
    invalid_cookie = False
    if token:
        user_id = decode_access_token(token)
        user = get_auth_user(user_id) if user_id is not None else None
        invalid_cookie = user is None and "access_token" in request.cookies
    request.state.user = user

    if not _public_request(request):
        is_api = request.url.path.startswith("/api/")
        if user is None:
            if is_api:
                response: Response = JSONResponse({"detail": "Authentication required"}, status_code=401)
            else:
                response = RedirectResponse(
                    url=f"/login?next={quote(request.url.path, safe='/')}", status_code=303
                )
            if invalid_cookie:
                response.delete_cookie("access_token")
            return response
        if _is_admin_only(request) and not is_admin(user):
            response = JSONResponse({"detail": "Administrator role required"}, status_code=403) if is_api else Response(
                "Administrator role required", status_code=403, media_type="text/plain"
            )
            if invalid_cookie:
                response.delete_cookie("access_token")
            return response
        if not _resource_permission(request, user):
            return JSONResponse(
                {"detail": "You do not have access to this resource"}, status_code=403
            ) if is_api else Response(
                "You do not have access to this resource", status_code=403, media_type="text/plain"
            )

    response = await call_next(request)
    if invalid_cookie:
        response.delete_cookie("access_token")
    return response
