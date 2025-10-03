# ingest.py
import os
from services.document_processor import DocumentProcessor
from services.vector_db_manager import VectorDBManager
from config import logger, SOURCE_DOCS_DIR

def ingest_ground_truth():
    """
    Finds all PDF files in the source documents directory, extracts their text content,
    and ingests them into the ChromaDB vector database.
    """
    if not os.path.exists(SOURCE_DOCS_DIR):
        logger.error(f"Source documents directory not found: '{SOURCE_DOCS_DIR}'")
        logger.error("Please create this directory and add your PDF files (e.g., job_description.pdf, case_study_brief.pdf).")
        return

    processor = DocumentProcessor()
    db_manager = VectorDBManager()
    
    logger.info(f"Starting ingestion of ground truth documents from '{SOURCE_DOCS_DIR}'...")

    # Find all .pdf files in the data directory
    for filename in os.listdir(SOURCE_DOCS_DIR):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(SOURCE_DOCS_DIR, filename)
            
            # Use the DocumentProcessor to extract text from the PDF
            logger.info(f"Processing file: {filename}")
            content = processor.extract_text_from_pdf(file_path)

            if "Error:" in content or not content.strip():
                logger.warning(f"Skipping ingestion for {filename} due to extraction issues.")
                continue

            # Use the filename (without extension) as the document type
            doc_type = filename.lower().replace(".pdf", "")
            doc_id = f"ground_truth_{doc_type}"
            metadata = {"doc_type": doc_type, "source": filename}

            # Ingest the extracted text into the vector DB
            db_manager.ingest_document(
                document_id=doc_id,
                text=content,
                metadata=metadata
            )
    
    logger.info("Ground truth ingestion complete.")

if __name__ == "__main__":
    # Before running, make sure you have created the 'source_documents'
    # directory (or whatever you set in .env) and placed your PDF files inside it.
    ingest_ground_truth()
