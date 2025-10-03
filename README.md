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
├── main.py                  # Main entry point
├── models.py                # Data models and schemas
├── requirements.txt         # Python dependencies
├── setup.sh                 # Setup script
├── chroma_db/               # Vector database files
├── docs/                    # Project documentation
├── ground_truth_docs/       # Job descriptions and scoring rubrics
├── services/                # Core service modules
│   ├── document_processor.py
│   ├── evaluation_service.py
│   ├── llm_provider.py
│   └── vector_db_manager.py
├── uploads/                 # Uploaded candidate documents
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
- Place candidate resumes and project files in the `uploads/` directory.
- Place job descriptions and rubrics in `ground_truth_docs/`.
- Use the main script or service endpoints to trigger evaluation.

## Folder Descriptions
- `services/`: Contains the main logic for document processing, evaluation, LLM integration, and vector DB management.
- `ground_truth_docs/`: Contains reference documents for evaluation (job descriptions, rubrics).
- `uploads/`: Stores candidate submissions.
- `chroma_db/`: Vector database files for semantic search.
- `docs/`: Additional documentation.

## Requirements
- Python 3.10+
- See `requirements.txt` for Python package dependencies.

## License
This project is for educational and demonstration purposes.
