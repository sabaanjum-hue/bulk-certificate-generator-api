import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def wait_for_completion(job_id: str, timeout: float = 5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = client.get(f"/api/v1/jobs/{job_id}").json()
        if data["status"] in {"completed", "completed_with_errors", "failed"}:
            return data
        time.sleep(0.05)
    raise AssertionError("Job did not finish within timeout")

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_generation_job():
    response = client.post("/api/v1/jobs", json={
        "event_name": "Test Event",
        "course": "Backend Engineering",
        "issue_date": "2026-10-07",
        "recipients": [
            {"name": "Test User", "email": "test@example.com"},
            {"name": "Second User", "email": "second@example.com"}
        ]
    })
    assert response.status_code == 202
    assert response.json()["total"] == 2

def test_input_validation():
    response = client.post("/api/v1/jobs", json={
        "event_name": "Test Event",
        "course": "Backend Engineering",
        "issue_date": "2026-10-07",
        "recipients": [{"name": "A", "email": "not-an-email"}]
    })
    assert response.status_code == 422

def test_certificate_generation_and_retrieval():
    response = client.post("/api/v1/jobs", json={
        "event_name": "Generation Test",
        "course": "Python",
        "issue_date": "2026-10-07",
        "recipients": [{"name": "Generated User", "email": "generated@example.com"}]
    })
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    status = wait_for_completion(job_id)
    assert status["processed"] == 1
    assert status["successful"] == 1

    certificates = client.get("/api/v1/certificates", params={"job_id": job_id})
    assert certificates.status_code == 200
    certificate = certificates.json()[0]
    assert certificate["status"] == "generated"

    download = client.get(f"/api/v1/certificates/{certificate['id']}/download")
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"
