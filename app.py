"""Complete Resume Builder Streamlit Application."""

import streamlit as st
import tempfile
import json
from pathlib import Path
from datetime import datetime

# Import all necessary modules
from src.parsers.resume_parser import ResumeParser
from src.parsers.jd_parser import JDParser
from src.analysis.skill_matcher import SkillMatcher
from src.rag.retriever import RAGRetriever
from src.generation.generator import ResumeGenerator
from src.generation.cover_letter_generator import CoverLetterGenerator
from src.generation.cover_letter_prompts import CoverLetterStyle
from src.export.docx_formatter import DOCXExporter
from src.chat.chat_service import ChatService
from src.chat.modification_handler import ModificationHandler

# Page configuration
st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1F4788;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E5C8A;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .score-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .success-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'resume' not in st.session_state:
    st.session_state.resume = None
if 'jd' not in st.session_state:
    st.session_state.jd = None
if 'match_results' not in st.session_state:
    st.session_state.match_results = None
if 'chat_service' not in st.session_state:
    st.session_state.chat_service = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'optimized_resume' not in st.session_state:
    st.session_state.optimized_resume = None
if 'ats_result' not in st.session_state:
    st.session_state.ats_result = None
if 'cover_letters' not in st.session_state:
    st.session_state.cover_letters = {}
if 'resume_filename' not in st.session_state:
    st.session_state.resume_filename = None


