"""
Matching Service - Integrates existing skill matcher and RAG retriever
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analysis.skill_matcher import SkillMatcher
from src.vectorstore.embeddings import EmbeddingService
from src.vectorstore.vector_db import VectorStore
from src.rag.retriever import RAGRetriever
from src.models import Resume, JobDescription


class MatchingService:
    """Service layer for resume-JD matching using skill matcher and RAG"""

    def __init__(self):
        self.skill_matcher = SkillMatcher()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.rag_retriever = RAGRetriever(self.embedding_service, self.vector_store)

    def calculate_match_score(
        self,
        resume: Resume,
        job_description: JobDescription
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive match score between resume and JD

        Args:
            resume: Parsed resume object
            job_description: Parsed JD object

        Returns:
            Dictionary with match scores and analysis
        """
        # Extract resume skills as a list of strings
        resume_skills = []
        if hasattr(resume, 'skills') and resume.skills:
            if isinstance(resume.skills, list):
                resume_skills = [str(s) for s in resume.skills if s]

        print(f"[MATCHING DEBUG] Resume skills type: {type(resume.skills) if hasattr(resume, 'skills') else 'None'}")
        print(f"[MATCHING DEBUG] Resume skills raw: {resume.skills if hasattr(resume, 'skills') else 'None'}")
        print(f"[MATCHING DEBUG] Resume skills extracted: {resume_skills}")
        print(f"[MATCHING DEBUG] Number of resume skills: {len(resume_skills)}")

        # Combine all experience text
        experience_text = ""
        if hasattr(resume, 'experience') and resume.experience:
            for exp in resume.experience:
                if hasattr(exp, 'bullets') and exp.bullets:
                    experience_text += " ".join(str(b) for b in exp.bullets) + " "

        print(f"[MATCHING DEBUG] Experience text length: {len(experience_text)}")

        # Extract JD required skills as list of strings
        jd_required_skills = []
        if hasattr(job_description, 'required_skills') and job_description.required_skills:
            if isinstance(job_description.required_skills, list):
                jd_required_skills = [str(s) for s in job_description.required_skills if s]

        print(f"[MATCHING DEBUG] JD required skills: {jd_required_skills}")
        print(f"[MATCHING DEBUG] Number of JD required skills: {len(jd_required_skills)}")

        # 1. Keyword/Skill Matching (using existing SkillMatcher)
        skill_match_result = self.skill_matcher.match_skills(
            required_skills=jd_required_skills,
            resume_skills=resume_skills,
            experience_text=experience_text
        )

        print(f"[MATCHING DEBUG] Skill match result: {skill_match_result}")
        print(f"[MATCHING DEBUG] Match percentage: {skill_match_result.get('match_percentage', 0)}")
        print(f"[MATCHING DEBUG] Matched skills: {skill_match_result.get('matched_skills', [])}")
        print(f"[MATCHING DEBUG] Missing skills: {skill_match_result.get('missing_skills', [])}")

        # 2. Semantic Matching (using existing RAG retriever)
        # Index resume and JD first before matching
        try:
            self.rag_retriever.index_resume(resume)
            self.rag_retriever.index_job_description(job_description)
            semantic_matches = self.rag_retriever.match_resume_to_jd(
                resume,
                job_description
            )
        except Exception as e:
            print(f"[MATCHING] RAG retriever error: {str(e)}")
            print("[MATCHING] Continuing with keyword matching only")
            semantic_matches = []

        # Calculate average semantic similarity from the matches
        avg_semantic_similarity = 0.0
        if semantic_matches and isinstance(semantic_matches, list):
            # Extract similarity scores from matches
            similarities = []
            for match in semantic_matches:
                if isinstance(match, dict) and 'similarity' in match:
                    similarities.append(match['similarity'])

            if similarities:
                avg_semantic_similarity = sum(similarities) / len(similarities)

        # 3. Compile results
        match_percentage = skill_match_result.get('match_percentage', 0) * 100

        # Extract skill names from matched_skills objects
        matched_skills_raw = skill_match_result.get('matched_skills', [])
        matched_skills_list = []
        if matched_skills_raw:
            for skill in matched_skills_raw:
                if isinstance(skill, dict):
                    # Extract the 'required' field (the JD skill name)
                    matched_skills_list.append(skill.get('required', str(skill)))
                else:
                    matched_skills_list.append(str(skill))

        missing_skills_list = skill_match_result.get('missing_skills', [])

        # Extract top semantic matches safely
        top_semantic_matches = []
        if semantic_matches and isinstance(semantic_matches, list):
            top_semantic_matches = semantic_matches[:5]
        elif semantic_matches and isinstance(semantic_matches, dict):
            # If it's a dict, convert to empty list for now
            top_semantic_matches = []

        match_analysis = {
            "keyword_match": {
                "percentage": match_percentage,
                "matched_skills": matched_skills_list,
                "missing_skills": missing_skills_list,
                "matched_count": len(matched_skills_list),
                "total_required": len(jd_required_skills),
            },
            "semantic_match": {
                "percentage": avg_semantic_similarity * 100,
                "top_matches": top_semantic_matches,
            },
            "overall_score": (
                match_percentage * 0.6 +  # 60% weight on keywords
                avg_semantic_similarity * 100 * 0.4  # 40% weight on semantics
            ),
        }

        return match_analysis

    def match_resume_to_jobs(
        self,
        resume_text: str,
        job_descriptions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Match resume against multiple job descriptions (for Adzuna workflow)

        Args:
            resume_text: Plain text resume
            job_descriptions: List of job description dictionaries

        Returns:
            List of jobs with match scores, sorted by score
        """
        # Create resume embeddings
        resume_embedding = self.embedding_service.create_embedding(resume_text)

        # Match against each job
        matched_jobs = []
        for job in job_descriptions:
            jd_text = f"{job.get('title', '')} {job.get('description', '')}"
            jd_embedding = self.embedding_service.create_embedding(jd_text)

            # Calculate cosine similarity
            similarity = self.embedding_service.cosine_similarity(
                resume_embedding,
                jd_embedding
            )

            job['similarity_score'] = similarity * 100
            matched_jobs.append(job)

        # Sort by score descending
        matched_jobs.sort(key=lambda x: x['similarity_score'], reverse=True)

        # Filter: only return jobs with >10% match
        return [job for job in matched_jobs if job['similarity_score'] > 10]
