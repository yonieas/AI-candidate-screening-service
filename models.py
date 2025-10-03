# models.py
from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    cv_id: str
    report_id: str

class EvaluateRequest(BaseModel):
    job_title: str
    cv_id: str
    report_id: str

class JobStatus(BaseModel):
    id: str
    status: str

class EvaluationResult(BaseModel):
    cv_match_rate: float
    cv_feedback: str
    project_score: float
    project_feedback: str
    overall_summary: str

class JobResult(JobStatus):
    result: Optional[EvaluationResult] = None
