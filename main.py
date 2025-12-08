"""Main entry point for Resume RAG Pipeline."""

import json
from pathlib import Path
from src.parsers.resume_parser import ResumeParser
from src.parsers.jd_parser import JDParser
from src.models import Resume, JobDescription
from src.analysis.skill_matcher import SkillMatcher
from src.rag.retriever import RAGRetriever
from src.generation.generator import ResumeGenerator


class ResumeOptimizer:
    """Main class for resume optimization pipeline."""

    def __init__(self, use_rag: bool = False, use_generation: bool = False):
        """Initialize the resume optimizer."""
        self.resume_parser = ResumeParser()
        self.jd_parser = JDParser()
        self.skill_matcher = SkillMatcher()
        self.use_rag = use_rag
        self.use_generation = use_generation
        self.rag_retriever = None
        self.resume_generator = None
        self.resume: Resume = None
        self.job_description: JobDescription = None
        self.optimized_resume: Resume = None
        self.resume_filename: str = None  # Store original filename

        if use_rag:
            print("Initializing RAG pipeline...")
            self.rag_retriever = RAGRetriever()

        if use_generation:
            print("Initializing LLM generation...")
            self.resume_generator = ResumeGenerator()

    def load_resume(self, file_path: str) -> Resume:
        """
        Load and parse a resume file.

        Args:
            file_path: Path to resume file (PDF, DOCX, or TXT)

        Returns:
            Parsed Resume object
        """
        print(f"Loading resume from: {file_path}")

        # Store the original filename (without extension)
        from pathlib import Path
        self.resume_filename = Path(file_path).stem

        # For TXT files, treat them as plain text resumes
        if file_path.endswith('.txt'):
            text = Path(file_path).read_text()
            # Create temporary DOCX handling or parse as text
            # For now, we'll need to add TXT support to resume parser
            print("Note: TXT format will be parsed as raw text")
            # TODO: Add text-only parsing support

        self.resume = self.resume_parser.parse(file_path)
        print(f"✓ Resume loaded successfully")
        print(f"  - Name: {self.resume.contact.full_name}")
        print(f"  - Email: {self.resume.contact.email}")
        print(f"  - Experience entries: {len(self.resume.experience)}")
        print(f"  - Education entries: {len(self.resume.education)}")
        print(f"  - Skills: {len(self.resume.skills)}")

        return self.resume

    def load_job_description(self, file_path: str) -> JobDescription:
        """
        Load and parse a job description file.

        Args:
            file_path: Path to JD file (PDF, DOCX, or TXT)

        Returns:
            Parsed JobDescription object
        """
        print(f"\nLoading job description from: {file_path}")

        self.job_description = self.jd_parser.parse(file_path)
        print(f"✓ Job description loaded successfully")
        print(f"  - Position: {self.job_description.job_title}")
        print(f"  - Company: {self.job_description.company}")
        print(f"  - Location: {self.job_description.location}")
        print(f"  - Required skills: {len(self.job_description.required_skills)}")
        print(f"  - Responsibilities: {len(self.job_description.responsibilities)}")

        return self.job_description

    def analyze_match(self):
        """Analyze how well the resume matches the job description using intelligent matching."""
        if not self.resume or not self.job_description:
            raise ValueError("Please load both resume and job description first")

        print("\n" + "=" * 60)
        print("INTELLIGENT MATCH ANALYSIS")
        print("=" * 60)

        # Combine all experience text for skill extraction
        experience_text = ""
        for exp in self.resume.experience:
            experience_text += " ".join(exp.bullets) + " "

        # Match required skills
        required_match = self.skill_matcher.match_skills(
            required_skills=self.job_description.required_skills,
            resume_skills=self.resume.skills,
            experience_text=experience_text
        )

        # Match preferred skills
        preferred_match = self.skill_matcher.match_skills(
            required_skills=self.job_description.preferred_skills,
            resume_skills=self.resume.skills,
            experience_text=experience_text
        )

        # Display matched required skills
        print(f"\n✓ MATCHED REQUIRED SKILLS ({required_match['total_matched']}/{required_match['total_required']}):")
        print(f"  Match Score: {required_match['match_percentage']:.1%}\n")

        # Group by source
        skills_section_matches = [m for m in required_match['matched_skills'] if m['source'] == 'skills_section']
        experience_matches = [m for m in required_match['matched_skills'] if m['source'] == 'experience']

        if skills_section_matches:
            print(f"  From Skills Section ({len(skills_section_matches)}):")
            for match in skills_section_matches[:15]:
                if match['required'] != match['matched_as']:
                    print(f"    ✓ {match['required']} → matched as '{match['matched_as']}'")
                else:
                    print(f"    ✓ {match['required']}")

        if experience_matches:
            print(f"\n  From Experience Bullets ({len(experience_matches)}):")
            for match in experience_matches[:15]:
                print(f"    ✓ {match['required']} (found in experience)")

        # Display missing skills
        if required_match['missing_skills']:
            print(f"\n✗ MISSING REQUIRED SKILLS ({len(required_match['missing_skills'])}):")
            for skill in required_match['missing_skills'][:15]:
                print(f"    • {skill}")

        # Display preferred skills match
        if preferred_match['total_required'] > 0:
            print(f"\n+ PREFERRED SKILLS ({preferred_match['total_matched']}/{preferred_match['total_required']}):")
            if preferred_match['matched_skills']:
                for match in preferred_match['matched_skills'][:10]:
                    print(f"    + {match['required']}")

        # Get skill suggestions
        suggestions = self.skill_matcher.get_skill_suggestions(
            required_match['missing_skills'],
            self.resume.skills
        )

        if suggestions:
            print(f"\n💡 SUGGESTIONS:")
            for sugg in suggestions[:5]:
                print(f"    {sugg['suggestion']}")

        # Calculate overall scores
        req_score = required_match['match_percentage']
        pref_score = preferred_match['match_percentage'] if preferred_match['total_required'] > 0 else 0
        overall_score = (req_score * 0.7 + pref_score * 0.3)

        print(f"\n" + "=" * 60)
        print("OVERALL MATCH SCORES")
        print("=" * 60)
        print(f"  Required Skills:  {req_score:.1%}")
        print(f"  Preferred Skills: {pref_score:.1%}")
        print(f"  Overall Match:    {overall_score:.1%}")
        print(f"\n  Skills from resume skills section: {required_match['skills_from_section']}")
        print(f"  Skills from experience bullets:     {required_match['skills_from_experience']}")

    def analyze_semantic_match(self):
        """Perform semantic matching using RAG (vector similarity)."""
        if not self.use_rag or not self.rag_retriever:
            print("\n⚠️  RAG is not enabled. Run with use_rag=True to enable semantic matching.")
            return

        if not self.resume or not self.job_description:
            raise ValueError("Please load both resume and job description first")

        # Index resume and JD
        self.rag_retriever.index_resume(self.resume)
        self.rag_retriever.index_job_description(self.job_description)

        # Perform semantic matching
        match_results = self.rag_retriever.match_resume_to_jd(
            self.resume,
            self.job_description,
            similarity_threshold=0.5
        )

        # Display summary
        print("\n" + "=" * 60)
        print("SEMANTIC MATCH SUMMARY")
        print("=" * 60)
        print(f"  Overall Semantic Similarity: {match_results['overall_similarity']:.1%}")
        print(f"  Responsibility Matches: {len(match_results['responsibility_matches'])}")
        print(f"  Requirement Matches: {len(match_results['requirement_matches'])}")

        # Get suggestions
        suggestions = self.rag_retriever.get_optimization_suggestions(match_results)
        if suggestions:
            print(f"\n📋 OPTIMIZATION SUGGESTIONS:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")

        return match_results

    def generate_optimized_resume(self):
        """Generate optimized resume using LLM."""
        if not self.use_generation or not self.resume_generator:
            print("\n⚠️  Generation is not enabled. Provide API key and run with --generate flag.")
            return

        if not self.resume or not self.job_description:
            raise ValueError("Please load both resume and job description first")

        print("\n" + "=" * 60)
        print("LLM-POWERED RESUME GENERATION")
        print("=" * 60)

        # Generate optimized resume
        self.optimized_resume = self.resume_generator.generate_optimized_resume(
            resume=self.resume,
            jd=self.job_description,
            optimize_summary=True,
            optimize_skills=True,
            optimize_all_experiences=True
        )

        # Generate comparison report
        comparison = self.resume_generator.generate_comparison_report(
            original_resume=self.resume,
            optimized_resume=self.optimized_resume,
            jd=self.job_description
        )

        # Display changes
        print("\n" + "=" * 60)
        print("OPTIMIZATION SUMMARY")
        print("=" * 60)

        if comparison['summary_changed']:
            print("\n✓ Professional Summary: OPTIMIZED")

        if comparison['skills_added']:
            print(f"\n✓ Skills Added ({len(comparison['skills_added'])}):")
            for skill in comparison['skills_added'][:10]:
                print(f"    + {skill}")

        if comparison['experience_changes']:
            print(f"\n✓ Experience Sections Optimized: {len(comparison['experience_changes'])}")
            for change in comparison['experience_changes']:
                print(f"    • {change['company']}: {change['original_bullets']} → {change['optimized_bullets']} bullets")

        return self.optimized_resume

    def export_json(self, output_dir: str = "output"):
        """Export parsed data to JSON files using original filename."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Use original filename as base, or fallback to generic names
        base_name = self.resume_filename if self.resume_filename else "resume"

        if self.resume:
            resume_json = output_path / f"{base_name}.json"
            with open(resume_json, 'w') as f:
                json.dump(self.resume.model_dump(), f, indent=2)
            print(f"\n✓ Resume exported to: {resume_json}")

        if self.job_description:
            jd_json = output_path / f"{base_name}_job_description.json"
            with open(jd_json, 'w') as f:
                json.dump(self.job_description.model_dump(), f, indent=2)
            print(f"✓ Job description exported to: {jd_json}")

        if self.optimized_resume:
            opt_resume_json = output_path / f"{base_name}_optimized_resume.json"
            with open(opt_resume_json, 'w') as f:
                json.dump(self.optimized_resume.model_dump(), f, indent=2)
            print(f"✓ Optimized resume exported to: {opt_resume_json}")


def main(use_rag: bool = False, use_generation: bool = False):
    """Run a simple demo of the resume optimizer."""
    print("=" * 60)
    if use_generation:
        print("RESUME RAG PIPELINE - Phase 3: LLM Generation")
    elif use_rag:
        print("RESUME RAG PIPELINE - Phase 2: Semantic Matching")
    else:
        print("RESUME RAG PIPELINE - Phase 1: Keyword Matching")
    print("=" * 60)

    # Initialize optimizer
    optimizer = ResumeOptimizer(use_rag=use_rag, use_generation=use_generation)

    # Check if sample files exist
    sample_resume = "data/sample_resumes/Haswanth_Data_Engineer_Profile.pdf"
    sample_jd = "data/sample_jds/sample_jd.txt"

    if not Path(sample_resume).exists():
        print(f"\nError: Sample resume not found at {sample_resume}")
        print("Please add a resume file to test the parser.")
        return

    if not Path(sample_jd).exists():
        print(f"\nError: Sample job description not found at {sample_jd}")
        print("Please add a job description file to test the parser.")
        return

    try:
        # For demo purposes, note that TXT files need special handling
        # The parser currently supports PDF and DOCX
        print("\nNote: Sample files are in TXT format for demonstration.")
        print("In production, use PDF or DOCX files with the parsers.")

        # Parse resume (PDF is supported for resume)
        optimizer.load_resume(sample_resume)

        # Parse JD (TXT is supported for JD)
        optimizer.load_job_description(sample_jd)

        # Analyze match (keyword matching)
        optimizer.analyze_match()

        # Semantic matching if RAG is enabled
        if use_rag:
            optimizer.analyze_semantic_match()

        # Generate optimized resume if generation is enabled
        if use_generation:
            optimizer.generate_optimized_resume()

        # Export to JSON
        optimizer.export_json()

        print("\n" + "=" * 60)
        if use_generation:
            print("Phase 3 (LLM Generation) - COMPLETE!")
            print("=" * 60)
            print("\nYour optimized resume has been generated!")
            print("Check output/optimized_resume.json for the result")
            print("\nNext steps:")
            print("1. Review the optimized resume")
            print("2. Compare original vs optimized bullets")
            print("3. Export to formatted DOCX (coming in Phase 6)")
        elif use_rag:
            print("Phase 2 (Semantic Matching) - COMPLETE!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Review the semantic match results above")
            print("2. Run with --generate to create optimized resume: python main.py --rag --generate")
            print("3. Make sure to set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env")
        else:
            print("Phase 1 (Document Processing) - COMPLETE!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Enable semantic matching: python main.py --rag")
            print("2. Enable LLM generation: python main.py --rag --generate")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys

    # Check for chat mode
    if "--chat" in sys.argv or "-c" in sys.argv:
        print("\n🚀 Launching interactive chat mode...")
        from src.chat.chat_service import ChatService

        # Load resume and JD
        sample_resume = "data/sample_resumes/Haswanth_Data_Engineer_Profile.pdf"
        sample_jd = "data/sample_jds/sample_jd.txt"

        if not Path(sample_resume).exists():
            print(f"Error: Resume not found at {sample_resume}")
            sys.exit(1)

        resume_parser = ResumeParser()
        jd_parser = JDParser()

        print(f"\nLoading resume from: {sample_resume}")
        resume = resume_parser.parse(sample_resume)
        print(f"✓ Resume loaded: {resume.contact.full_name}")

        jd = None
        if Path(sample_jd).exists():
            print(f"\nLoading job description from: {sample_jd}")
            jd = jd_parser.parse(sample_jd)
            print(f"✓ Job description loaded: {jd.job_title}\n")

        # Initialize chat service
        chat_service = ChatService(resume=resume, jd=jd)

        # Interactive loop
        print("=" * 60)
        print("RESUME CHAT - Ask questions about your resume!")
        print("=" * 60)
        print("\nType /help for commands, /exit to quit\n")

        while True:
            try:
                question = input("You: ").strip()

                if not question:
                    continue

                if question in ['/exit', '/quit']:
                    print("\n👋 Goodbye!\n")
                    break

                if question == '/help':
                    print("\nCommands: /help, /exit")
                    print("\nExample questions:")
                    print("  • What experience do I have with Spark?")
                    print("  • How well do I match this job?")
                    print("  • What skills should I add?\n")
                    continue

                # Ask question
                print("\n💬 Assistant: ", end="", flush=True)
                answer = chat_service.ask(question)
                print(answer + "\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

        sys.exit(0)

    # Check flags for standard mode
    use_rag = "--rag" in sys.argv or "-r" in sys.argv
    use_generation = "--generate" in sys.argv or "-g" in sys.argv or "--gen" in sys.argv

    main(use_rag=use_rag, use_generation=use_generation)