def main():
    """Main application function."""

    # Header
    st.markdown('<div class="main-header">🚀 AI-Powered Resume Builder</div>', unsafe_allow_html=True)

    # Sidebar - Progress tracker
    with st.sidebar:
        st.markdown("### 📋 Workflow Progress")
        steps = [
            "1️⃣ Upload Resume & JD",
            "2️⃣ Document Analysis",
            "3️⃣ Interactive Chat",
            "4️⃣ Generate Optimized Resume",
            "5️⃣ Export Options"
        ]

        for i, step_text in enumerate(steps, 1):
            if st.session_state.step > i:
                st.success(step_text)
            elif st.session_state.step == i:
                st.info(f"**{step_text}** ⬅️")
            else:
                st.text(step_text)

        st.markdown("---")
        if st.button("🔄 Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.step = 1
            st.rerun()

    # Main content based on step
    if st.session_state.step == 1:
        step1_upload()
    elif st.session_state.step == 2:
        step2_analysis()
    elif st.session_state.step == 3:
        step3_chat()
    elif st.session_state.step == 4:
        step4_generate()
    elif st.session_state.step == 5:
        step5_export()


def step1_upload():
    """Step 1: Upload resume and paste JD."""
    st.markdown('<div class="section-header">Step 1: Upload Your Resume & Job Description</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📄 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume in PDF, DOCX, or TXT format"
        )

        if uploaded_file:
            st.success(f"✓ Uploaded: {uploaded_file.name}")

    with col2:
        st.markdown("#### 📋 Paste Job Description")
        jd_text = st.text_area(
            "Paste the job description here",
            height=300,
            placeholder="Copy and paste the full job description from the job posting..."
        )

        if jd_text:
            st.success(f"✓ JD pasted ({len(jd_text)} characters)")

    # Process button
    if uploaded_file and jd_text:
        if st.button("🔍 Process & Analyze", type="primary"):
            with st.spinner("Processing documents..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name

                try:
                    # Store original filename (without extension)
                    st.session_state.resume_filename = Path(uploaded_file.name).stem

                    # Parse resume
                    resume_parser = ResumeParser()
                    st.session_state.resume = resume_parser.parse(tmp_path)

                    # Parse JD (save to temp file first)
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as jd_file:
                        jd_file.write(jd_text)
                        jd_path = jd_file.name

                    jd_parser = JDParser()
                    st.session_state.jd = jd_parser.parse(jd_path)

                    # Move to next step
                    st.session_state.step = 2
                    st.rerun()

                except Exception as e:
                    st.error(f"Error processing files: {e}")
                finally:
                    # Clean up temp files
                    Path(tmp_path).unlink(missing_ok=True)
                    if 'jd_path' in locals():
                        Path(jd_path).unlink(missing_ok=True)


def step2_analysis():
    """Step 2: Show document analysis and matching scores."""
    st.markdown('<div class="section-header">Step 2: Document Analysis & Matching</div>', unsafe_allow_html=True)

    resume = st.session_state.resume
    jd = st.session_state.jd

    # Display parsed information
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 👤 Your Resume")
        st.write(f"**Name:** {resume.contact.full_name}")
        st.write(f"**Email:** {resume.contact.email}")
        st.write(f"**Experience Entries:** {len(resume.experience)}")
        st.write(f"**Skills:** {len(resume.skills)}")

    with col2:
        st.markdown("#### 💼 Target Position")
        st.write(f"**Job Title:** {jd.job_title}")
        if jd.company:
            st.write(f"**Company:** {jd.company}")
        st.write(f"**Required Skills:** {len(jd.required_skills)}")
        st.write(f"**Responsibilities:** {len(jd.responsibilities)}")

    # Perform matching analysis
    with st.spinner("Analyzing match..."):
        # Keyword matching
        skill_matcher = SkillMatcher()
        experience_text = " ".join([" ".join(exp.bullets) for exp in resume.experience])

        match_result = skill_matcher.match_skills(
            required_skills=jd.required_skills,
            resume_skills=resume.skills,
            experience_text=experience_text
        )

        # Semantic matching with RAG
        rag_retriever = RAGRetriever()
        rag_retriever.index_resume(resume)
        rag_retriever.index_job_description(jd)

        semantic_results = rag_retriever.match_resume_to_jd(
            resume, jd, similarity_threshold=0.5
        )

        st.session_state.match_results = {
            'keyword_match': match_result,
            'semantic_match': semantic_results
        }

    # Display scores
    st.markdown("---")
    st.markdown("### 📊 Match Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        keyword_score = match_result['match_percentage']
        st.markdown(f"""
        <div class="score-box">
            <h3 style="text-align: center; color: #1F4788;">Keyword Match</h3>
            <h1 style="text-align: center; color: {'#28a745' if keyword_score > 0.7 else '#ffc107' if keyword_score > 0.5 else '#dc3545'};">{keyword_score:.1%}</h1>
            <p style="text-align: center;">{match_result['total_matched']}/{match_result['total_required']} skills</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        semantic_score = semantic_results['overall_similarity']
        st.markdown(f"""
        <div class="score-box">
            <h3 style="text-align: center; color: #1F4788;">Semantic Match</h3>
            <h1 style="text-align: center; color: {'#28a745' if semantic_score > 0.7 else '#ffc107' if semantic_score > 0.5 else '#dc3545'};">{semantic_score:.1%}</h1>
            <p style="text-align: center;">AI-powered analysis</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        overall_score = (keyword_score * 0.6 + semantic_score * 0.4)
        st.markdown(f"""
        <div class="score-box">
            <h3 style="text-align: center; color: #1F4788;">Overall Score</h3>
            <h1 style="text-align: center; color: {'#28a745' if overall_score > 0.7 else '#ffc107' if overall_score > 0.5 else '#dc3545'};">{overall_score:.1%}</h1>
            <p style="text-align: center;">Combined rating</p>
        </div>
        """, unsafe_allow_html=True)

    # Show details in expander
    with st.expander("📋 View Detailed Analysis"):
        tab1, tab2, tab3 = st.tabs(["✅ Matched Skills", "❌ Missing Skills", "💡 Suggestions"])

        with tab1:
            st.markdown("**Skills found in your resume:**")
            for match in match_result['matched_skills'][:20]:
                source = "📄 Skills Section" if match['source'] == 'skills_section' else "💼 Experience"
                st.write(f"• {match['required']} ({source})")

        with tab2:
            st.markdown("**Skills missing from your resume:**")
            for skill in match_result['missing_skills'][:15]:
                st.write(f"• {skill}")

        with tab3:
            suggestions = skill_matcher.get_skill_suggestions(
                match_result['missing_skills'],
                resume.skills
            )
            for sugg in suggestions[:5]:
                st.info(sugg['suggestion'])

    # Next step button
    if st.button("💬 Continue to Chat & Modify", type="primary"):
        # Initialize chat service
        st.session_state.chat_service = ChatService(resume=resume, jd=jd)
        st.session_state.step = 3
        st.rerun()


def step3_chat():
    """Step 3: Interactive chat for modifications."""
    st.markdown('<div class="section-header">Step 3: Chat to Modify Your Resume</div>', unsafe_allow_html=True)

    st.info("💡 Ask questions or request changes to your resume. Examples: 'Change my email to...', 'Add skill: Docker', 'What experience do I have with Spark?'")

    # Display chat history
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI Assistant:** {message['content']}")
            st.markdown("---")

    # Chat input
    user_input = st.text_input("Type your message...", key="chat_input")

    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        if st.button("Send"):
            if user_input:
                # Add user message to history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input
                })

                # Check if it's a modification request first
                is_modification, mod_message, chat_response = ModificationHandler.process_user_request(
                    user_input,
                    st.session_state.resume
                )

                if is_modification:
                    # It's a modification - show modification result
                    full_response = mod_message
                    if chat_response:
                        full_response += f"\n\n{chat_response}"

                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': full_response
                    })
                else:
                    # Not a modification - use regular chat service
                    response = st.session_state.chat_service.ask(user_input)

                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })

                st.rerun()

    with col2:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.chat_service.clear_history()
            st.rerun()

    # Show current resume state
    with st.expander("📄 View Current Resume"):
        resume = st.session_state.resume
        st.json(resume.model_dump(), expanded=False)

    # Next step
    st.markdown("---")
    if st.button("✨ Generate Optimized Resume", type="primary"):
        st.session_state.step = 4
        st.rerun()


