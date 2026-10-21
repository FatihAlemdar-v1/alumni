# 🎓 Alumni Tracking System

A comprehensive backend system to track Management Information Systems (MIS) graduates. Built as a part of the Web Programming (YBSB3001) course, this project provides both a RESTful JSON API and a server-side rendered Web UI.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ed.svg)
![Status](https://img.shields.io/badge/Status-Work_in_Progress-orange.svg)

---

## 🚀 Overview & Tech Stack

This project is built incrementally week by week. It follows a clean architecture to manage users, job postings, applications, and announcements.

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose
- **ORM & Migrations:** SQLAlchemy & Alembic
- **Data Seeding:** Faker

---

## 🏗 Project Architecture (MVC)

The project follows the Model–View–Controller (MVC) pattern, split into dedicated files and folders under the `app/` directory:

| Layer | Location | Responsibility |
| :--- | :--- | :--- |
| **Model** | `app/models/` | SQLAlchemy ORM models (`User`, `Announcement`, `JobPosting`, `Application`), Pydantic schemas, and CRUD functions. Reads/writes to PostgreSQL. |
| **View** | `app/views/`, `app/templates/` | Builds the HTML returned to the browser. Shared layouts and static pages (`index.html`, `about.html`). |
| **Controller** | `app/controllers/` | Two independent controllers per resource (e.g., `UserController` for HTML pages, `ApiUserController` for JSON). Wired together in `main.py`. |

<details>
<summary><b>📂 Click to expand the full folder structure</b></summary>

```text
AlumniTrackingSystem/
├── app/
│   ├── __init__.py
│   ├── main.py                          # Wires routers into the FastAPI app
│   ├── controllers/                     # Route handlers (HTML and JSON)
│   ├── database/                        # DB connection, factories, and seeders
│   ├── models/                          # ORM models (User, JobPosting, etc.)
│   ├── views/                           # Shared layouts and view builders
│   └── templates/                       # Static HTML pages
├── migrations/                          # Alembic migrations (database schema)
│   ├── env.py
│   └── versions/
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                                 # Real values (git ignored)
├── .env.example                         # Template, committed to git
├── ddd.md                               # Data Design Documentation
└── README.md
```

</details>

---

## 🚦 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/FatihAlemdar-v1/alumni.git
cd alumni
```

### 2. Configure Environment Variables

Create your environment file from the template:

```bash
cp .env.example .env
```

Open `.env` and set your own values. **Never commit `.env` to Git.**

| Variable | Used By | Description |
| --- | --- | --- |
| `POSTGRES_USER` | `db` | Database user created on first start. |
| `POSTGRES_PASSWORD` | `db` | Password for the database user. |
| `POSTGRES_DB` | `db` | Name of the database. |
| `POSTGRES_PORT` | `db` | Host port mapped to PostgreSQL (default 5432). |
| `API_PORT` | `api` | Host port mapped to the FastAPI app (default 8000). |
| `DATABASE_URL` | `api` | Connection string: `postgresql://USER:PASSWORD@db:5432/DB_NAME`. |

*Note: Database credentials only apply when the volume is created for the first time. To apply new values, run `docker compose down -v` (this deletes stored data).*

### 3. Start the System

```bash
docker compose up -d
```

### 4. Run Migrations (Create Tables)

```bash
docker compose exec api alembic upgrade head
```

### 5. Access the App

- **API Docs (Swagger UI):** [http://localhost:8000/api/swagger](http://localhost:8000/api/swagger) (Auto-updated with every endpoint)
- **Health Check:** `GET /api/health`

---

## 🗄 Database Documentation & Migrations

The single source of truth for the database design is **`ddd.md`** (Data Design Documentation). Every change to the database (new table, column, constraint, index, or relationship) must be documented in `ddd.md` in the same commit.

The database schema is created by Alembic migrations (located in `migrations/versions/`).

| Command | Meaning |
| --- | --- |
| `docker compose exec api alembic upgrade head` | Create/update the tables to the latest version. |
| `docker compose exec api alembic current` | Show the current database version. |
| `docker compose exec api alembic downgrade base` | Undo all migrations (drops the tables and their data). |

To inspect tables directly inside PostgreSQL:

```bash
docker compose exec db psql -U alumni -d alumni -c "\dt"
```

---

## 🌱 Factories and Seeding

Factories (`app/database/factories.py`) generate realistic fake data using Faker. The seeder (`app/database/seed.py`) inserts them into the database to easily fill tables for testing.

| Command | Meaning |
| --- | --- |
| `docker compose exec api python -m app.database.seed` | Add 20 users, 10 announcements, and 15 job postings. |
| `docker compose exec api python -m app.database.seed --users 50 --announcements 5 --job-postings 30` | Choose the counts (0 skips a table). |
| `docker compose exec api python -m app.database.seed --fresh` | Empty all tables (including applications), reset IDs, then seed. |
| `docker compose exec api python -m app.database.seed --seed 7` | Same fake data on every run (use with `--fresh`). |

---

## 🛣 API & Web Routes

The application features dual routing: traditional HTML pages for browsers, and JSON API routes for clients/Postman.

### Web Interface (HTML Pages)

HTML forms only send GET/POST, so update and delete use POST sub-routes.

- **Users:** `GET /users`, `POST /users`, `GET /users/{id}`, `GET /users/{id}/edit`, `POST /users/{id}/edit`, `POST /users/{id}/delete`
- **Announcements:** `GET /announcements`, `POST /announcements`, `GET /announcements/{id}`, `GET /announcements/{id}/edit`, `POST /announcements/{id}/edit`, `POST /announcements/{id}/delete`
- **Job Postings:** `GET /job-postings`, `POST /job-postings`, `GET /job-postings/{id}`, `GET /job-postings/{id}/edit`, `POST /job-postings/{id}/edit`, `POST /job-postings/{id}/delete`
- **Applications:** `GET /applications`, `POST /applications`, `GET /applications/{id}`, `POST /applications/{id}/status`, `POST /applications/{id}/delete`

### JSON API (Swagger / Postman)

*All routes return JSON.* `404` for missing IDs, `409` for duplicate emails/applications, `422` for invalid input.

| Resource | Methods | Base Path | Description |
| --- | --- | --- | --- |
| **Users** | `GET, POST, PUT, PATCH, DELETE` | `/api/users` | Manage users (ApiUser tag). |
| **Announcements** | `GET, POST, PUT, PATCH, DELETE` | `/api/announcements` | Manage announcements. |
| **Job Postings** | `GET, POST, PUT, PATCH, DELETE` | `/api/job-postings` | Direct route. `posted_by_user_id` in body. |
| **Applications** | `GET, POST, PATCH, DELETE` | `/api/applications` | Direct route. Apply with `user_id` & `job_posting_id`. |

**Nested API Routes (Relational):**

- `GET, POST, DELETE` on `/api/users/{user_id}/job-postings` (Job postings belonging to a specific user)
- `GET, POST, DELETE` on `/api/users/{user_id}/applications` (Applications submitted by a user)
- `GET, POST, PATCH` on `/api/job-postings/{posting_id}/applications` (Applicants for a specific job posting)
