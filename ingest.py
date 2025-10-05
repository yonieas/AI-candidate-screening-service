# ingest.py
import os
from services.document_processor import DocumentProcessor
from services.vector_db_manager import VectorDBManager
from config import logger, SOURCE_DOCS_DIR

def ingest_ground_truth():
    """
    Finds all PDF files in the source documents directory, chunks them,
    and ingests the chunks into the ChromaDB vector database.
    """
    if not os.path.exists(SOURCE_DOCS_DIR):
        logger.error(f"Source documents directory not found: '{SOURCE_DOCS_DIR}'")
        logger.error("Please create this directory and add your PDF files (e.g., job_description.pdf, scoring_rubric.pdf).")
        return

    processor = DocumentProcessor()
    db_manager = VectorDBManager()
    
    logger.info(f"Starting ingestion of ground truth documents from '{SOURCE_DOCS_DIR}'...")

    for filename in os.listdir(SOURCE_DOCS_DIR):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(SOURCE_DOCS_DIR, filename)
            
            logger.info(f"Processing file: {filename}")
            # --- MODIFIED LINE: Use the new chunking method ---
            chunks = processor.load_and_chunk_pdf(file_path)
            logger.info(f"Chunked {filename} into {len(chunks)} chunks.")
            logger.info(f"Chunks metadata sample: {chunks[0].metadata if chunks else 'No chunks'}")

            if not chunks:
                logger.warning(f"Skipping ingestion for {filename} due to chunking issues.")
                continue

            doc_type = filename.lower().replace(".pdf", "")
            doc_id_base = f"ground_truth_{doc_type}"
            metadata = {"doc_type": doc_type, "source": filename}

            # --- MODIFIED LINE: Use the new ingestion method for chunks ---
            db_manager.ingest_document_chunks(
                base_doc_id=doc_id_base,
                chunks=chunks,
                metadata=metadata
            )
    
    logger.info("Ground truth ingestion complete.")

if __name__ == "__main__":
    ingest_ground_truth()

