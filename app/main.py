from uuid import uuid4
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Certificate, GenerationJob
from .schemas import CertificateResponse, GenerationJobResponse, GenerationRequest
from .services import process_job

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator API",
    version="1.0.0",
    description="Bulk certificate generation service for the Aereo SDE Intern assignment.",
)

def job_response(job: GenerationJob, db: Session) -> GenerationJobResponse:
    errors = [
        {
            "certificate_id": cert.id,
            "recipient_name": cert.recipient_name,
            "recipient_email": cert.recipient_email,
            "error": cert.error_message,
        }
        for cert in db.query(Certificate)
        .filter(Certificate.job_id == job.id, Certificate.status == "failed")
        .all()
    ]
    return GenerationJobResponse(
        job_id=job.id, status=job.status, total=job.total,
        processed=job.processed, successful=job.successful,
        failed=job.failed, errors=errors,
    )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/jobs", response_model=GenerationJobResponse, status_code=202)
def create_generation_job(request: GenerationRequest, background_tasks: BackgroundTasks,
                          db: Session = Depends(get_db)):
    job_id = str(uuid4())
    job = GenerationJob(
        id=job_id, event_name=request.event_name.strip(),
        course=request.course.strip(), issue_date=request.issue_date,
        status="queued", total=len(request.recipients),
    )
    db.add(job)

    for recipient in request.recipients:
        db.add(Certificate(
            id=str(uuid4()), job_id=job_id, recipient_name=recipient.name,
            recipient_email=str(recipient.email), course=request.course.strip(),
            issue_date=request.issue_date, status="pending",
        ))

    db.commit()
    db.refresh(job)
    background_tasks.add_task(process_job, job_id)
    return job_response(job, db)

@app.get("/api/v1/jobs/{job_id}", response_model=GenerationJobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return job_response(job, db)

@app.get("/api/v1/certificates", response_model=list[CertificateResponse])
def list_certificates(job_id: str | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Certificate)
    if job_id:
        query = query.filter(Certificate.job_id == job_id)
    return query.order_by(Certificate.created_at.desc()).all()

@app.get("/api/v1/certificates/{certificate_id}/download")
def download_certificate(certificate_id: str, db: Session = Depends(get_db)):
    certificate = db.get(Certificate, certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if certificate.status != "generated" or not certificate.file_path:
        raise HTTPException(status_code=409, detail="Certificate is not available yet")
    return FileResponse(certificate.file_path, media_type="application/pdf",
                        filename=f"certificate-{certificate.id}.pdf")
