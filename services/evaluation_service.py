# services/evaluation_service.py
import json
from typing import Dict, Any
from .llm_provider import LLMProvider
from .vector_db_manager import VectorDBManager
from .document_processor import DocumentProcessor
from config import logger

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

    async def evaluate_candidate(self, cv_path: str, report_path: str, job_title: str) -> Dict[str, Any]:
        """
        Orchestrates the multi-step evaluation process using RAG.
        """
        cv_content = self._get_document_content(cv_path)
        report_content = self._get_document_content(report_path)

        # 1. CV Evaluation using RAG
        job_desc_context = self.db.query(job_title, doc_type="job_description")
        cv_rubric_context = self.db.query("cv scoring", doc_type="cv_scoring_rubric")
        
        cv_prompt = f"""
        **Context:**
        - Job Description Context: {job_desc_context}
        - CV Scoring Rubric: {cv_rubric_context}

        **Candidate CV Content:**
        {cv_content}

        **Task:**
        Evaluate the CV against the job description and rubric. Provide ONLY a JSON object with two keys:
        1. "cv_match_rate": A float between 0.0 and 1.0.
        2. "cv_feedback": A brief string (20-30 words) summarizing strengths and weaknesses.
        """
        cv_result_str = await self.llm.generate_text_async(cv_prompt)
        cv_result = self.llm.safe_json_loads(cv_result_str)

        # 2. Project Report Evaluation using RAG
        case_brief_context = self.db.query("case study brief", doc_type="case_study_brief")
        project_rubric_context = self.db.query("project rubric", doc_type="project_scoring_rubric")

        project_prompt = f"""
        **Context:**
        - Case Study Brief: {case_brief_context}
        - Project Scoring Rubric: {project_rubric_context}

        **Candidate Project Report Content:**
        {report_content}

        **Task:**
        Evaluate the project report against the case study brief and rubric. Provide ONLY a JSON object with two keys:
        1. "project_score": A float between 1.0 and 5.0.
        2. "project_feedback": A brief string (20-30 words) on correctness and code quality.
        """
        project_result_str = await self.llm.generate_text_async(project_prompt)
        project_result = self.llm.safe_json_loads(project_result_str)

        # 3. Final Summary
        summary_prompt = f"""
        **CV Evaluation:**
        - Match Rate: {cv_result['cv_match_rate']}
        - Feedback: {cv_result['cv_feedback']}

        **Project Evaluation:**
        - Score: {project_result['project_score']}
        - Feedback: {project_result['project_feedback']}

        **Task:**
        Synthesize all the information into a concise overall summary (30-40 words) for the hiring manager.
        """
        overall_summary = await self.llm.generate_text_async(summary_prompt)

        return {
            "cv_match_rate": cv_result['cv_match_rate'],
            "cv_feedback": cv_result['cv_feedback'],
            "project_score": project_result['project_score'],
            "project_feedback": project_result['project_feedback'],
            "overall_summary": overall_summary.strip()
        }
