# services/vector_db_manager.py
import chromadb
from chromadb.utils import embedding_functions
from config import DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL_NAME, logger, RAG_NUM_RESULTS

class VectorDBManager:
    """Manages all interactions with the ChromaDB vector database."""

    def __init__(self):
        """Initializes the ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(path=DB_PATH)
            
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=EMBEDDING_MODEL_NAME
            )
            
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB client initialized and collection loaded.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def ingest_document(self, document_id: str, text: str, metadata: dict):
        """
        Ingests a document's text into the vector database.
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

    def query(self, query_text: str, doc_type: str = "all") -> str:
        """
        Queries the vector database to find relevant document chunks.
        """
        try:
            where_clause = {}
            if doc_type != "all":
                where_clause = {"doc_type": doc_type}

            results = self.collection.query(
                query_texts=[query_text],
                n_results=RAG_NUM_RESULTS, # Using the configured value
                where=where_clause
            )
            
            context = "\n---\n".join(results['documents'][0])
            logger.info(f"Query successful for doc_type '{doc_type}'. Retrieved context.")
            return context
        except Exception as e:
            logger.error(f"Failed to query ChromaDB for doc_type '{doc_type}': {e}")
            return "Error: Could not retrieve context from the knowledge base."

