from fastapi.testclient import TestClient
from main import app
from database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_create_and_fetch_job():
    payload = {"recipients": [{"name": "John Doe", "email": "john@example.com"}, {"name": "error", "email": "err@example.com"}]}
    response = client.post("/jobs/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    job_id = data["id"]
    assert len(data["certificates"]) == 2
    resp2 = client.get(f"/jobs/{job_id}")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "completed"
    success_cert = next(c for c in data2["certificates"] if c["recipient_name"] == "John Doe")
    assert success_cert["status"] == "success"
    err_cert = next(c for c in data2["certificates"] if c["recipient_name"] == "error")
    assert err_cert["status"] == "failed"
    resp3 = client.get(f"/certificates/{success_cert['id']}/download")
    assert resp3.status_code == 200
    assert resp3.headers["content-type"] == "application/pdf"