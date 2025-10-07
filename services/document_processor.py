# services/document_processor.py
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import logger
from typing import List

class DocumentProcessor:
    """
    Handles loading, chunking, and text extraction from documents using LangChain.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initializes the DocumentProcessor with a text splitter.
        
        Args:
            chunk_size: The number of characters in each chunk.
            chunk_overlap: The number of characters to overlap between chunks.
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        logger.info(f"DocumentProcessor initialized with chunk_size={chunk_size} and chunk_overlap={chunk_overlap}")

    def load_and_chunk_pdf(self, file_path: str) -> List:
        """
        Loads a PDF and splits it into manageable chunks.
        This is used for ingesting documents into the vector DB.
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Successfully loaded and chunked {file_path} into {len(chunks)} chunks.")
            return chunks
        except Exception as e:
            logger.error(f"Failed to load or chunk PDF {file_path}: {e}")
            return []

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extracts the full, raw text from a PDF without chunking.
        This is used for getting the content of candidate-provided files for the LLM prompt.
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            full_text = "\n".join([doc.page_content for doc in documents])
            
            if not full_text:
                logger.warning(f"Could not extract text from {file_path}. The document might be an image.")
                return f"Content of document {file_path} could not be extracted (possibly image-based)."
            
            logger.info(f"Successfully extracted full text from {file_path}.")
            return full_text
        except Exception as e:
            logger.error(f"Failed to extract full text from PDF {file_path}: {e}")
            return f"Error: Could not process document at {file_path}."

