# services/database_service.py
import sqlite3
import json
from typing import Dict, Any, List, Optional
from config import logger, DATABASE_FILE
class DatabaseService:
    """Handles all database operations for storing and retrieving job results."""

    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self.conn = None

    def connect(self):
        """Establish a database connection."""
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Successfully connected to database: {self.db_file}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed.")

    def init_db(self):
        """Initializes the database and creates the 'jobs' table if it doesn't exist."""
        if not self.conn:
            self.connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    result TEXT 
                );
            """)
            self.conn.commit()
            logger.info("Database initialized and 'jobs' table is ready.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database table: {e}")

    def save_job(self, job_data: Dict[str, Any]):
        """Saves or updates a job's status and result in the database."""
        if not self.conn:
            self.connect()
        
        # The result dictionary is stored as a JSON string
        result_json = json.dumps(job_data.get("result")) if job_data.get("result") else None
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO jobs (id, status, result) VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status=excluded.status,
                    result=excluded.result;
            """, (job_data["id"], job_data["status"], result_json))
            self.conn.commit()
            logger.info(f"Successfully saved job {job_data['id']} to the database.")
        except sqlite3.Error as e:
            logger.error(f"Error saving job {job_data['id']}: {e}")

    def load_all_jobs_to_memory(self) -> Dict[str, Dict[str, Any]]:
        """Loads all jobs from the database into an in-memory dictionary on startup."""
        if not self.conn:
            self.connect()
        
        jobs_map = {}
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM jobs;")
            rows = cursor.fetchall()
            for row in rows:
                job_id = row['id']
                result_data = json.loads(row['result']) if row['result'] else None
                jobs_map[job_id] = {
                    "id": job_id,
                    "status": row['status'],
                    "result": result_data
                }
            logger.info(f"Loaded {len(jobs_map)} jobs from database into memory.")
            return jobs_map
        except sqlite3.Error as e:
            logger.error(f"Error loading jobs from database: {e}")
            return {}

    def get_all_completed_jobs(self) -> List[Dict[str, Any]]:
        """Retrieves all jobs with a 'completed' status from the database."""
        if not self.conn:
            self.connect()
        
        completed_jobs = []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE status = 'completed';")
            rows = cursor.fetchall()
            for row in rows:
                completed_jobs.append({
                    "id": row['id'],
                    "status": row['status'],
                    "result": json.loads(row['result']) if row['result'] else None
                })
            return completed_jobs
        except sqlite3.Error as e:
            logger.error(f"Error fetching completed jobs: {e}")
            return []
