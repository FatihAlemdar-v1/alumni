# 🎓 Alumni Tracking System

A comprehensive backend system to track Management Information Systems (MIS) graduates. Built as a part of the Web Programming (YBSB3001) course, this project provides both a RESTful JSON API and a server-side rendered Web UI.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ed.svg)

---

## 🚀 Features

- **Dual Interface:** Fully functional JSON API (with Swagger documentation) and a traditional Web interface (HTML forms/pages).
- **Relational Database:** Robust PostgreSQL schema managed by Alembic migrations.
- **Containerized:** Instant setup and deployment using Docker and Docker Compose.
- **Data Generation:** Built-in Faker seeding to instantly populate the database with realistic test data.
- **MVC Architecture:** Clean separation of concerns (Models, Views, Controllers).

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend Framework** | FastAPI (Python) |
| **Database** | PostgreSQL |
| **ORM & Migrations** | SQLAlchemy & Alembic |
| **Containerization** | Docker & Docker Compose |
| **Data Seeding** | Faker |

---

## 🏗 Project Architecture (MVC)

The project strictly follows the Model–View–Controller (MVC) architectural pattern:

| Layer | Location | Responsibility |
| :--- | :--- | :--- |
| **Model** | `app/models/` | SQLAlchemy ORM models, Pydantic schemas, and CRUD functions. Defines tables, relationships, and data validation. |
| **View** | `app/views/`, `app/templates/` | Builds the HTML returned to the browser. For API routes, the JSON response itself acts as the view. |
| **Controller** | `app/controllers/` | Routes incoming requests. Two independent controllers exist per resource: one for HTML pages (`UserController`) and one for the JSON API (`ApiUserController`). |

<details>
<summary><b>Click to expand folder structure</b></summary>

```text
AlumniTrackingSystem/
├── app/
│   ├── main.py                          # Wires routers into the FastAPI app
│   ├── controllers/                     # Route handlers (HTML and JSON)
│   ├── database/                        # DB connection, factories, and seeders
│   ├── models/                          # ORM models (User, JobPosting, etc.)
│   ├── views/                           # Shared layouts and view builders
│   └── templates/                       # Static HTML pages
├── migrations/                          # Alembic migrations
├── ddd.md                               # Data Design Documentation
├── docker-compose.yml
├── requirements.txt
└── .env.example
