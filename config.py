# config.py
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# --- Logging Configuration (Setup early to catch logs from other initializations) ---
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
# Safely get the logging level from the string (e.g., "INFO" -> logging.INFO)
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info(f"Logger configured with level: {LOG_LEVEL_STR}")

# --- File Path Configurations ---
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
DB_PATH = os.getenv("DB_PATH", "chroma_db")
SOURCE_DOCS_DIR = os.getenv("SOURCE_DOCS_DIR", "source_documents")

# --- DB & Model Name Configurations ---
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "job_screening_docs")
GENERATIVE_MODEL_NAME = os.getenv("GENERATIVE_MODEL_NAME", "gemini-2.5-flash")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

# --- Algorithmic Tuning Parameters (loaded from .env) ---
# We use `float` and `int` to cast the string values from the .env file
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.1))
LLM_RETRIES = int(os.getenv("LLM_RETRIES", 3))
LLM_RETRY_DELAY = int(os.getenv("LLM_RETRY_DELAY", 5))
RAG_NUM_RESULTS = int(os.getenv("RAG_NUM_RESULTS", 2))


# --- Gemini API Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set!")

genai.configure(api_key=GEMINI_API_KEY)


# --- Ensure Core Directories Exist ---
os.makedirs(UPLOAD_DIR, exist_ok=True)

