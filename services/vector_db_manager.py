# services/vector_db_manager.py
import chromadb
from chromadb.utils import embedding_functions
from config import DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL_NAME, logger

class VectorDBManager:
    """Manages all interactions with the ChromaDB vector database."""

    def __init__(self):
        """Initializes the ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(path=DB_PATH)
            
            # Using a sentence-transformer model for creating embeddings locally
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=EMBEDDING_MODEL_NAME
            )
            
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"} # Using cosine distance for similarity
            )
            logger.info("ChromaDB client initialized and collection loaded.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def ingest_document(self, document_id: str, text: str, metadata: dict):
        """
        Ingests a document's text into the vector database.
        ChromaDB handles chunking and embedding internally.
        """
        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[document_id]
            )
            logger.info(f"Successfully ingested document with ID: {document_id}")
        except Exception as e:
            logger.error(f"Failed to ingest document {document_id}: {e}")

    def query(self, query_text: str, n_results: int = 2, doc_type: str = "all") -> str:
        """
        Queries the vector database to find relevant document chunks.
        
        Args:
            query_text: The text to search for.
            n_results: The number of results to return.
            doc_type: Filter by document type (e.g., 'job_description', 'rubric').
        
        Returns:
            A string containing the concatenated context of the retrieved documents.
        """
        try:
            where_clause = {}
            if doc_type != "all":
                where_clause = {"doc_type": doc_type}

            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_clause
            )
            
            context = "\n---\n".join(results['documents'][0])
            logger.info(f"Query successful for doc_type '{doc_type}'. Retrieved context.")
            return context
        except Exception as e:
            logger.error(f"Failed to query ChromaDB for doc_type '{doc_type}': {e}")
            return "Error: Could not retrieve context from the knowledge base."
