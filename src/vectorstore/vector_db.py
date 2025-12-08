"""Vector database operations using simple in-memory storage."""

from typing import List, Dict, Optional, Tuple
import numpy as np
from pathlib import Path
import pickle


class VectorStore:
    """Simple vector store for resume and job description embeddings using in-memory FAISS-like storage."""

    def __init__(self, persist_directory: str = "./data/vector_store"):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # In-memory storage
        self.resume_embeddings = []
        self.resume_documents = []
        self.resume_ids = []
        self.resume_metadatas = []

        self.jd_embeddings = []
        self.jd_documents = []
        self.jd_ids = []
        self.jd_metadatas = []

        # Collections
        self.resume_collection = None
        self.jd_collection = None

    def create_resume_collection(self, collection_name: str = "resume_embeddings"):
        """
        Create or get collection for resume embeddings.

        Args:
            collection_name: Name of the collection
        """
        self.resume_collection = collection_name
        print(f"✓ Resume collection '{collection_name}' ready")
        return self.resume_collection

    def create_jd_collection(self, collection_name: str = "jd_embeddings"):
        """
        Create or get collection for job description embeddings.

        Args:
            collection_name: Name of the collection
        """
        self.jd_collection = collection_name
        print(f"✓ JD collection '{collection_name}' ready")
        return self.jd_collection

    def add_resume_embeddings(self, embeddings_data: Dict):
        """
        Add resume embeddings to the vector store.

        Args:
            embeddings_data: Dictionary from EmbeddingService.embed_resume_sections
        """
        if not self.resume_collection:
            self.create_resume_collection()

        documents = []
        embeddings = []
        ids = []
        metadatas = []

        # Add summary
        if 'summary' in embeddings_data:
            data = embeddings_data['summary']
            documents.append(data['text'])
            embeddings.append(data['embedding'].tolist())
            ids.append(data['id'])
            metadatas.append({'type': data['type']})

        # Add experiences
        if 'experiences' in embeddings_data:
            for data in embeddings_data['experiences']:
                documents.append(data['text'])
                embeddings.append(data['embedding'].tolist())
                ids.append(data['id'])
                metadata = {'type': data['type']}
                if 'metadata' in data:
                    metadata.update(data['metadata'])
                metadatas.append(metadata)

        # Add education
        if 'education' in embeddings_data:
            for data in embeddings_data['education']:
                documents.append(data['text'])
                embeddings.append(data['embedding'].tolist())
                ids.append(data['id'])
                metadata = {'type': data['type']}
                if 'metadata' in data:
                    metadata.update(data['metadata'])
                metadatas.append(metadata)

        # Add skills
        if 'skills' in embeddings_data:
            data = embeddings_data['skills']
            documents.append(data['text'])
            embeddings.append(data['embedding'].tolist())
            ids.append(data['id'])
            metadatas.append({'type': data['type']})

        # Add projects
        if 'projects' in embeddings_data:
            for data in embeddings_data['projects']:
                documents.append(data['text'])
                embeddings.append(data['embedding'].tolist())
                ids.append(data['id'])
                metadata = {'type': data['type']}
                if 'metadata' in data:
                    metadata.update(data['metadata'])
                metadatas.append(metadata)

        # Add to collection (in-memory)
        if documents:
            self.resume_embeddings.extend(embeddings)
            self.resume_documents.extend(documents)
            self.resume_ids.extend(ids)
            self.resume_metadatas.extend(metadatas)
            print(f"✓ Added {len(documents)} resume embeddings to vector store")

    def add_jd_embeddings(self, embeddings_data: Dict):
        """
        Add job description embeddings to the vector store.

        Args:
            embeddings_data: Dictionary from EmbeddingService.embed_job_description
        """
        if not self.jd_collection:
            self.create_jd_collection()

        documents = []
        embeddings = []
        ids = []
        metadatas = []

        # Add overview
        if 'overview' in embeddings_data:
            data = embeddings_data['overview']
            documents.append(data['text'])
            embeddings.append(data['embedding'].tolist())
            ids.append(data['id'])
            metadatas.append({'type': data['type']})

        # Add responsibilities
        if 'responsibilities' in embeddings_data:
            for data in embeddings_data['responsibilities']:
                documents.append(data['text'])
                embeddings.append(data['embedding'].tolist())
                ids.append(data['id'])
                metadatas.append({'type': data['type']})

        # Add requirements
        if 'requirements' in embeddings_data:
            for data in embeddings_data['requirements']:
                documents.append(data['text'])
                embeddings.append(data['embedding'].tolist())
                ids.append(data['id'])
                metadata = {'type': data['type']}
                if 'metadata' in data:
                    metadata.update(data['metadata'])
                metadatas.append(metadata)

        # Add required skills
        if 'required_skills' in embeddings_data:
            data = embeddings_data['required_skills']
            documents.append(data['text'])
            embeddings.append(data['embedding'].tolist())
            ids.append(data['id'])
            metadatas.append({'type': data['type']})

        # Add preferred skills
        if 'preferred_skills' in embeddings_data:
            data = embeddings_data['preferred_skills']
            documents.append(data['text'])
            embeddings.append(data['embedding'].tolist())
            ids.append(data['id'])
            metadatas.append({'type': data['type']})

        # Add to collection (in-memory)
        if documents:
            self.jd_embeddings.extend(embeddings)
            self.jd_documents.extend(documents)
            self.jd_ids.extend(ids)
            self.jd_metadatas.extend(metadatas)
            print(f"✓ Added {len(documents)} JD embeddings to vector store")

    def query_resume(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        filter_type: Optional[str] = None
    ) -> Dict:
        """
        Query resume collection for similar content.

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            filter_type: Filter by content type (e.g., 'experience', 'skills')

        Returns:
            Query results with documents, distances, and metadata
        """
        if not self.resume_embeddings:
            raise ValueError("Resume collection is empty")

        # Convert to numpy arrays
        query_emb = np.array(query_embedding).flatten()
        all_embeddings = np.array(self.resume_embeddings)

        # Filter by type if specified
        valid_indices = []
        for i, metadata in enumerate(self.resume_metadatas):
            if filter_type is None or metadata.get('type') == filter_type:
                valid_indices.append(i)

        if not valid_indices:
            return {'documents': [[]], 'distances': [[]], 'metadatas': [[]]}

        # Calculate cosine distances
        valid_embeddings = all_embeddings[valid_indices]
        similarities = np.dot(valid_embeddings, query_emb) / (
            np.linalg.norm(valid_embeddings, axis=1) * np.linalg.norm(query_emb)
        )

        distances = 1 - similarities  # Convert similarity to distance

        # Get top k results
        top_k = min(n_results, len(valid_indices))
        top_indices = np.argsort(distances)[:top_k]

        # Prepare results
        results = {
            'documents': [[]],
            'distances': [[]],
            'metadatas': [[]]
        }

        for idx in top_indices:
            orig_idx = valid_indices[idx]
            results['documents'][0].append(self.resume_documents[orig_idx])
            results['distances'][0].append(float(distances[idx]))
            results['metadatas'][0].append(self.resume_metadatas[orig_idx])

        return results

    def query_jd(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        filter_type: Optional[str] = None
    ) -> Dict:
        """
        Query JD collection for similar content.

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            filter_type: Filter by content type

        Returns:
            Query results with documents, distances, and metadata
        """
        if not self.jd_collection:
            raise ValueError("JD collection not initialized")

        where_filter = {"type": filter_type} if filter_type else None

        results = self.jd_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where_filter
        )

        return results

    def find_relevant_experiences(
        self,
        jd_requirement: str,
        query_embedding: np.ndarray,
        n_results: int = 3
    ) -> List[Dict]:
        """
        Find resume experiences most relevant to a JD requirement.

        Args:
            jd_requirement: Job description requirement text
            query_embedding: Embedding of the requirement
            n_results: Number of experiences to return

        Returns:
            List of relevant experiences with similarity scores
        """
        results = self.query_resume(
            query_embedding=query_embedding,
            n_results=n_results,
            filter_type='experience_bullet'
        )

        relevant_experiences = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i]
                similarity = 1 - distance  # Convert distance to similarity

                relevant_experiences.append({
                    'text': doc,
                    'similarity': similarity,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                })

        return relevant_experiences

    def clear_collections(self):
        """Clear all collections (useful for testing)."""
        self.resume_embeddings = []
        self.resume_documents = []
        self.resume_ids = []
        self.resume_metadatas = []
        self.jd_embeddings = []
        self.jd_documents = []
        self.jd_ids = []
        self.jd_metadatas = []
        print("✓ Cleared all collections")

    def get_collection_stats(self):
        """Get statistics about stored collections."""
        stats = {}

        if self.resume_collection:
            stats['resume_count'] = len(self.resume_documents)

        if self.jd_collection:
            stats['jd_count'] = len(self.jd_documents)

        return stats
