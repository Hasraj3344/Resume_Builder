"""Interactive chat interface for resume Q&A."""

import sys
from pathlib import Path
from src.parsers.resume_parser import ResumeParser
from src.parsers.jd_parser import JDParser
from src.chat.chat_service import ChatService


class InteractiveChatCLI:
    """Interactive CLI for chatting about resumes."""

    def __init__(self):
        """Initialize the chat CLI."""
        self.chat_service = None
        self.resume_parser = ResumeParser()
        self.jd_parser = JDParser()

    def print_header(self):
        """Print chat header."""
        print("\n" + "=" * 60)
        print("RESUME CHAT - Interactive Q&A")
        print("=" * 60)
        print("\nAsk questions about your resume and get instant answers!")
        print("Powered by RAG + LLM\n")

    def print_commands(self):
        """Print available commands."""
        print("\nAvailable commands:")
        print("  /help     - Show this help message")
        print("  /history  - Show conversation history")
        print("  /clear    - Clear conversation history")
        print("  /examples - Show example questions")
        print("  /exit     - Exit chat")
        print()

    def print_examples(self):
        """Print example questions."""
        print("\n" + "=" * 60)
        print("EXAMPLE QUESTIONS")
        print("=" * 60)
        print("\n📊 Experience Questions:")
        print("  • What experience do I have with Spark?")
        print("  • Where have I used Azure Data Factory?")
        print("  • What data engineering projects have I worked on?")
        print("\n🔧 Skill Questions:")
        print("  • Do I know Python?")
        print("  • What is my experience with Databricks?")
        print("  • Am I familiar with CI/CD?")
        print("\n🎯 Matching Questions (requires JD):")
        print("  • How well do I match this job description?")
        print("  • Do I qualify for this role?")
        print("  • What requirements am I missing?")
        print("\n💡 Improvement Questions:")
        print("  • What skills should I add to my resume?")
        print("  • How can I improve my resume?")
        print("  • What am I missing for this role?")
        print("\n📝 General Questions:")
        print("  • Tell me about my background")
        print("  • What are my key strengths?")
        print("  • Summarize my work history")
        print("=" * 60 + "\n")

    def load_resume_and_jd(self):
        """Load resume and optionally JD."""
        # Check for sample files
        sample_resume = "data/sample_resumes/Haswanth_Data_Engineer_Profile.pdf"
        sample_jd = "data/sample_jds/sample_jd.txt"

        if not Path(sample_resume).exists():
            print(f"\n❌ Error: Resume not found at {sample_resume}")
            print("Please add a resume file to continue.")
            sys.exit(1)

        # Load resume
        print(f"\nLoading resume from: {sample_resume}")
        resume = self.resume_parser.parse(sample_resume)
        print(f"✓ Resume loaded: {resume.contact.full_name}")

        # Load JD if available
        jd = None
        if Path(sample_jd).exists():
            print(f"\nLoading job description from: {sample_jd}")
            jd = self.jd_parser.parse(sample_jd)
            print(f"✓ Job description loaded: {jd.job_title}")
        else:
            print("\nℹ️  No job description found. Matching questions will be limited.")

        return resume, jd

    def run(self):
        """Run the interactive chat."""
        self.print_header()

        # Load resume and JD
        print("\nInitializing chat service...")
        resume, jd = self.load_resume_and_jd()

        # Initialize chat service
        self.chat_service = ChatService(resume=resume, jd=jd)

        # Show commands
        self.print_commands()

        # Main chat loop
        print("Type your question or /help for commands\n")

        while True:
            try:
                # Get user input
                question = input("You: ").strip()

                if not question:
                    continue

                # Handle commands
                if question.startswith('/'):
                    if question == '/exit' or question == '/quit':
                        print("\n👋 Thanks for using Resume Chat! Goodbye.\n")
                        break

                    elif question == '/help':
                        self.print_commands()
                        continue

                    elif question == '/examples':
                        self.print_examples()
                        continue

                    elif question == '/history':
                        self.print_history()
                        continue

                    elif question == '/clear':
                        self.chat_service.clear_history()
                        continue

                    else:
                        print(f"❌ Unknown command: {question}")
                        print("Type /help for available commands\n")
                        continue

                # Ask question
                print("\n💬 Assistant: ", end="", flush=True)
                answer = self.chat_service.ask(question)
                print(answer + "\n")

            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using Resume Chat! Goodbye.\n")
                break

            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    def print_history(self):
        """Print conversation history."""
        history = self.chat_service.get_conversation_history()

        if not history:
            print("\n📭 No conversation history yet.\n")
            return

        print("\n" + "=" * 60)
        print("CONVERSATION HISTORY")
        print("=" * 60)

        for i, item in enumerate(history, 1):
            print(f"\n[{i}] You: {item['question']}")
            print(f"    Type: {item['type']}")
            print(f"    Assistant: {item['answer'][:150]}...")

        print("\n" + "=" * 60 + "\n")


def main():
    """Main entry point."""
    cli = InteractiveChatCLI()
    cli.run()


if __name__ == "__main__":
    main()
