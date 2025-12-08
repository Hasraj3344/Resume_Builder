"""Chat service for interactive resume Q&A."""

from typing import List, Dict, Optional
from src.models import Resume, JobDescription
from src.generation.llm_service import LLMService, get_default_llm_service
from src.generation.chat_prompts import ChatPromptTemplates
from src.rag.retriever import RAGRetriever
from src.analysis.skill_matcher import SkillMatcher


class ChatService:
    """Interactive chat service for resume questions."""

    def __init__(
        self,
        resume: Resume,
        jd: Optional[JobDescription] = None,
        llm_service: Optional[LLMService] = None,
        rag_retriever: Optional[RAGRetriever] = None
    ):
        """
        Initialize chat service.

        Args:
            resume: Resume to answer questions about
            jd: Optional job description for matching questions
            llm_service: LLM service (creates default if None)
            rag_retriever: RAG retriever (creates default if None)
        """
        self.resume = resume
        self.jd = jd
        self.llm_service = llm_service or get_default_llm_service()
        self.rag_retriever = rag_retriever or RAGRetriever()
        self.chat_prompts = ChatPromptTemplates()
        self.skill_matcher = SkillMatcher()
        self.conversation_history: List[Dict[str, str]] = []

        # Index resume in RAG
        print("Indexing resume for chat...")
        self.rag_retriever.index_resume(resume)

        # Index JD if provided
        if jd:
            print("Indexing job description for chat...")
            self.rag_retriever.index_job_description(jd)

        print("✓ Chat service ready!\n")

    def ask(self, question: str) -> str:
        """
        Ask a question about the resume.

        Args:
            question: User's question

        Returns:
            Answer string
        """
        # Classify question type
        question_type = self.chat_prompts.classify_question_type(question)

        # Route to appropriate handler
        if question_type == 'skill':
            answer = self._handle_skill_question(question)
        elif question_type == 'experience':
            answer = self._handle_experience_question(question)
        elif question_type == 'match':
            answer = self._handle_match_question(question)
        elif question_type == 'suggestion':
            answer = self._handle_suggestion_question(question)
        else:
            answer = self._handle_general_question(question)

        # Store in conversation history
        self.conversation_history.append({
            'question': question,
            'answer': answer,
            'type': question_type
        })

        return answer

    def _handle_skill_question(self, question: str) -> str:
        """Handle questions about specific skills."""
        # Extract skill from question (simple extraction)
        skill_keywords = self._extract_skill_from_question(question)

        # Get relevant experience
        experience_text = self._get_experience_text()

        # Find mentions in experience
        relevant_exp = []
        for exp in self.resume.experience:
            for bullet in exp.bullets:
                if any(skill.lower() in bullet.lower() for skill in skill_keywords):
                    relevant_exp.append(f"• {exp.title} at {exp.company}: {bullet}")

        experience_context = "\n".join(relevant_exp[:5]) if relevant_exp else "No specific mentions found."

        # Generate prompt
        prompt = self.chat_prompts.get_skill_query_prompt(
            skill=", ".join(skill_keywords),
            experience_context=experience_context,
            skills_list=self.resume.skills
        )

        # Generate answer
        try:
            answer = self.llm_service.generate(prompt, temperature=0.7, max_tokens=400)
            return answer.strip()
        except Exception as e:
            return f"Error generating answer: {e}"

    def _handle_experience_question(self, question: str) -> str:
        """Handle questions about experience."""
        # Use RAG to retrieve relevant experience
        query_embedding = self.rag_retriever.embedding_service.generate_embedding(question)
        results = self.rag_retriever.vector_store.query_resume(
            query_embedding=query_embedding,
            n_results=5,
            filter_type='experience'
        )

        # Build context from results
        context_parts = []
        if results['documents'][0]:  # Check if we have results
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                similarity = 1 - distance
                if similarity > 0.3:  # Relevance threshold
                    context_parts.append(f"• {doc} (relevance: {similarity:.1%})")

        context = "\n".join(context_parts) if context_parts else "No directly relevant experience found."

        # Generate prompt
        prompt = self.chat_prompts.get_resume_qa_prompt(
            question=question,
            retrieved_context=context,
            resume_summary=self.resume.summary
        )

        # Generate answer
        try:
            answer = self.llm_service.generate(prompt, temperature=0.7, max_tokens=400)
            return answer.strip()
        except Exception as e:
            return f"Error generating answer: {e}"

    def _handle_match_question(self, question: str) -> str:
        """Handle questions about JD matching."""
        if not self.jd:
            return "I don't have a job description loaded. Please load a JD to ask matching questions."

        # Get match results
        match_results = self.rag_retriever.match_resume_to_jd(
            self.resume,
            self.jd,
            similarity_threshold=0.5
        )

        # Build resume context
        resume_highlights = []
        for exp in self.resume.experience[:2]:
            resume_highlights.append(f"{exp.title} at {exp.company}:")
            for bullet in exp.bullets[:3]:
                resume_highlights.append(f"  • {bullet}")

        resume_context = "\n".join(resume_highlights)

        # Build JD context
        jd_context = f"Position: {self.jd.job_title}\n\n"
        jd_context += "Required Skills:\n" + "\n".join([f"• {skill}" for skill in self.jd.required_skills[:10]])
        jd_context += "\n\nKey Responsibilities:\n" + "\n".join([f"• {resp}" for resp in self.jd.responsibilities[:5]])

        # Generate prompt
        prompt = self.chat_prompts.get_jd_match_prompt(
            question=question,
            resume_context=resume_context,
            jd_context=jd_context,
            match_score=match_results['overall_similarity']
        )

        # Generate answer
        try:
            answer = self.llm_service.generate(prompt, temperature=0.7, max_tokens=600)
            return answer.strip()
        except Exception as e:
            return f"Error generating answer: {e}"

    def _handle_suggestion_question(self, question: str) -> str:
        """Handle questions about improvements."""
        if not self.jd:
            # General suggestions without JD
            current_state = f"Resume has {len(self.resume.experience)} experience entries, "
            current_state += f"{len(self.resume.skills)} skills listed"

            missing_elements = [
                "Consider adding metrics and quantifiable achievements",
                "Ensure each bullet starts with a strong action verb",
                "Add specific technologies and tools used",
                "Include project outcomes and business impact"
            ]

            context = self._get_experience_text()[:500]
        else:
            # Suggestions based on JD matching
            experience_text = " ".join([" ".join(exp.bullets) for exp in self.resume.experience])

            match_result = self.skill_matcher.match_skills(
                required_skills=self.jd.required_skills,
                resume_skills=self.resume.skills,
                experience_text=experience_text
            )

            current_state = f"You match {match_result['match_percentage']:.1%} of required skills"
            missing_elements = match_result['missing_skills'][:10]

            context = f"Target role: {self.jd.job_title}\n"
            context += f"Missing skills: {', '.join(missing_elements)}"

        # Generate prompt
        prompt = self.chat_prompts.get_suggestion_prompt(
            current_state=current_state,
            missing_elements=missing_elements,
            context=context
        )

        # Generate answer
        try:
            answer = self.llm_service.generate(prompt, temperature=0.7, max_tokens=600)
            return answer.strip()
        except Exception as e:
            return f"Error generating answer: {e}"

    def _handle_general_question(self, question: str) -> str:
        """Handle general questions using RAG."""
        # Use RAG to retrieve relevant content
        query_embedding = self.rag_retriever.embedding_service.generate_embedding(question)
        results = self.rag_retriever.vector_store.query_resume(
            query_embedding=query_embedding,
            n_results=5
        )

        # Build context
        context_parts = []
        if results['documents'][0]:  # Check if we have results
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                similarity = 1 - distance
                if similarity > 0.3:
                    context_parts.append(f"• {doc}")

        context = "\n".join(context_parts) if context_parts else "No relevant information found."

        # Use conversation history if available
        if self.conversation_history:
            prompt = self.chat_prompts.get_conversation_prompt(
                question=question,
                conversation_history=self.conversation_history,
                current_context=context
            )
        else:
            prompt = self.chat_prompts.get_resume_qa_prompt(
                question=question,
                retrieved_context=context,
                resume_summary=self.resume.summary
            )

        # Generate answer
        try:
            answer = self.llm_service.generate(prompt, temperature=0.7, max_tokens=400)
            return answer.strip()
        except Exception as e:
            return f"Error generating answer: {e}"

    def _extract_skill_from_question(self, question: str) -> List[str]:
        """Extract skill keywords from question."""
        # Simple extraction - look for quoted terms or words after "with"
        import re

        # Check for quoted terms
        quoted = re.findall(r'"([^"]+)"', question)
        if quoted:
            return quoted

        # Check for pattern "experience with X"
        match = re.search(r'(?:with|about|in)\s+([A-Za-z][A-Za-z0-9\s\+\#\.]+?)(?:\?|$)', question)
        if match:
            skill = match.group(1).strip()
            return [skill]

        # Fallback - check against known skills
        question_lower = question.lower()
        found_skills = []
        for skill in self.resume.skills:
            if skill.lower() in question_lower:
                found_skills.append(skill)

        return found_skills if found_skills else ["the skill mentioned"]

    def _get_experience_text(self) -> str:
        """Get all experience text concatenated."""
        text_parts = []
        for exp in self.resume.experience:
            text_parts.append(f"{exp.title} at {exp.company}")
            text_parts.extend(exp.bullets)
        return " ".join(text_parts)

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("✓ Conversation history cleared")
