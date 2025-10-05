# services/vector_db_manager.py
import chromadb
from chromadb.utils import embedding_functions
from typing import List
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

    def ingest_document_chunks(self, base_doc_id: str, chunks: List, metadata: dict):
        """
        Ingests a list of document chunks into the vector database.
        """
        if not chunks:
            logger.warning(f"No chunks provided for document ID {base_doc_id}. Skipping ingestion.")
            return

        try:
            # Create unique IDs and separate content/metadata for each chunk
            chunk_ids = [f"{base_doc_id}_chunk_{i}" for i in range(len(chunks))]
            chunk_documents = [chunk.page_content for chunk in chunks]
            
            # Add common metadata to each chunk's specific metadata
            chunk_metadatas = []
            for i, chunk in enumerate(chunks):
                # Start with the chunk's own metadata (like page number)
                chunk_meta = chunk.metadata.copy() 
                # Add the common metadata we passed in (like doc_type)
                chunk_meta.update(metadata) 
                chunk_metadatas.append(chunk_meta)

            self.collection.add(
                documents=chunk_documents,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            logger.info(f"Successfully ingested {len(chunks)} chunks for document ID: {base_doc_id}")
        except Exception as e:
            logger.error(f"Failed to ingest chunks for document {base_doc_id}: {e}")

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

