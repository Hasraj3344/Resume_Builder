"""Embedding generation for resume and job description content."""

from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import hashlib


class EmbeddingService:
    """Service for generating embeddings using sentence transformers."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the sentence-transformers model to use
                       Default: all-MiniLM-L6-v2 (fast, 384 dimensions)
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the sentence transformer model."""
        print(f"Loading embedding model: {self.model_name}")
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"✓ Model loaded successfully")
            print(f"  Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            numpy array of embeddings
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.model.get_sentence_embedding_dimension())

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def generate_embeddings(self, texts: List[str], show_progress: bool = False) -> np.ndarray:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts to embed
            show_progress: Whether to show progress bar

        Returns:
            numpy array of embeddings (shape: [len(texts), embedding_dim])
        """
        if not texts:
            return np.array([])

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=show_progress
        )
        return embeddings

    def generate_text_id(self, text: str) -> str:
        """
        Generate a unique ID for a text based on its content.

        Args:
            text: Input text

        Returns:
            Unique hash ID
        """
        return hashlib.md5(text.encode()).hexdigest()

    def embed_resume_sections(self, resume) -> Dict[str, Dict]:
        """
        Generate embeddings for all sections of a resume.

        Args:
            resume: Resume object from models

        Returns:
            Dictionary mapping section names to embeddings and metadata
        """
        embeddings_data = {}

        # Embed summary
        if resume.summary:
            embeddings_data['summary'] = {
                'text': resume.summary,
                'embedding': self.generate_embedding(resume.summary),
                'type': 'summary',
                'id': self.generate_text_id(resume.summary)
            }

        # Embed each experience entry
        embeddings_data['experiences'] = []
        for i, exp in enumerate(resume.experience):
            # Embed full experience (title + company + all bullets)
            exp_text = f"{exp.title} at {exp.company}. " + " ".join(exp.bullets)

            embeddings_data['experiences'].append({
                'text': exp_text,
                'embedding': self.generate_embedding(exp_text),
                'type': 'experience',
                'id': f"exp_{i}",
                'metadata': {
                    'company': exp.company,
                    'title': exp.title,
                    'dates': f"{exp.start_date} - {exp.end_date}",
                    'is_current': exp.is_current
                }
            })

            # Also embed individual bullets for granular matching
            for j, bullet in enumerate(exp.bullets):
                if bullet.strip():
                    embeddings_data['experiences'].append({
                        'text': bullet,
                        'embedding': self.generate_embedding(bullet),
                        'type': 'experience_bullet',
                        'id': f"exp_{i}_bullet_{j}",
                        'metadata': {
                            'company': exp.company,
                            'title': exp.title,
                            'bullet_index': j
                        }
                    })

        # Embed education
        embeddings_data['education'] = []
        for i, edu in enumerate(resume.education):
            edu_text = f"{edu.degree} in {edu.field_of_study} from {edu.institution}"
            embeddings_data['education'].append({
                'text': edu_text,
                'embedding': self.generate_embedding(edu_text),
                'type': 'education',
                'id': f"edu_{i}",
                'metadata': {
                    'institution': edu.institution,
                    'degree': edu.degree
                }
            })

        # Embed skills (as a combined text)
        if resume.skills:
            skills_text = ", ".join(resume.skills)
            embeddings_data['skills'] = {
                'text': skills_text,
                'embedding': self.generate_embedding(skills_text),
                'type': 'skills',
                'id': 'skills_all'
            }

        # Embed projects
        embeddings_data['projects'] = []
        for i, proj in enumerate(resume.projects):
            proj_text = f"{proj.name}. {proj.description if proj.description else ''} {' '.join(proj.bullets)}"
            embeddings_data['projects'].append({
                'text': proj_text,
                'embedding': self.generate_embedding(proj_text),
                'type': 'project',
                'id': f"proj_{i}",
                'metadata': {
                    'name': proj.name
                }
            })

        return embeddings_data

    def embed_job_description(self, jd) -> Dict[str, Dict]:
        """
        Generate embeddings for all sections of a job description.

        Args:
            jd: JobDescription object from models

        Returns:
            Dictionary mapping section names to embeddings and metadata
        """
        embeddings_data = {}

        # Embed overview
        if jd.overview:
            embeddings_data['overview'] = {
                'text': jd.overview,
                'embedding': self.generate_embedding(jd.overview),
                'type': 'jd_overview',
                'id': 'jd_overview'
            }

        # Embed responsibilities
        embeddings_data['responsibilities'] = []
        for i, resp in enumerate(jd.responsibilities):
            embeddings_data['responsibilities'].append({
                'text': resp,
                'embedding': self.generate_embedding(resp),
                'type': 'jd_responsibility',
                'id': f"jd_resp_{i}"
            })

        # Embed requirements
        embeddings_data['requirements'] = []
        for i, req in enumerate(jd.requirements):
            embeddings_data['requirements'].append({
                'text': req.description,
                'embedding': self.generate_embedding(req.description),
                'type': 'jd_requirement',
                'id': f"jd_req_{i}",
                'metadata': {
                    'category': req.category,
                    'skills': req.skills
                }
            })

        # Embed required skills (as combined text)
        if jd.required_skills:
            req_skills_text = ", ".join(jd.required_skills)
            embeddings_data['required_skills'] = {
                'text': req_skills_text,
                'embedding': self.generate_embedding(req_skills_text),
                'type': 'jd_required_skills',
                'id': 'jd_req_skills'
            }

        # Embed preferred skills
        if jd.preferred_skills:
            pref_skills_text = ", ".join(jd.preferred_skills)
            embeddings_data['preferred_skills'] = {
                'text': pref_skills_text,
                'embedding': self.generate_embedding(pref_skills_text),
                'type': 'jd_preferred_skills',
                'id': 'jd_pref_skills'
            }

        return embeddings_data

    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        # Cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
