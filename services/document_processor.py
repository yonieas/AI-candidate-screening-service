# services/document_processor.py
import pypdf
from config import logger

class DocumentProcessor:
    """Handles parsing and text extraction from documents."""

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extracts text content from a given PDF file.
        """
        try:
            with open(file_path, "rb") as pdf_file:
                reader = pypdf.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                
                if not text:
                    logger.warning(f"Could not extract text from {file_path}. The document might be an image.")
                    return f"Content of document {file_path} could not be extracted (possibly image-based)."
                    
                logger.info(f"Successfully extracted text from {file_path}.")
                return text
        except Exception as e:
            logger.error(f"Failed to read or parse PDF {file_path}: {e}")
            return f"Error: Could not process document at {file_path}."
