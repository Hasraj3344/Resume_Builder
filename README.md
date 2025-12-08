# 🚀 AI-Powered Resume Builder

An intelligent resume optimization platform that uses LLMs, RAG, and semantic matching to help you create ATS-friendly, job-tailored resumes.

## ✨ Features

### Core Capabilities
- 📄 **Smart Resume Parsing** - Extracts structured data from PDF/DOCX resumes
- 🎯 **Intelligent Job Matching** - Analyzes how well your resume matches job descriptions
- 🤖 **LLM-Powered Optimization** - Uses GPT/Claude to enhance your resume
- 💬 **Interactive Chat** - Modify your resume through natural language
- 📊 **Semantic Search (RAG)** - Vector-based matching for deeper insights
- 🎨 **Professional Export** - Generate polished DOCX resumes
- 🧠 **GenAI Skills Section** - Dedicated parsing for AI/ML skills

### Advanced Features
- **Skill Gap Analysis** - Identifies missing skills from job requirements
- **Experience Optimization** - Rewrites bullets with metrics and impact
- **ATS Optimization** - Ensures your resume passes Applicant Tracking Systems
- **Cover Letter Generation** - Creates tailored cover letters
- **Resume Chat** - Ask questions about your experience and skills

---

## 🚀 Quick Start

### Option 1: Local Setup (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/Resume_Builder.git
cd Resume_Builder

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API key
cp .env.example .env
# Edit .env and add your OpenAI API key

# 4. Run the app
streamlit run app.py

# 5. Open http://localhost:8501
```

### Option 2: Docker (1 minute)

```bash
# Build and run
docker-compose up -d

# Open http://localhost:8501
```

### Option 3: Deploy to Cloud (FREE)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for Streamlit Cloud, AWS, GCP, Azure, and Heroku.

---

## 📋 Prerequisites

- Python 3.9+ 
- OpenAI API key OR Anthropic API key
- 2GB RAM minimum

---

## 🎯 Usage

### Streamlit Web App (Recommended)

```bash
streamlit run app.py
```

**Workflow:**
1. Upload your resume (PDF/DOCX)
2. Paste job description
3. Review skill match analysis
4. Chat to modify resume
5. Generate optimized version
6. Export to DOCX

### Command Line Interface

```bash
# Basic analysis
python main.py

# With semantic matching
python main.py --rag

# With LLM optimization
python main.py --rag --generate

# Interactive chat
python main.py --chat
```

---

## 🏗️ Project Structure

```
Resume_Builder/
├── src/
│   ├── parsers/          # Resume & JD parsing
│   │   ├── resume_parser.py
│   │   └── jd_parser.py
│   ├── analysis/         # Skill matching
│   │   └── skill_matcher.py
│   ├── rag/              # Vector embeddings & retrieval
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   ├── generation/       # LLM optimization
│   │   ├── generator.py
│   │   ├── prompts.py
│   │   └── llm_service.py
│   ├── chat/             # Interactive chat
│   │   ├── chat_service.py
│   │   └── modification_handler.py
│   ├── export/           # DOCX export
│   │   └── docx_formatter.py
│   └── models.py         # Pydantic data models
├── data/
│   ├── sample_resumes/   # Sample PDFs
│   ├── sample_jds/       # Sample job descriptions
│   └── vector_store/     # ChromaDB storage
├── output/               # Generated files
├── app.py               # Streamlit UI
├── main.py              # CLI entry point
└── requirements.txt     # Dependencies
```

---

## 🔑 API Key Setup

### OpenAI (Recommended)
1. Visit https://platform.openai.com/api-keys
2. Create new API key
3. Add to `.env`: `OPENAI_API_KEY=sk-proj-...`

**Cost:** ~$0.01-0.10 per resume (GPT-3.5/GPT-4)

### Anthropic Claude (Alternative)
1. Visit https://console.anthropic.com/settings/keys
2. Create new API key
3. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

**Test your setup:**
```bash
python test_api_key.py
```

---

## 🎨 Features Deep Dive

### 1. Resume Parsing
Extracts:
- Contact info (name, email, phone, LinkedIn, GitHub)
- Professional summary
- Work experience (company, title, dates, bullets)
- Education (degree, institution, GPA)
- Skills (technical + GenAI skills separately)
- Projects, certifications

### 2. Job Description Analysis
Extracts:
- Job title, company, location
- Required vs preferred skills
- Responsibilities
- Years of experience requirement
- Keywords for ATS optimization

### 3. Intelligent Matching
- **Keyword Matching:** Exact skill matches
- **Fuzzy Matching:** Similar skills (e.g., "React.js" → "React")
- **Experience Matching:** Skills found in experience bullets
- **Semantic Matching (RAG):** Vector similarity for context

### 4. LLM Optimization
- **Summary:** Rewritten for target role
- **Experience Bullets:** Enhanced with metrics and impact
- **Skills:** Prioritized and keyword-optimized
- **ATS-Friendly:** Removes tables, uses standard formatting

### 5. Interactive Chat
Modify your resume naturally:
```
"Change my years of experience to 5"
"Add skill: Docker"
"Update my email to john@example.com"
"What experience do I have with Python?"
```

---

## 📊 Technologies

| Category | Technology |
|----------|-----------|
| **LLMs** | OpenAI GPT-4, Claude 3.5 |
| **Embeddings** | Sentence Transformers |
| **Vector DB** | ChromaDB |
| **Parsing** | PyPDF2, python-docx |
| **Web UI** | Streamlit |
| **Data Models** | Pydantic |
| **Export** | python-docx |

---

## 🧪 Testing

```bash
# Test API key
python test_api_key.py

# Test parser
python test_parser_fixes.py

# Test modification flow
python test_modification_flow.py

# Test years preservation
python test_years_preservation.py

# Run full test suite
pytest
```

---

## 🐛 Troubleshooting

### "401 Unauthorized" Error
- Invalid API key → Check `.env` file
- Expired key → Generate new key at OpenAI/Anthropic

### "Module not found" Error
```bash
pip install -r requirements.txt --force-reinstall
```

### Parser Issues
- Ensure resume is PDF or DOCX format
- Check file isn't password-protected
- Verify text is selectable (not scanned image)

### Memory Issues
```bash
# Use smaller embedding model in .env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## 🚀 Deployment

**Easiest:** [Streamlit Cloud](https://share.streamlit.io) (FREE)
1. Push to GitHub
2. Connect repository
3. Add API key to secrets
4. Deploy!

**Other options:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Docker + Google Cloud Run
- AWS Elastic Beanstalk
- Azure App Service
- Heroku

---

## 📈 Roadmap

- [ ] Multi-resume comparison
- [ ] Job application tracker
- [ ] LinkedIn integration
- [ ] Resume scoring (0-100)
- [ ] A/B testing different versions
- [ ] Interview prep based on JD
- [ ] Salary insights
- [ ] Browser extension

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude
- Streamlit for the amazing framework
- ChromaDB for vector storage
- LangChain for RAG utilities

---

## 📞 Support

- 📧 Email: haswanthrajeshn@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/Resume_Builder/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/YOUR_USERNAME/Resume_Builder/discussions)

---

**⭐ If this helped you land an interview, give it a star!**

---

Made with ❤️ by Haswanth Rajesh
