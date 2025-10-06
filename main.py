# main.py
import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from typing import Dict, Any

from config import UPLOAD_DIR, logger
from models import UploadResponse, EvaluateRequest, JobStatus, JobResult, EvaluationResult

# --- Import Core AI Services ---
from services.llm_provider import LLMProvider
from services.vector_db_manager import VectorDBManager
from services.document_processor import DocumentProcessor
from services.evaluation_service import AIEvaluationService

# --- FastAPI Application Setup ---
app = FastAPI(
    title="AI Candidate Screening Service",
    description="An API to automate the initial screening of job applications using GenAI."
)

# --- Initialize Services (Dependency Injection) ---
try:
    llm_provider = LLMProvider()
    db_manager = VectorDBManager()
    doc_processor = DocumentProcessor()
    ai_evaluator = AIEvaluationService(llm_provider, db_manager, doc_processor)
except Exception as e:
    logger.critical(f"Fatal error during service initialization: {e}")
    # In a real app, you might not want to start the server if core services fail
    ai_evaluator = None 


# --- In-Memory Storage (for simplicity; use Redis/Celery in production) ---
jobs: Dict[str, Dict[str, Any]] = {}
uploaded_files: Dict[str, str] = {}
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _rebuild_file_map_on_startup():
    """
    Scans the UPLOAD_DIR and rebuilds the in-memory 'uploaded_files'
    dictionary to persist across server restarts.
    """
    if not os.path.exists(UPLOAD_DIR):
        return
    
    logger.info("Rebuilding file map from disk...")
    count = 0
    for filename in os.listdir(UPLOAD_DIR):
        # Filenames are in the format: {uuid}_{original_filename}.pdf
        try:
            file_id = filename.split('_')[0]
            # Validate that it's a UUID to avoid other stray files
            uuid.UUID(file_id) 
            file_path = os.path.join(UPLOAD_DIR, filename)
            uploaded_files[file_id] = file_path
            count += 1
        except (IndexError, ValueError):
            logger.warning(f"Skipping file with unexpected format: {filename}")
    logger.info(f"Rebuilt file map with {count} items.")

@app.on_event("startup")
async def startup_event():
    _rebuild_file_map_on_startup()

# --- Background Task for Evaluation ---
async def run_evaluation_task(job_id: str, cv_id: str, report_id: str, job_title: str):
    """The actual async task that runs the AI evaluation."""
    if not ai_evaluator:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = {"error": "AI Evaluation Service not available."}
        return

    try:
        jobs[job_id]["status"] = "processing"
        logger.info(f"Starting evaluation for job {job_id}.")
        
        cv_path = uploaded_files.get(cv_id)
        report_path = uploaded_files.get(report_id)

        result = await ai_evaluator.evaluate_candidate(cv_path, report_path, job_title)
        jobs[job_id]["result"] = result
        jobs[job_id]["status"] = "completed"
        logger.info(f"Evaluation for job {job_id} completed successfully.")
    except Exception as e:
        logger.error(f"Evaluation for job {job_id} failed: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = {"error": str(e)}


# --- API Endpoints ---
@app.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_files(cv: UploadFile = File(...), project_report: UploadFile = File(...)):
    """
    Accepts a candidate's CV and Project Report files.
    Stores the files and returns unique IDs for each.
    """
    try:
        cv_id = str(uuid.uuid4())
        cv_path = os.path.join(UPLOAD_DIR, f"{cv_id}_{cv.filename}")
        with open(cv_path, "wb") as buffer:
            buffer.write(await cv.read())
        uploaded_files[cv_id] = cv_path

        report_id = str(uuid.uuid4())
        report_path = os.path.join(UPLOAD_DIR, f"{report_id}_{project_report.filename}")
        with open(report_path, "wb") as buffer:
            buffer.write(await project_report.read())
        uploaded_files[report_id] = report_path

        return {"cv_id": cv_id, "report_id": report_id}
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during file upload.")

@app.post("/evaluate", response_model=JobStatus, status_code=202)
def evaluate(request: EvaluateRequest, background_tasks: BackgroundTasks):
    """
    Triggers the asynchronous AI evaluation pipeline.
    Immediately returns a job ID to track the process.
    """
    if request.cv_id not in uploaded_files or request.report_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="One or both document IDs not found.")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"id": job_id, "status": "queued", "result": None}

    background_tasks.add_task(
        run_evaluation_task,
        job_id,
        request.cv_id,
        request.report_id,
        request.job_title
    )

    logger.info(f"Job {job_id} queued for evaluation.")
    return jobs[job_id]

@app.get("/result/{job_id}", response_model=JobResult)
def get_result(job_id: str):
    """
    Retrieves the status and result of an evaluation job.
    """
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    # When using Pydantic V2, model validation happens on return.
    # We need to handle the case where a failed job's result is an error dict.
    if job.get("status") == "failed":
        # The response model allows result to be None, but not a dict with 'error'.
        # We create a valid JobResult structure for failed tasks.
        return JobResult(id=job["id"], status="failed", result=None)

    return job

@app.get("/", include_in_schema=False)
def root():
    return {"message": "AI Candidate Screening Service is running."}
