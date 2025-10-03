import chromadb
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

ids_str = os.getenv("IDS", "ground_truth_job description")
ids = [i.strip() for i in ids_str.split(",") if i.strip()]

client = chromadb.PersistentClient(path=os.getenv("DB_PATH", "chroma_db"))
collection = client.get_or_create_collection(name=os.getenv("COLLECTION_NAME", "job_screening_docs"))

results = collection.get(ids=ids)
print(json.dumps(results, indent=2, ensure_ascii=False))