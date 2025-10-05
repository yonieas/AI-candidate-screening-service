# services/evaluation_service.py
from typing import Dict, Any
from .llm_provider import LLMProvider
from .vector_db_manager import VectorDBManager
from .document_processor import DocumentProcessor
from config import logger

# --- ADDED CODE: Define the scoring weights from the rubric ---
CV_WEIGHTS = {
    "technical_skills": 0.40,
    "experience_level": 0.25,
    "relevant_achievements": 0.20,
    "cultural_fit": 0.15
}

PROJECT_WEIGHTS = {
    "correctness": 0.30,
    "code_quality": 0.25,
    "resilience": 0.20,
    "documentation": 0.15,
    "creativity": 0.10
}
# --- END ADDED CODE ---


class AIEvaluationService:
    """
    Orchestrates the entire RAG and evaluation pipeline.
    """
    def __init__(self, llm_provider: LLMProvider, db_manager: VectorDBManager, doc_processor: DocumentProcessor):
        self.llm = llm_provider
        self.db = db_manager
        self.processor = doc_processor
        logger.info("AI Evaluation Service initialized.")

    def _get_document_content(self, file_path: str) -> str:
        """Helper to get text content from a file path."""
        if not file_path:
            return "Error: Document path not found."
        return self.processor.extract_text_from_pdf(file_path)

    # --- ADDED CODE: Helper function for weighted average calculation ---
    def _calculate_weighted_average(self, scores: dict, weights: dict) -> float:
        """Calculates the weighted average for a set of scores."""
        total_score = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0
        return total_score / total_weight
    # --- END ADDED CODE ---

    async def evaluate_candidate(self, cv_path: str, report_path: str, job_title: str) -> Dict[str, Any]:
        """
        Orchestrates the multi-step evaluation process using RAG.
        """
        cv_content = self._get_document_content(cv_path)
        report_content = self._get_document_content(report_path)

        # 1. CV Evaluation using RAG
        job_desc_context = self.db.query(job_title, doc_type="job_description")
        # --- MODIFIED LINE: Query the single, combined rubric document ---
        cv_rubric_context = self.db.query("cv scoring", doc_type="scoring_rubric")
        
        # --- MODIFIED PROMPT: Ask for detailed scores ---
        cv_prompt = f"""
        **Context:**
        - Job Description Context: {job_desc_context}
        - CV Scoring Rubric: {cv_rubric_context}

        **Candidate CV Content:**
        {cv_content}

        **Task:**
        Evaluate the CV against the rubric. Provide ONLY a JSON object with a score (1-5) for each parameter and a brief feedback summary.
        The keys must be: "technical_skills", "experience_level", "relevant_achievements", "cultural_fit", and "cv_feedback".
        
        Example JSON:
        {{
            "technical_skills": 4,
            "experience_level": 5,
            "relevant_achievements": 3,
            "cultural_fit": 4,
            "cv_feedback": "Strong in backend and cloud, limited AI integration experience..."
        }}
        """
        cv_result_str = await self.llm.generate_text_async(cv_prompt)
        cv_detailed_scores = self.llm.safe_json_loads(cv_result_str)

        # --- ADDED CODE: Perform the calculation in Python ---
        cv_weighted_avg_1_5 = self._calculate_weighted_average(cv_detailed_scores, CV_WEIGHTS)
        # Convert the 1-5 score to the required 0-1 decimal format
        final_cv_match_rate = round(cv_weighted_avg_1_5 * 0.2, 2)
        # --- END ADDED CODE ---

        # 2. Project Report Evaluation using RAG
        case_brief_context = self.db.query("case study brief", doc_type="case_study_brief")
        # --- MODIFIED LINE: Query the single, combined rubric document ---
        project_rubric_context = self.db.query("project rubric", doc_type="scoring_rubric")

        # --- MODIFIED PROMPT: Ask for detailed scores ---
        project_prompt = f"""
        **Context:**
        - Case Study Brief: {case_brief_context}
        - Project Scoring Rubric: {project_rubric_context}

        **Candidate Project Report Content:**
        {report_content}

        **Task:**
        Evaluate the project report against the rubric. Provide ONLY a JSON object with a score (1-5) for each parameter and a brief feedback summary.
        The keys must be: "correctness", "code_quality", "resilience", "documentation", "creativity", and "project_feedback".
        
        Example JSON:
        {{
            "correctness": 5,
            "code_quality": 4,
            "resilience": 3,
            "documentation": 5,
            "creativity": 2,
            "project_feedback": "Meets prompt chaining requirements, lacks error handling robustness..."
        }}
        """
        project_result_str = await self.llm.generate_text_async(project_prompt)
        project_detailed_scores = self.llm.safe_json_loads(project_result_str)

        # --- ADDED CODE: Perform the calculation in Python ---
        final_project_score = round(self._calculate_weighted_average(project_detailed_scores, PROJECT_WEIGHTS), 2)
        # --- END ADDED CODE ---

        # 3. Final Summary
        summary_prompt = f"""
        **CV Evaluation:**
        - Match Rate: {final_cv_match_rate}
        - Feedback: {cv_detailed_scores.get('cv_feedback', '')}

        **Project Evaluation:**
        - Score: {final_project_score}
        - Feedback: {project_detailed_scores.get('project_feedback', '')}

        **Task:**
        Synthesize all the information into a concise overall summary (30-40 words) for the hiring manager.
        """
        overall_summary = await self.llm.generate_text_async(summary_prompt)

        # --- MODIFIED RETURN: Use the calculated scores ---
        return {
            "cv_match_rate": final_cv_match_rate,
            "cv_feedback": cv_detailed_scores.get('cv_feedback', 'No feedback generated.'),
            "project_score": final_project_score,
            "project_feedback": project_detailed_scores.get('project_feedback', 'No feedback generated.'),
            "overall_summary": overall_summary.strip()
        }

'''
### Instructions for This to Work

1.  **File Naming:** In your `source_documents` directory, make sure your single rubric PDF is named **`scoring_rubric.pdf`**. This is important because the ingestion script uses the filename to create the `doc_type`.
2.  **Re-Ingest Data:** After placing the file, you must run the ingestion script again to update the vector database:
    ```bash
    python ingest.py
'''