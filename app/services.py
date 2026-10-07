from pathlib import Path
from .certificate import generate_certificate
from .models import Certificate

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "generated_certificates"

def process_job(job_id: str) -> None:
    from .database import SessionLocal
    from .models import GenerationJob

    db = SessionLocal()
    try:
        job = db.get(GenerationJob, job_id)
        if not job:
            return

        job.status = "processing"
        db.commit()

        certificates = (
            db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .order_by(Certificate.created_at)
            .all()
        )

        for certificate in certificates:
            try:
                path = generate_certificate(
                    OUTPUT_DIR, certificate.id, certificate.recipient_name,
                    certificate.course, job.event_name, certificate.issue_date
                )
                certificate.status = "generated"
                certificate.file_path = str(path)
                job.successful += 1
            except Exception as exc:
                certificate.status = "failed"
                certificate.error_message = str(exc)
                job.failed += 1
            finally:
                job.processed += 1
                db.commit()

        job.status = "completed_with_errors" if job.failed else "completed"
        db.commit()
    except Exception:
        job.status = "failed"
        db.commit()
    finally:
        db.close()