def step4_generate():
    """Step 4: Generate optimized resume."""
    st.markdown('<div class="section-header">Step 4: Generate Optimized Resume</div>', unsafe_allow_html=True)

    resume = st.session_state.resume
    jd = st.session_state.jd

    with st.spinner("🤖 Generating optimized resume with AI..."):
        generator = ResumeGenerator()

        optimized_resume = generator.generate_optimized_resume(
            resume=resume,
            jd=jd,
            optimize_summary=True,
            optimize_skills=True,
            optimize_all_experiences=True
        )

        st.session_state.optimized_resume = optimized_resume

        # Generate comparison report
        comparison = generator.generate_comparison_report(
            original_resume=resume,
            optimized_resume=optimized_resume,
            jd=jd
        )

    st.success("✅ Optimized resume generated successfully!")

    # Show comparison
    st.markdown("### 📊 Optimization Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Summary", "Optimized" if comparison['summary_changed'] else "Unchanged")

    with col2:
        st.metric("Skills Added", len(comparison['skills_added']))

    with col3:
        st.metric("Experience Sections Optimized", len(comparison['experience_changes']))

    # Show details
    with st.expander("📝 View Changes"):
        if comparison['summary_changed']:
            st.markdown("**✓ Professional Summary:** Optimized")

        if comparison['skills_added']:
            st.markdown(f"**✓ Skills Added ({len(comparison['skills_added'])}):**")
            for skill in comparison['skills_added'][:10]:
                st.write(f"• {skill}")

        if comparison['experience_changes']:
            st.markdown(f"**✓ Experience Sections Optimized:**")
            for change in comparison['experience_changes']:
                st.write(f"• {change['company']}: {change['original_bullets']} → {change['optimized_bullets']} bullets")

    # Preview optimized resume
    with st.expander("👁️ Preview Optimized Resume"):
        st.json(optimized_resume.model_dump(), expanded=False)

    # Next step
    if st.button("📥 Continue to Export Options", type="primary"):
        st.session_state.step = 5
        st.rerun()


