# Bulk Certificate Generator API

This is a backend API built with FastAPI that accepts bulk certificate generation requests, processes them efficiently in the background, and allows clients to track the status and retrieve the generated PDF certificates.

## Setup Instructions

1. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   ```
2. **Activate the virtual environment:**
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## How to Run the Application

Start the FastAPI server using Uvicorn:

```bash
python -m uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. 
You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## How to Run Tests

To run the automated tests covering job creation, validation, failure handling, and file retrieval, run:

```bash
pytest test_main.py
```

## API Endpoints & Usage

### 1. Submit a certificate generation request
- **Endpoint:** `POST /jobs/`
- **Description:** Accepts a list of recipients and triggers background generation.
- **Request Body Example:**
  ```json
  {
    "recipients": [
      {
        "name": "Alice Smith",
        "email": "alice@example.com"
      },
      {
        "name": "Bob Jones",
        "email": "bob@example.com"
      }
    ]
  }
  ```

### 2. Check Job Status
- **Endpoint:** `GET /jobs/{job_id}`
- **Description:** Returns the status of the overall job (`pending`, `processing`, `completed`) along with the individual status of each certificate (`pending`, `success`, `failed`).

### 3. Retrieve Generated Certificates
- **Endpoint:** `GET /certificates/{cert_id}/download`
- **Description:** Downloads the generated PDF file for a specific certificate if it was processed successfully.

## Important Implementation & Design Decisions

### Bulk Processing & Asynchronous Execution
The API is designed to handle bulk requests where a single job might contain hundreds or thousands of recipients. To handle this efficiently:
- **BackgroundTasks:** Generation is handled via FastAPI's `BackgroundTasks`. When a client submits a job, the database records are created instantly, and the CPU-heavy PDF generation is sent to a background worker. 
- **Reasoning:** This asynchronous approach ensures the main thread is not blocked. The client receives an immediate `200 OK` response with a `job_id` rather than waiting for potentially long PDF rendering times.

### Partial Failure Handling
- Inside the background worker, the PDF generation for the job is wrapped in a loop where *each individual certificate* gets its own `try...except` block. 
- **Reasoning:** If one certificate fails (e.g., due to an invalid character crashing the PDF canvas), the exception is caught, that specific certificate is marked as `failed` with an `error_message`, and the loop safely continues. This guarantees that one bad input does not ruin the entire bulk batch.

### Input Validation
- Relies on Pydantic models (`schemas.py`) to enforce data integrity before the application even touches the database. For example, `EmailStr` strictly ensures that every provided email is formatted correctly.