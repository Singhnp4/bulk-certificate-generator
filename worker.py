import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from sqlalchemy.orm import Session
from models import Job, Certificate

CERT_DIR = "generated_certs"
os.makedirs(CERT_DIR, exist_ok=True)

def generate_pdf(name: str, filename: str):
    if name.lower() == "error":
        raise Exception("Simulated generation error")
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 500, "Certificate of Completion")
    c.drawString(100, 450, f"Awarded to: {name}")
    c.save()

def process_job(job_id: int, db: Session):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return
    job.status = "processing"
    db.commit()
    for cert in job.certificates:
        try:
            filename = os.path.join(CERT_DIR, f"cert_{cert.id}.pdf")
            generate_pdf(cert.recipient_name, filename)
            cert.status = "success"
            cert.file_path = filename
        except Exception as e:
            cert.status = "failed"
            cert.error_message = str(e)
        db.commit()
    job.status = "completed"
    db.commit()