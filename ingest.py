# ingest.py
import os
from services.document_processor import DocumentProcessor
from services.vector_db_manager import VectorDBManager
from config import logger, SOURCE_DOCS_DIR

# --- ADD THIS SET of required document types ---
# These are the doc_types the system needs to function correctly.
REQUIRED_DOC_TYPES = {
    "job_description",
    "scoring_rubric",
    "case_study_brief"
}

# Maps keywords found in filenames to the official doc_type the system uses.
DOC_TYPE_MAP = {
    "job_description": "job_description",
    "job description": "job_description",
    "jd": "job_description",
    "scoring_rubric": "scoring_rubric",
    "rubric": "scoring_rubric",
    "scoring": "scoring_rubric",
    "case_study_brief": "case_study_brief",
    "case_study": "case_study_brief",
    "brief": "case_study_brief",
}

def get_doc_type_from_filename(filename: str) -> str | None:
    """Finds the correct doc_type by checking for keywords in the filename."""
    fn_lower = filename.lower()
    for keyword, doc_type in DOC_TYPE_MAP.items():
        if keyword in fn_lower:
            return doc_type
    return None

def ingest_ground_truth():
    """
    Finds all PDF files, validates their type, chunks them, and ingests them.
    Raises an error if any of the required document types are missing.
    """
    if not os.path.exists(SOURCE_DOCS_DIR):
        # --- MODIFIED: Raise an error if the directory itself is missing ---
        error_msg = f"Source documents directory not found: '{SOURCE_DOCS_DIR}'. Please create it and add your PDFs."
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    processor = DocumentProcessor()
    db_manager = VectorDBManager()
    
    logger.info(f"Starting ingestion of ground truth documents from '{SOURCE_DOCS_DIR}'...")
    
    # --- ADDED: A set to track which document types we find ---
    found_doc_types = set()

    all_files = os.listdir(SOURCE_DOCS_DIR)
    pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]

    if not pdf_files:
        error_msg = f"No PDF files found in the '{SOURCE_DOCS_DIR}' directory."
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    for filename in pdf_files:
        doc_type = get_doc_type_from_filename(filename)

        if not doc_type:
            # --- MODIFIED: Provide a more helpful warning message ---
            logger.warning(
                f"Could not determine document type for '{filename}'. Skipping file. "
                f"Please ensure the filename contains a keyword like 'job_description', 'rubric', or 'case_study'."
            )
            continue
        
        logger.info(f"Processing file: {filename} as doc_type: '{doc_type}'")
        found_doc_types.add(doc_type) # Track the found type
        
        file_path = os.path.join(SOURCE_DOCS_DIR, filename)
        chunks = processor.load_and_chunk_pdf(file_path)

        if not chunks:
            logger.warning(f"Skipping ingestion for {filename} due to chunking issues.")
            continue

        doc_id_base = f"ground_truth_{doc_type}"
        metadata = {"doc_type": doc_type, "source": filename}

        db_manager.ingest_document_chunks(
            base_doc_id=doc_id_base,
            chunks=chunks,
            metadata=metadata
        )
    
    # --- ADDED VALIDATION BLOCK: Check if all required documents were found ---
    missing_docs = REQUIRED_DOC_TYPES - found_doc_types
    if missing_docs:
        error_msg = (
            f"Ingestion failed. Required document types are missing: {list(missing_docs)}. "
            f"Please add a PDF file for each missing type to the '{SOURCE_DOCS_DIR}' directory."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info("Ingestion complete. All required document types were found and processed.")

if __name__ == "__main__":
    try:
        ingest_ground_truth()
    except (FileNotFoundError, ValueError) as e:
        print(f"\nFATAL ERROR: {e}")

