# AI Candidate Screening Service

This project is an AI-powered candidate screening service designed to automate and enhance the process of evaluating job applicants. It leverages document processing, large language models (LLMs), and vector databases to assess candidate resumes and project submissions against job descriptions and scoring rubrics.

## Features
- **Resume and Project Evaluation**: Automatically scores candidate resumes and project submissions using customizable rubrics.
- **Document Ingestion**: Supports uploading and processing of various document types (PDF, TXT, etc.).
- **LLM Integration**: Utilizes LLMs for semantic analysis and scoring.
- **Vector Database**: Stores and retrieves document embeddings for efficient similarity search.
- **Modular Services**: Clean separation of concerns via service modules (document processing, evaluation, LLM provider, vector DB manager).

## Project Structure
```
├── config.py                # Configuration settings
├── ingest.py                # Document ingestion script
├── main.py                  # Main FastAPI entry point
├── models.py                # Data models and schemas
├── requirements.txt         # Python dependencies
├── setup.sh                 # Setup script
├── chroma_db/               # Vector database files (ChromaDB)
├── docs/                    # Project documentation
├── source_documents/        # Job descriptions, scoring rubrics, and case study briefs (PDFs)
├── services/                # Core service modules
│   ├── document_processor.py
│   ├── evaluation_service.py
│   ├── llm_provider.py
│   └── vector_db_manager.py
├── uploads/                 # Uploaded candidate documents
├── check_db.py              # Utility to check DB contents
├── .env                     # Environment variables (API keys, DB paths, etc.)
├── venv/                    # Python virtual environment (optional, not tracked)
```

## Setup Instructions
1. **Clone the repository**
   ```zsh
   git clone <repo-url>
   cd AI-candidate-screening-service
   ```
2. **Install dependencies**
   ```zsh
   pip install -r requirements.txt
   ```
3. **Run setup script (if needed)**
   ```zsh
   ./setup.sh
   ```
4. **Start the service**
   ```zsh
   uvicorn main:app --reload
   ```


## Usage

- Place job descriptions, scoring rubrics, and case study briefs in the `source_documents/` directory as PDFs.
- Use the main script or service endpoints to trigger evaluation.

### Ingestion and Data Refresh
- If you update or add files in `source_documents/` (e.g., a new or updated `Scoring_Rubric.pdf`), you **must re-run the ingestion script** to update the vector database:
   ```zsh
   python ingest.py
   ```
   This ensures the latest documents are available for retrieval-augmented generation (RAG) and evaluation.

### Environment Variables
- Copy `.env.example` to `.env` and fill in required values (API keys, DB paths, etc.).
- Key variables:
   - `GEMINI_API_KEY`: Your LLM API key
   - `DB_PATH`: Path to ChromaDB directory (default: `chroma_db`)
   - `COLLECTION_NAME`: Name of the ChromaDB collection (default: `job_screening_docs`)
   - `UPLOAD_DIR`: Where candidate files are uploaded (default: `uploads`)
   - `SOURCE_DOCS_DIR`: Where source/reference PDFs are stored (default: `source_documents`)
   - `EMBEDDING_MODEL_NAME`, `GENERATIVE_MODEL_NAME`: Model names for embeddings and LLM


## Folder Descriptions
- `services/`: Main logic for document processing, evaluation, LLM integration, and vector DB management
- `source_documents/`: Reference documents for evaluation (job descriptions, scoring rubrics, case study briefs)
- `uploads/`: Stores candidate submissions (resumes, project reports)
- `chroma_db/`: Vector database files for semantic search (ChromaDB)
- `docs/`: Additional documentation
- `.env`: Environment variables for configuration
- `check_db.py`: Utility to inspect DB contents

## Important
- **File Naming:** In `source_documents/`, make sure your single rubric PDF is named `Scoring_Rubric.pdf` (case-sensitive). The ingestion script uses the filename to create the `doc_type`.
- **Re-Ingest Data:** After placing or updating files, always re-run `python ingest.py` to refresh the vector DB.

## Requirements
- Python 3.12+
- See `requirements.txt` for Python package dependencies.

## License
This project is for educational and demonstration purposes.
