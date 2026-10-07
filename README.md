# Bulk Certificate Generator API

A FastAPI backend for bulk certificate generation, designed for the Aereo SDE Intern assignment.

## Features
- REST API with FastAPI
- One request for many recipients
- SQLite persistence with SQLAlchemy
- Background job processing
- Pydantic input validation
- Partial failure handling
- Job progress/status tracking
- PDF certificate generation using one predefined template
- Certificate listing and PDF download
- Pytest test suite

## Setup
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI: `http://127.0.0.1:8000/docs`

## Main endpoints
- `POST /api/v1/jobs` — create one bulk generation job
- `GET /api/v1/jobs/{job_id}` — track progress and failures
- `GET /api/v1/certificates?job_id={job_id}` — retrieve generated certificate records
- `GET /api/v1/certificates/{certificate_id}/download` — download a generated PDF
- `GET /health` — health check

## Example request
```json
{
  "event_name": "Aereo Python Workshop",
  "course": "Backend Engineering",
  "issue_date": "2026-10-07",
  "recipients": [
    {"name": "Aarav Sharma", "email": "aarav@example.com"},
    {"name": "Saba Anjum", "email": "saba@example.com"}
  ]
}
```

## Design decisions
FastAPI BackgroundTasks is used to keep the assignment self-contained while providing job-style asynchronous processing. Each recipient is processed independently, so one generation failure does not cancel the rest. SQLite keeps local setup simple; the persistence layer can be moved to PostgreSQL in production. A durable queue such as Celery/RQ with Redis would be appropriate for a larger production workload.

## Testing
```bash
pytest -q
```

Tests cover job creation, input validation, certificate generation/retrieval, job progress, and individual processing behavior.
