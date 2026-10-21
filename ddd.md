# Data Design Documentation (DDD)

> Back to [README.md](README.md)

This document describes the database design of the Alumni Tracking System. The tables below are created by the migrations in [section 7](#7-migrations), and the app reads and writes them through the models in `app/models/` (see [section 8](#8-from-in-memory-models-to-tables)).

## 1. Why a Database

The app first stored records in memory. The "forgetting test" showed the problem:

1. Create a user and an announcement.
2. Run `docker compose down` followed by `docker compose up`.
3. Check the records: both lists came back empty.

Restarting the container wiped the Python process's memory, so all data was lost. A database keeps data on disk, independent of the app process, so records survive restarts. After connecting the app to PostgreSQL, the same test passes: the records are still there after `down` and `up`.

## 2. Database Choice

| Decision | Choice | Reason |
| --- | --- | --- |
| DBMS | PostgreSQL 16 | Already defined as the `db` service in `docker-compose.yml`, with a persistent `pgdata` volume. |
| Connection | `DATABASE_URL=postgresql://USER:PASSWORD@db:5432/DB_NAME` | Passed to the `api` service as an environment variable. The real values live in `.env` (git ignored); `.env.example` is the committed template. See the Environment Variables section of the README. |
| Credentials | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Read from `.env` by `docker-compose.yml`, no longer hard-coded. They apply only when the `pgdata` volume is first created. |
| Access from Python | SQLAlchemy + psycopg2 | Both are already listed in `requirements.txt`. |
| Startup order | `db` healthcheck (`pg_isready`) + `depends_on: condition: service_healthy` | The `api` container starts only after PostgreSQL accepts connections, so the app never tries to connect to a database that is still booting. |
| Table creation | Alembic migrations (`migrations/`) | Tables are created by running `alembic upgrade head` inside the `api` container. See section 7. |

## 3. Entities

The system has three entities:

- **User**: an MIS graduate (alumnus/alumna) tracked by the system.
- **Announcement**: a news item or notice published to graduates (e.g. a graduation ceremony, an event).
- **Job Posting**: a job or internship offer shared with graduates, optionally posted by a registered user (e.g. an alumnus hiring at their company).

## 4. Tables

### 4.1 `users`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-incremented identifier. |
| `name` | `VARCHAR(100)` | `NOT NULL` | Full name of the graduate. |
| `email` | `VARCHAR(255)` | `NOT NULL`, `UNIQUE` | Contact email. Unique so the same person cannot be registered twice. |
| `graduation_year` | `INTEGER` | `NOT NULL`, `CHECK (graduation_year BETWEEN 1950 AND 2100)` | Year of graduation. |
| `department` | `VARCHAR(100)` | `NOT NULL` | Department graduated from. |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When the record was created. |
| `updated_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When the record was last changed. |

### 4.2 `announcements`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-incremented identifier. |
| `title` | `VARCHAR(200)` | `NOT NULL` | Headline of the announcement. |
| `content` | `TEXT` | `NOT NULL` | Body text, no length limit. |
| `author` | `VARCHAR(100)` | `NOT NULL` | Who published it (e.g. "Department Office"). |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When the announcement was published. |
| `updated_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When it was last edited. |

### 4.3 `job_postings`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-incremented identifier. |
| `title` | `VARCHAR(200)` | `NOT NULL` | Position title (e.g. "Junior Data Analyst"). |
| `company` | `VARCHAR(150)` | `NOT NULL` | Hiring company. |
| `location` | `VARCHAR(150)` | `NOT NULL` | City, or "Remote". |
| `employment_type` | `VARCHAR(20)` | `NOT NULL`, `CHECK (employment_type IN ('full_time', 'part_time', 'internship', 'contract'))` | Kind of position. A fixed list so filtering by type is reliable. |
| `description` | `TEXT` | `NOT NULL` | Responsibilities and requirements, no length limit. |
| `application_url` | `VARCHAR(500)` | nullable | Where to apply. Optional: some postings only give a contact in the description. |
| `deadline` | `DATE` | nullable | Last day to apply. Optional: some postings stay open until filled. |
| `is_active` | `BOOLEAN` | `NOT NULL`, `DEFAULT TRUE` | `FALSE` hides a filled or expired posting without deleting it. |
| `posted_by_user_id` | `INTEGER` | nullable, `REFERENCES users(id) ON DELETE SET NULL` | The user who shared the posting. `NULL` when the department posts it, or when the user is later deleted. |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When the posting was created. |
| `updated_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When it was last edited. |

| Index | Columns | Reason |
| --- | --- | --- |
| `ix_job_postings_posted_by_user_id` | `posted_by_user_id` | PostgreSQL does not index foreign keys automatically. This keeps "postings by this user" lookups and user deletes fast. |

## 5. Relationships

### `users` (1) &mdash; `job_postings` (N)

One user can post multiple job postings. A job posting belongs to at most one user (it can also be posted by the department, in which case `posted_by_user_id` is `NULL`).

- **Foreign key:** `job_postings.posted_by_user_id -> users.id`.
- **On delete:** `SET NULL`. If a user is deleted, their postings stay in the system with `posted_by_user_id = NULL`. The department keeps the posting and applicants can still find it.

## 6. DDL (PostgreSQL Schema)

```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    graduation_year INTEGER      NOT NULL CHECK (graduation_year BETWEEN 1950 AND 2100),
    department      VARCHAR(100) NOT NULL,
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE announcements (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    content    TEXT         NOT NULL,
    author     VARCHAR(100) NOT NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_postings (
    id                 SERIAL PRIMARY KEY,
    title              VARCHAR(200) NOT NULL,
    company            VARCHAR(150) NOT NULL,
    location           VARCHAR(150) NOT NULL,
    employment_type    VARCHAR(20)  NOT NULL CHECK (employment_type IN ('full_time', 'part_time', 'internship', 'contract')),
    description        TEXT         NOT NULL,
    application_url    VARCHAR(500),
    deadline           DATE,
    is_active          BOOLEAN      NOT NULL DEFAULT TRUE,
    posted_by_user_id  INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    created_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_job_postings_posted_by_user_id ON job_postings (posted_by_user_id);
```

The SQL above is shown for reading. It is not run by hand: migrations produce the same tables.

## 7. Migrations

Migrations are managed with [Alembic](https://alembic.sqlalchemy.org/). Each migration is a Python file in `migrations/versions/` with an `upgrade()` (apply) and a `downgrade()` (undo) function.

| Revision | File | What it does |
| --- | --- | --- |
| `0001` | `migrations/versions/0001_create_users_and_announcements.py` | Creates `users` and `announcements`. |
| `0002` | `migrations/versions/0002_create_job_postings.py` | Creates `job_postings` table and foreign key to `users`. |

## 8. Naming Conventions

- Table names are plural and lowercase: `users`, `announcements`, `job_postings`.
- Column names use `snake_case`: `graduation_year`, `created_at`, `posted_by_user_id`.
- Every table has an `id` primary key plus `created_at` and `updated_at` columns.
- Foreign keys are named `<role>_<table>_id`: `posted_by_user_id`.
