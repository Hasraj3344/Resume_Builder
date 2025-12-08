"""RAG retriever for matching resume content to job requirements."""

from typing import List, Dict, Tuple
import numpy as np
from src.vectorstore.embeddings import EmbeddingService
from src.vectorstore.vector_db import VectorStore
from src.models import Resume, JobDescription


class RAGRetriever:
    """Retrieval-Augmented Generation retriever for resume optimization."""

    def __init__(self, embedding_service: EmbeddingService = None, vector_store: VectorStore = None):
        """
        Initialize the RAG retriever.

        Args:
            embedding_service: EmbeddingService instance (creates new if None)
            vector_store: VectorStore instance (creates new if None)
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

    def index_resume(self, resume: Resume):
        """
        Index a resume in the vector store.

        Args:
            resume: Resume object to index
        """
        print("\n" + "=" * 60)
        print("INDEXING RESUME")
        print("=" * 60)

        # Generate embeddings
        embeddings_data = self.embedding_service.embed_resume_sections(resume)

        # Store in vector database
        self.vector_store.create_resume_collection()
        self.vector_store.add_resume_embeddings(embeddings_data)

        # Print stats
        stats = self.vector_store.get_collection_stats()
        print(f"\n✓ Resume indexed successfully")
        print(f"  Total embeddings: {stats.get('resume_count', 0)}")

    def index_job_description(self, jd: JobDescription):
        """
        Index a job description in the vector store.

        Args:
            jd: JobDescription object to index
        """
        print("\n" + "=" * 60)
        print("INDEXING JOB DESCRIPTION")
        print("=" * 60)

        # Generate embeddings
        embeddings_data = self.embedding_service.embed_job_description(jd)

        # Store in vector database
        self.vector_store.create_jd_collection()
        self.vector_store.add_jd_embeddings(embeddings_data)

        # Print stats
        stats = self.vector_store.get_collection_stats()
        print(f"\n✓ Job description indexed successfully")
        print(f"  Total embeddings: {stats.get('jd_count', 0)}")

    def find_relevant_experiences_for_requirement(
        self,
        requirement: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Find the most relevant resume experiences for a JD requirement.

        Args:
            requirement: Job requirement text
            top_k: Number of top results to return

        Returns:
            List of relevant experiences with similarity scores
        """
        # Generate embedding for the requirement
        req_embedding = self.embedding_service.generate_embedding(requirement)

        # Query resume for relevant experiences
        relevant = self.vector_store.find_relevant_experiences(
            jd_requirement=requirement,
            query_embedding=req_embedding,
            n_results=top_k
        )

        return relevant

    def match_resume_to_jd(
        self,
        resume: Resume,
        jd: JobDescription,
        similarity_threshold: float = 0.5
    ) -> Dict:
        """
        Perform semantic matching between resume and job description.

        Args:
            resume: Resume object
            jd: JobDescription object
            similarity_threshold: Minimum similarity score to consider a match

        Returns:
            Dictionary with match results
        """
        print("\n" + "=" * 60)
        print("SEMANTIC MATCHING (RAG)")
        print("=" * 60)

        results = {
            'responsibility_matches': [],
            'requirement_matches': [],
            'overall_similarity': 0.0,
            'top_experiences': []
        }

        # Match each JD responsibility to resume experiences
        print("\nMatching JD Responsibilities to Resume Experiences:")
        for i, responsibility in enumerate(jd.responsibilities[:5]):  # Top 5 responsibilities
            relevant_exps = self.find_relevant_experiences_for_requirement(
                responsibility,
                top_k=2
            )

            if relevant_exps:
                top_match = relevant_exps[0]
                if top_match['similarity'] >= similarity_threshold:
                    results['responsibility_matches'].append({
                        'responsibility': responsibility,
                        'matched_experience': top_match['text'],
                        'similarity': top_match['similarity']
                    })

                    print(f"\n  Responsibility {i+1}: {responsibility[:80]}...")
                    print(f"  ↓ Similarity: {top_match['similarity']:.2%}")
                    print(f"  ✓ Matched: {top_match['text'][:100]}...")

        # Match each JD requirement to resume content
        print("\n\nMatching JD Requirements to Resume:")
        for i, req in enumerate(jd.requirements[:5]):  # Top 5 requirements
            relevant_exps = self.find_relevant_experiences_for_requirement(
                req.description,
                top_k=2
            )

            if relevant_exps:
                top_match = relevant_exps[0]
                if top_match['similarity'] >= similarity_threshold:
                    results['requirement_matches'].append({
                        'requirement': req.description,
                        'category': req.category,
                        'matched_experience': top_match['text'],
                        'similarity': top_match['similarity']
                    })

                    print(f"\n  Requirement {i+1}: {req.description[:80]}...")
                    print(f"  ↓ Similarity: {top_match['similarity']:.2%}")
                    print(f"  ✓ Matched: {top_match['text'][:100]}...")

        # Calculate overall similarity
        all_similarities = (
            [m['similarity'] for m in results['responsibility_matches']] +
            [m['similarity'] for m in results['requirement_matches']]
        )

        if all_similarities:
            results['overall_similarity'] = np.mean(all_similarities)

        # Get top experiences overall
        if jd.responsibilities:
            combined_jd_text = " ".join(jd.responsibilities[:3])
            jd_embedding = self.embedding_service.generate_embedding(combined_jd_text)

            top_exps = self.vector_store.find_relevant_experiences(
                jd_requirement=combined_jd_text,
                query_embedding=jd_embedding,
                n_results=5
            )

            results['top_experiences'] = top_exps

        return results

    def get_optimization_suggestions(self, match_results: Dict) -> List[str]:
        """
        Generate suggestions for resume optimization based on match results.

        Args:
            match_results: Results from match_resume_to_jd

        Returns:
            List of suggestion strings
        """
        suggestions = []

        # Check semantic match score
        overall_sim = match_results['overall_similarity']

        if overall_sim < 0.5:
            suggestions.append(
                "Low semantic match detected. Consider rewriting experience bullets "
                "to better align with job description terminology."
            )

        # Check if key responsibilities are matched
        resp_matches = len(match_results['responsibility_matches'])
        if resp_matches < 3:
            suggestions.append(
                f"Only {resp_matches} key responsibilities matched. Highlight experiences "
                "that demonstrate these responsibilities more prominently."
            )

        # Check requirement matches
        req_matches = len(match_results['requirement_matches'])
        if req_matches < 3:
            suggestions.append(
                f"Only {req_matches} requirements strongly matched. Consider adding "
                "specific examples or projects that demonstrate missing requirements."
            )

        return suggestions
