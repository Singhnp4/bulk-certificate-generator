from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db
from worker import process_job
import os

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Bulk Certificate Generator")

@app.post("/jobs/", response_model=schemas.JobResponse)
def create_job(job_req: schemas.JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job = models.Job(status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)
    for rec in job_req.recipients:
        cert = models.Certificate(job_id=job.id, recipient_name=rec.name, recipient_email=rec.email)
        db.add(cert)
    db.commit()
    db.refresh(job)
    background_tasks.add_task(process_job, job.id, db)
    return job

@app.get("/jobs/{job_id}", response_model=schemas.JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/certificates/{cert_id}/download")
def download_certificate(cert_id: int, db: Session = Depends(get_db)):
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
    if not cert or not cert.file_path or not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="Certificate not found or not ready")
    return FileResponse(cert.file_path, media_type="application/pdf", filename=f"{cert.recipient_name}_certificate.pdf")