def step5_export():
    """Step 5: Export options and downloads."""
    st.markdown('<div class="section-header">Step 5: Export & Download</div>', unsafe_allow_html=True)

    resume = st.session_state.optimized_resume or st.session_state.resume
    jd = st.session_state.jd

    # Export options
    st.markdown("### 📦 Select Export Options")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Resume Export")
        export_original = st.checkbox("Original Resume (DOCX)")
        export_optimized = st.checkbox("Optimized Resume with Bold Keywords (DOCX)", value=True)
        export_json = st.checkbox("Resume Data (JSON)")

    with col2:
        st.markdown("#### Cover Letter Export")
        export_cl_professional = st.checkbox("Professional Style Cover Letter")
        export_cl_enthusiastic = st.checkbox("Enthusiastic Style Cover Letter")
        export_cl_concise = st.checkbox("Concise Style Cover Letter")
        export_combined = st.checkbox("Combined (Cover Letter + Resume)")

    # ATS Score option
    st.markdown("---")
    show_ats = st.checkbox("📊 Calculate ATS Score", value=False)

    if show_ats:
        with st.spinner("Calculating ATS score..."):
            generator = ResumeGenerator()
            ats_result = generator.calculate_ats_score(resume, jd)
            st.session_state.ats_result = ats_result

        st.markdown("### 📊 ATS Score Analysis")
        st.markdown(ats_result['analysis_text'])

    # Generate button
    if st.button("🚀 Generate Selected Exports", type="primary"):
        with st.spinner("Generating exports..."):
            output_dir = Path("output/streamlit_exports")
            output_dir.mkdir(parents=True, exist_ok=True)

            generated_files = []

            # Get base filename
            base_name = st.session_state.resume_filename if st.session_state.resume_filename else "resume"

            # Export resume
            if export_original:
                filename = f"{base_name}.docx"
                path = output_dir / filename
                DOCXExporter.export_resume(st.session_state.resume, str(path))
                generated_files.append((filename, path))

            if export_optimized:
                filename = f"{base_name}_optimized_resume.docx"
                path = output_dir / filename
                DOCXExporter.export_resume(
                    resume,
                    str(path),
                    bold_keywords=jd.required_skills[:15]
                )
                generated_files.append((filename, path))

            if export_json:
                filename = f"{base_name}_data.json"
                path = output_dir / filename
                with open(path, 'w') as f:
                    json.dump(resume.model_dump(), f, indent=2)
                generated_files.append((filename, path))

            # Export cover letters
            cover_letter_gen = CoverLetterGenerator()

            if export_cl_professional:
                cl_result = cover_letter_gen.generate_cover_letter(
                    resume, jd, CoverLetterStyle.PROFESSIONAL
                )
                filename = f"{base_name}_cover_letter_professional.docx"
                path = output_dir / filename
                DOCXExporter.export_cover_letter(
                    cl_result['cover_letter'],
                    resume.contact.full_name,
                    str(path)
                )
                generated_files.append((filename, path))

            if export_cl_enthusiastic:
                cl_result = cover_letter_gen.generate_cover_letter(
                    resume, jd, CoverLetterStyle.ENTHUSIASTIC
                )
                filename = f"{base_name}_cover_letter_enthusiastic.docx"
                path = output_dir / filename
                DOCXExporter.export_cover_letter(
                    cl_result['cover_letter'],
                    resume.contact.full_name,
                    str(path)
                )
                generated_files.append((filename, path))

            if export_cl_concise:
                cl_result = cover_letter_gen.generate_cover_letter(
                    resume, jd, CoverLetterStyle.CONCISE
                )
                filename = f"{base_name}_cover_letter_concise.docx"
                path = output_dir / filename
                DOCXExporter.export_cover_letter(
                    cl_result['cover_letter'],
                    resume.contact.full_name,
                    str(path)
                )
                generated_files.append((filename, path))

            if export_combined:
                cl_result = cover_letter_gen.generate_cover_letter(
                    resume, jd, CoverLetterStyle.PROFESSIONAL
                )
                filename = f"{base_name}_combined_application.docx"
                path = output_dir / filename
                DOCXExporter.export_combined(
                    resume,
                    cl_result['cover_letter'],
                    str(path),
                    bold_keywords=jd.required_skills[:15]
                )
                generated_files.append((filename, path))

            st.session_state.generated_files = generated_files

        st.success(f"✅ Generated {len(generated_files)} files!")

        # Download buttons
        st.markdown("### 📥 Download Your Files")

        for filename, filepath in generated_files:
            with open(filepath, 'rb') as f:
                st.download_button(
                    label=f"⬇️ Download {filename}",
                    data=f.read(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document" if filename.endswith('.docx') else "application/json"
                )

    # Done
    st.markdown("---")
    st.markdown('<div class="success-box">🎉 <b>All done!</b> Your resume is ready for submission.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
