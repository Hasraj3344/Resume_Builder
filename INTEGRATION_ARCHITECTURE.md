# Integration Architecture - Complete System Overview

## 🔄 How Everything Connects

This document explains how the **existing Resume_Builder modules** (`src/`, `data/`) integrate with the **new React frontend** (`frontend/`) via the **FastAPI backend** (`backend/`).

---

## 📊 Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE (React)                          │
│                                                                      │
│  Pages:                                                              │
│  ├── Registration (multi-step with resume upload)                   │
│  ├── Login                                                           │
│  ├── Dashboard (workflow selector)                                  │
│  ├── Manual Workflow (paste JD → optimize)                          │
│  ├── Adzuna Workflow (search jobs → match → optimize)               │
│  └── Profile                                                         │
│                                                                      │
│  Components:                                                         │
│  └── Shared (Button, Card, LoadingSpinner, Transition)              │
│                                                                      │
│  Services (Axios API calls):                                        │
│  ├── authService.js         → /api/auth/*                           │
│  ├── resumeService.js        → /api/resume/*                        │
│  ├── jobService.js           → /api/jobs/*                          │
│  └── generationService.js    → /api/generate/*                      │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       │ HTTP/JSON (REST API)
                       │
┌──────────────────────▼───────────────────────────────────────────────┐
│                    BACKEND LAYER (FastAPI)                           │
│                                                                      │
│  API Routers (backend/routers/):                                    │
│  ├── auth.py          → Authentication (login, register, logout)    │
│  ├── resume.py        → Resume upload, parse, update, delete        │
│  ├── jobs.py          → Adzuna search, job matching (FAISS)         │
│  └── generation.py    → Manual/Adzuna workflows, DOCX export        │
│                                                                      │
│  Services (backend/services/):                                      │
│  ├── resume_service.py      → Wraps src/parsers/resume_parser.py   │
│  ├── jd_service.py          → Wraps src/parsers/jd_parser.py        │
│  ├── matching_service.py    → Wraps src/analysis + src/rag          │
│  ├── generation_service.py  → Wraps src/generation + src/export     │
│  └── adzuna_service.py      → Adzuna API integration                │
│                                                                      │
│  Database (SQLAlchemy ORM):                                         │
│  ├── User (extended with phone, address, profile_pic, resume data) │
│  ├── Subscription (free/pro plans)                                  │
│  ├── UsageRecord (monthly limits)                                   │
│  ├── Resume (saved optimizations)                                   │
│  └── Session (JWT tracking)                                         │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       │ Python imports
                       │
┌──────────────────────▼───────────────────────────────────────────────┐
│               EXISTING MODULES (src/)                                │
│                                                                      │
│  Parsers (src/parsers/):                                            │
│  ├── resume_parser.py   → Extract data from PDF/DOCX resumes        │
│  └── jd_parser.py       → Parse job descriptions                    │
│                                                                      │
│  Analysis (src/analysis/):                                          │
│  └── skill_matcher.py   → Keyword matching with synonyms/abbrevs    │
│                                                                      │
│  Vector Store (src/vectorstore/):                                   │
│  ├── embeddings.py      → sentence-transformers/all-MiniLM-L6-v2    │
│  └── vector_db.py       → In-memory vector database                 │
│                                                                      │
│  RAG (src/rag/):                                                    │
│  └── retriever.py       → Semantic matching (66%+ similarity)       │
│                                                                      │
│  Generation (src/generation/):                                      │
│  ├── llm_service.py     → OpenAI/Anthropic API wrapper              │
│  ├── prompts.py         → WHR format templates (20-25 bullets)      │
│  └── generator.py       → Resume optimization orchestration         │
│                                                                      │
│  Export (src/export/):                                              │
│  └── docx_formatter.py  → ATS-friendly DOCX generation              │
│                                                                      │
│  Models (src/models.py):                                            │
│  └── Pydantic schemas (Resume, JobDescription, Experience, etc.)    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 **Integration Points**

### **1. Resume Upload & Parsing (Registration Step 2)**

**User Action:**
- User uploads resume in registration form

**Flow:**
```
Frontend (RegisterPage.jsx)
  └─> POST /api/resume/parse (FormData with resume file)
       └─> backend/routers/resume.py::parse_resume()
            └─> backend/services/resume_service.py::parse_resume()
                 └─> src/parsers/resume_parser.py::ResumeParser.parse_resume()
                      └─> Returns: Resume object (Pydantic)
                           └─> Converted to JSON dict
                                └─> Sent back to frontend
                                     └─> Frontend displays education, experience, skills
```

**Data Flow:**
```python
# resume_service.py uses existing parser
from src.parsers.resume_parser import ResumeParser

parser = ResumeParser()
resume: Resume = parser.parse_resume(file_path)  # From src/

# Convert Resume object to dict for JSON response
parsed_data = {
    "contact_info": {...},
    "education": [...],
    "experience": [...],
    "skills": [...],
    "projects": [...],
    "certifications": [...]
}
```

---

### **2. Manual Workflow (Paste JD → Optimize Resume)**

**User Action:**
- User pastes job description text
- Clicks "Optimize Resume"

**Flow:**
```
Frontend (ManualWorkflow.jsx)
  └─> POST /api/generate/manual { jd_text: "..." }
       └─> backend/routers/generation.py::generate_from_manual_jd()
            ├─> jd_service.parse_job_description(jd_text)
            │    └─> src/parsers/jd_parser.py::JDParser.parse()
            ├─> matching_service.calculate_match_score(resume, jd)
            │    ├─> src/analysis/skill_matcher.py::SkillMatcher.match_skills()
            │    └─> src/rag/retriever.py::RAGRetriever.retrieve_relevant_sections()
            ├─> generation_service.optimize_resume(resume, jd)
            │    └─> src/generation/generator.py::ResumeGenerator.optimize_resume()
            │         ├─> src/generation/llm_service.py (GPT-3.5)
            │         └─> src/generation/prompts.py (WHR templates)
            └─> generation_service.export_to_docx(optimized_resume)
                 └─> src/export/docx_formatter.py::DOCXFormatter.export_resume()
                      └─> Returns: DOCX file path
```

**Response:**
```json
{
  "original_resume": { ... },
  "optimized_resume": {
    "professional_summary": "Optimized...",
    "experience": [
      {
        "company": "...",
        "job_title": "...",
        "responsibilities": [
          "**Architected** end-to-end data pipelines...",  // Bold keywords
          "**Reduced** processing time by 40%..."          // Metrics added
        ]
      }
    ],
    "skills": { "Technical Skills": [...], "GenAI Skills": [...] }
  },
  "match_analysis": {
    "keyword_match": { "percentage": 75.5, ... },
    "semantic_match": { "percentage": 82.3, ... },
    "overall_score": 78.2
  },
  "docx_url": "/api/generate/download/resume_abc123.docx"
}
```

---

### **3. Adzuna Workflow (Search Jobs → Match → Optimize)**

**User Action:**
- User enters search filters (title, location, salary)
- Clicks "Search Jobs"

**Flow Part 1: Search & Match**
```
Frontend (AdzunaWorkflow.jsx)
  └─> POST /api/jobs/search { query: "data engineer", location: "Atlanta, GA", filters: {...} }
       └─> backend/routers/jobs.py::search_jobs()
            └─> backend/services/adzuna_service.py::search_jobs()
                 └─> Adzuna API call (HTTPS)
                      └─> Returns: List of 20 jobs

  └─> POST /api/jobs/match { resume_text: "...", jobs: [...] }
       └─> backend/routers/jobs.py::match_resume_to_jobs()
            └─> backend/services/matching_service.py::match_resume_to_jobs()
                 ├─> src/vectorstore/embeddings.py::create_embedding(resume)
                 ├─> For each job:
                 │    ├─> src/vectorstore/embeddings.py::create_embedding(job)
                 │    └─> Calculate cosine similarity
                 └─> Returns: Jobs sorted by similarity (>10%)
```

**Response:**
```json
[
  {
    "id": "adzuna_123456",
    "title": "Senior Data Engineer",
    "company": "TechCorp",
    "description": "...",
    "similarity_score": 85.5  // <-- Added by FAISS matching
  },
  ...
]
```

**Flow Part 2: User Selects Job → Optimize**
```
Frontend (JobCard.jsx - user clicks "Optimize Resume")
  └─> POST /api/generate/adzuna { job_id: "...", job_data: {...} }
       └─> backend/routers/generation.py::generate_from_adzuna_job()
            └─> Same flow as manual workflow (parse JD, match, optimize, export)
```

---

### **4. Skill Matching (Keyword + Semantic)**

**Integration:**
```python
# backend/services/matching_service.py

from src.analysis.skill_matcher import SkillMatcher
from src.rag.retriever import RAGRetriever

# Keyword matching (60% weight)
skill_match_result = SkillMatcher().match_skills(resume, jd)
# Returns: match_percentage, matched_skills, missing_skills

# Semantic matching (40% weight)
semantic_matches = RAGRetriever().retrieve_relevant_sections(resume, jd)
# Returns: List of (resume_section, jd_requirement, similarity_score)

# Combined score
overall_score = (keyword_match * 0.6) + (semantic_match * 0.4)
```

**Existing Features Used:**
- ✅ Abbreviation matching (ADF = Azure Data Factory)
- ✅ Synonym matching (Python = PySpark)
- ✅ Skills extracted from experience bullets
- ✅ RAG-based semantic similarity

---

### **5. Resume Optimization (LLM)**

**Integration:**
```python
# backend/services/generation_service.py

from src.generation.generator import ResumeGenerator
from src.generation.llm_service import get_default_llm_service

llm = get_default_llm_service()  # GPT-3.5-turbo
generator = ResumeGenerator(llm)

# Optimize using existing prompts (WHR format, 20-25 bullets)
optimized_resume = generator.optimize_resume(resume, jd)
```

**Existing Features Used:**
- ✅ WHR (What-How-Result) format
- ✅ 20-25 bullets per experience section
- ✅ Bold keywords using **markdown** syntax
- ✅ Metrics and quantification
- ✅ Skills optimization (preserves all original skills)
- ✅ Project optimization

---

### **6. DOCX Export (ATS-Friendly)**

**Integration:**
```python
# backend/services/generation_service.py

from src/export/docx_formatter import DOCXFormatter

formatter = DOCXFormatter()
formatter.export_resume(optimized_resume, output_path)
```

**Existing Features Used:**
- ✅ Clickable hyperlinks (GitHub, LinkedIn)
- ✅ Bold keyword formatting (parses **text**)
- ✅ Skills tables (Technical Skills + GenAI Skills)
- ✅ Text justification
- ✅ No bullet symbols (ATS-friendly)

---

## 📦 **Data Models Mapping**

### **Database → Pydantic → JSON**

```python
# User stores parsed resume data in JSON column
User.resume_parsed_data = {
    "contact_info": {...},
    "education": [...],
    "experience": [...],
    "skills": [...]
}

# When needed, convert to Pydantic Resume object
from src.models import Resume

resume = Resume(**user.resume_parsed_data)

# Pass to existing generators
optimized = generator.optimize_resume(resume, jd)

# Convert back to dict for JSON response
optimized_dict = {
    "professional_summary": optimized.professional_summary,
    "experience": [exp.dict() for exp in optimized.experience],
    ...
}
```

---

## 🔧 **Configuration & Dependencies**

### **Shared Dependencies**

Both backend and existing modules use:
- `openai` - GPT-3.5-turbo API
- `sentence-transformers` - all-MiniLM-L6-v2 embeddings
- `python-docx` - DOCX generation
- `pydantic` - Data validation

### **Environment Variables**

```env
# .env (shared)
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=...
ADZUNA_APP_ID=...
ADZUNA_APP_KEY=...

# Backend only
DATABASE_URL=sqlite:///./resume_builder.db
JWT_SECRET_KEY=...
```

---

## 📂 **File Organization**

```
Resume_Builder/
├── frontend/                  # NEW: React UI
│   ├── src/components/
│   ├── src/services/          # Axios API calls
│   └── src/context/
│
├── backend/                   # NEW: FastAPI backend
│   ├── routers/               # API endpoints
│   ├── services/              # 🔗 Integration layer (uses src/)
│   ├── models/                # Database models
│   └── main.py
│
├── src/                       # EXISTING: Core modules
│   ├── parsers/               # ✅ Used by resume_service.py
│   ├── analysis/              # ✅ Used by matching_service.py
│   ├── vectorstore/           # ✅ Used by matching_service.py
│   ├── rag/                   # ✅ Used by matching_service.py
│   ├── generation/            # ✅ Used by generation_service.py
│   ├── export/                # ✅ Used by generation_service.py
│   └── models.py              # ✅ Pydantic schemas
│
├── data/                      # EXISTING: Sample files
│   ├── sample_resumes/        # Used for testing
│   └── sample_jds/            # Used for testing
│
├── output/                    # Generated files (DOCX)
└── resume_builder.db          # SQLite database
```

---

## 🚀 **Testing the Integration**

### **Test Resume Parsing**

```bash
# 1. Start backend
python -m uvicorn backend.main:app --reload

# 2. Test endpoint
curl -X POST http://localhost:8000/api/resume/parse \
  -F "resume=@data/sample_resumes/Haswanth_Data_Engineer_Profile.pdf"

# Should return:
{
  "contact_info": {"name": "Haswanth", "email": "...", ...},
  "education": [...],
  "experience": [...],
  "skills": [...]
}
```

### **Test Manual Workflow**

```bash
curl -X POST http://localhost:8000/api/generate/manual \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "jd_text": "We are looking for a Data Engineer with Python, Spark, and AWS experience..."
  }'

# Should return optimized resume + match analysis + DOCX URL
```

### **Test Adzuna Search**

```bash
curl -X POST http://localhost:8000/api/jobs/search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "data engineer",
    "location": "Atlanta, GA",
    "filters": {"salary_min": 80000}
  }'

# Should return list of jobs from Adzuna
```

---

## ✅ **Integration Checklist**

- [x] Backend service layer created (resume, jd, matching, generation, adzuna)
- [x] API routers created (resume, jobs, generation)
- [x] Main.py updated with new routers
- [x] User model extended (phone, address, resume_parsed_data)
- [x] Existing modules imported correctly (`sys.path.insert`)
- [ ] Database migration script (add new User columns) ⚠️ **TODO**
- [ ] File upload handling (save to uploads/) ⚠️ **TODO**
- [ ] Frontend services created (resumeService, jobService, generationService) ⚠️ **TODO**
- [ ] Workflow UI pages (ManualWorkflow, AdzunaWorkflow) ⚠️ **TODO**

---

## 🎯 **Next Steps**

### **Immediate (Required for Registration):**
1. **Database Migration**:
   ```bash
   # Create migration script
   backend/migrations/002_add_user_fields.sql
   ```
   ```sql
   ALTER TABLE users ADD COLUMN phone VARCHAR(50);
   ALTER TABLE users ADD COLUMN address TEXT;
   ALTER TABLE users ADD COLUMN profile_pic_path VARCHAR(500);
   ALTER TABLE users ADD COLUMN resume_file_path VARCHAR(500);
   ALTER TABLE users ADD COLUMN resume_text TEXT;
   ALTER TABLE users ADD COLUMN resume_parsed_data JSON;
   ```

2. **Test Registration Flow**:
   - Start backend: `python -m uvicorn backend.main:app --reload`
   - Start frontend: `cd frontend && npm start`
   - Register new user with resume
   - Verify data in database: `sqlite3 resume_builder.db "SELECT * FROM users;"`

### **Next (Build Workflows):**
3. Create frontend workflow pages
4. Create frontend service files
5. Test end-to-end flows

---

**Last Updated:** 2025-12-16
**Integration Status:** 80% Complete (services ready, needs testing)
