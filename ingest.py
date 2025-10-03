# ingest.py
import os
from services.document_processor import DocumentProcessor
from services.vector_db_manager import VectorDBManager
from config import logger

# --- Create dummy documents for ingestion ---
# In a real scenario, these would be actual PDF files.
DATA_DIR = "ground_truth_docs"
os.makedirs(DATA_DIR, exist_ok=True)

docs_to_create = {
    "job_description.txt": (
        "Product Engineer (Backend). Key skills: Python, FastAPI, "
        "cloud tech (AWS/GCP), AI/LLM integration. Requires experience with RESTful APIs, "
        "databases (PostgreSQL/MongoDB), and async tasks. Strong problem-solving and "
        "communication skills are essential. Focus on clean, scalable code."
    ),
    "cv_scoring_rubric.txt": (
        "CV Scoring Rubric: Evaluate CV based on: 1. Technical Skills Match (Python, APIs, DBs, Cloud, AI/LLM), "
        "2. Experience Level (years, project complexity), 3. Relevant Achievements (impact, scale). "
        "Rate from 0.0 to 1.0. A strong candidate will show direct experience in building and scaling backend systems."
    ),
    "case_study_brief.txt": (
        "Case Study Brief: The project requires building a backend service with FastAPI for "
        "asynchronous job processing. Key components are API endpoints (/upload, /evaluate, /result), "
        "a RAG pipeline for evaluation, and robust error handling. The system must ingest documents into a vector DB."
    ),
    "project_scoring_rubric.txt": (
        "Project Scoring Rubric: Evaluate project on: 1. Correctness (meets all requirements like RAG and async), "
        "2. Code Quality (clean, modular, OOP), 3. Resilience (handles failures, retries). Score from 1.0 to 5.0. "
        "Bonus for clear documentation and design choices explained."
    )
}

for filename, content in docs_to_create.items():
    with open(os.path.join(DATA_DIR, filename), "w") as f:
        f.write(content)

logger.info(f"Created dummy documents in {DATA_DIR}")
# --- End of dummy document creation ---


def ingest_ground_truth():
    """
    Parses and ingests all ground truth documents into ChromaDB.
    """
    processor = DocumentProcessor()
    db_manager = VectorDBManager()
    
    logger.info("Starting ingestion of ground truth documents...")

    for filename in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.isfile(file_path):
            # For this script, we read text files. If they were PDFs, we'd use extract_text_from_pdf
            with open(file_path, "r") as f:
                content = f.read()

            doc_type = filename.replace(".txt", "")
            doc_id = f"ground_truth_{doc_type}"
            metadata = {"doc_type": doc_type, "source": filename}

            db_manager.ingest_document(
                document_id=doc_id,
                text=content,
                metadata=metadata
            )
    
    logger.info("Ground truth ingestion complete.")

if __name__ == "__main__":
    ingest_ground_truth()
