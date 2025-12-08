# Resume Builder RAG Pipeline - Project Context

## Project Status: Phase 4 Complete ✓

This document helps you (or Claude) resume work on this project from the current state.

---

## What Has Been Built

### ✅ Phase 1: Document Processing (COMPLETE)
- **Resume Parser** (`src/parsers/resume_parser.py`): Extracts structured data from PDF/DOCX resumes
- **Job Description Parser** (`src/parsers/jd_parser.py`): Parses JD files for requirements and skills
- **Intelligent Skill Matcher** (`src/analysis/skill_matcher.py`):
  - Handles abbreviations (ADF = Azure Data Factory, CI/CD, ETL, etc.)
  - Matches skills from both skills section AND experience bullets
  - Fuzzy matching with synonyms and variations
- **Data Models** (`src/models.py`): Pydantic schemas for Resume, JobDescription, Experience, etc.

**Result:** 60.9% keyword match score on real resume vs real JD

### ✅ Phase 2: Semantic Matching with RAG (COMPLETE)
- **Embedding Service** (`src/vectorstore/embeddings.py`): Uses sentence-transformers/all-MiniLM-L6-v2
- **Vector Store** (`src/vectorstore/vector_db.py`): In-memory vector store with cosine similarity
- **RAG Retriever** (`src/rag/retriever.py`): Semantic matching between resume sections and JD requirements

**Result:** 66.8% semantic similarity, showing which experience bullets match which JD requirements

### ✅ Phase 3: LLM-Powered Resume Generation (COMPLETE)
- **LLM Service** (`src/generation/llm_service.py`): Supports OpenAI and Anthropic APIs
- **Prompt Templates** (`src/generation/prompts.py`): STAR-method prompts for optimization
- **Resume Generator** (`src/generation/generator.py`): Orchestrates LLM-based optimization

**Current Model:** gpt-3.5-turbo (switched from gpt-4 due to API access)

**Capabilities:**
- Optimizes professional summary with JD keywords
- Rewrites experience bullets using STAR method
- Adds metrics and quantification
- Optimizes skills section with missing keywords
- Generates comparison report

### ✅ Phase 4: Interactive Chat Interface (COMPLETE)
- **Chat Prompts** (`src/generation/chat_prompts.py`): Specialized prompts for different question types
- **Chat Service** (`src/chat/chat_service.py`): RAG-powered Q&A system with conversation history
- **Interactive CLI** (`chat.py` and integrated into `main.py --chat`): User-friendly chat interface

**Question Types Supported:**
1. **Skill Questions**: "What experience do I have with Spark?"
2. **Experience Questions**: "Tell me about my data engineering projects"
3. **Match Questions**: "How well do I match this job description?"
4. **Suggestion Questions**: "What skills should I add to my resume?"
5. **General Questions**: "What are my key strengths?"

**Features:**
- Automatic question type classification
- RAG-based context retrieval (finds most relevant resume sections)
- Conversation history tracking for follow-up questions
- LLM-generated natural language answers
- Works with or without job description

---

## Current Project Structure

```
Resume_Builder/
├── src/
│   ├── models.py                    # Pydantic data models
│   ├── parsers/
│   │   ├── resume_parser.py         # PDF/DOCX resume parser
│   │   └── jd_parser.py             # Job description parser
│   ├── analysis/
│   │   └── skill_matcher.py         # Intelligent skill matching
│   ├── vectorstore/
│   │   ├── embeddings.py            # sentence-transformers embeddings
│   │   └── vector_db.py             # In-memory vector store
│   ├── rag/
│   │   └── retriever.py             # RAG-based semantic matching
│   ├── generation/
│   │   ├── llm_service.py           # OpenAI/Anthropic integration
│   │   ├── prompts.py               # STAR-method prompt templates
│   │   ├── chat_prompts.py          # Chat Q&A prompt templates
│   │   └── generator.py             # Resume optimization logic
│   └── chat/
│       ├── chat_service.py          # Interactive Q&A service
│       └── __init__.py
├── data/
│   ├── sample_resumes/
│   │   └── Haswanth_Data_Engineer_Profile.pdf
│   └── sample_jds/
│       └── sample_jd.txt
├── output/                          # Generated JSON files
│   ├── resume.json
│   ├── job_description.json
│   └── optimized_resume.json
├── .env                             # API keys (gitignored)
├── .env.example                     # Template for API keys
├── main.py                          # Main CLI application
├── test_api_key.py                  # Test API key setup
├── requirements.txt
└── claude.md                        # This file
```

---

## How to Run

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key in .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY or ANTHROPIC_API_KEY
```

### Running Each Phase

**Phase 1 Only (Keyword Matching):**
```bash
python main.py
```
- Parses resume and JD
- Shows intelligent keyword match (60.9% for current files)
- Matches skills from both skills section and experience bullets
- Exports to `output/resume.json` and `output/job_description.json`

**Phase 2 (Semantic Matching with RAG):**
```bash
python main.py --rag
```
- Everything from Phase 1
- Generates embeddings for resume and JD sections
- Shows semantic similarity matches (66.8%)
- Displays which experience bullets match which JD requirements

**Phase 3 (LLM Generation):**
```bash
python main.py --rag --generate
```
- Everything from Phases 1 & 2
- Optimizes professional summary
- Rewrites top 3 experience sections with STAR method
- Optimizes skills section with missing keywords
- Exports to `output/optimized_resume.json`

**Phase 4 (Interactive Chat):**
```bash
python main.py --chat
```
- Interactive Q&A about your resume
- Ask natural language questions
- Get instant answers powered by RAG + LLM
- Conversation history tracking
- Example questions:
  - "What experience do I have with Spark?"
  - "How well do I match this job?"
  - "What skills should I add?"

**Alternative Chat Interface:**
```bash
python chat.py
```
- Standalone chat interface with more features
- Commands: /help, /examples, /history, /exit

**Test API Key Setup:**
```bash
python test_api_key.py
```

**Test Chat Functionality:**
```bash
python test_chat.py
```

---

## API Configuration

### Current Setup (.env file)
```env
# OpenAI (ACTIVE - using gpt-3.5-turbo)
OPENAI_API_KEY=sk-proj-...  # ✓ Working

# Anthropic (placeholder)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Models
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=gpt-4-turbo-preview  # Note: Not used, hardcoded in llm_service.py
```

### Important Notes:
- **Model Used:** gpt-3.5-turbo (hardcoded in `src/generation/llm_service.py:46` and `:239`)
- **Why gpt-3.5-turbo:** User's OpenAI project doesn't have access to gpt-4
- **Cost:** ~$0.002 per 1K tokens (very affordable with $9 credit)
- **Provider Selection:** Checks for valid API keys (not placeholders) via `get_default_llm_service()`

---

## Key Problems Solved

### 1. Resume Parser Accuracy
**Issue:** Wrong companies, incomplete bullets, tech names in location field
**Fix:**
- Improved job title regex pattern
- Multi-line bullet continuation logic
- Better contact info extraction (LinkedIn, GitHub, location)

### 2. Abbreviation Matching
**Issue:** "Azure Data Factory (ADF)" in resume not matching "ADF" in JD
**Fix:** Created `SkillMatcher` with abbreviation mapping and synonym support

### 3. Hidden Skills in Experience
**Issue:** Skills mentioned in bullet points not counted
**Fix:** Extract skills from experience text, not just skills section

### 4. ChromaDB Python 3.8 Compatibility
**Issue:** Type hint errors in ChromaDB telemetry module
**Fix:** Built custom in-memory vector store using numpy

### 5. GPT-4 Access Denied
**Issue:** 403 error - User's project doesn't have GPT-4 access
**Fix:** Switched to gpt-3.5-turbo in `llm_service.py`

### 6. API Key Not Loading
**Issue:** "LLM client not initialized" despite .env file
**Fix:** Added `load_dotenv()` at top of `llm_service.py`

---

## Current Output Examples

### Keyword Matching Results
```
✓ MATCHED REQUIRED SKILLS (14/23): 60.9%
  From Skills Section (9):
    ✓ Python → matched as 'Python (PySpark)'
    ✓ Azure → matched as 'Azure Data Factory (ADF)'
    ✓ ADF (found in experience)
    ...

  From Experience Bullets (5):
    ✓ Azure cloud
    ✓ CI/CD
    ✓ ETL
```

### Semantic Matching Results
```
Responsibility: Design, develop, and maintain scalable data pipelines...
↓ Similarity: 79.61%
✓ Matched: Designed and developed end-to-end data pipelines using Databricks...
```

### LLM Optimization Example
**Original Bullet:**
> "Designed and developed end-to-end data pipelines using Databricks, PySpark, and Delta Lake for enterprise data integration."

**Optimized Bullet:**
> "Architected end-to-end data pipelines in Databricks, PySpark, and Delta Lake, reducing data processing time by 40%."

**Changes:**
- Stronger action verb (Architected vs Designed)
- Added metric (40% reduction)
- More concise

---

## Sample Files Being Used

### Resume
- **File:** `data/sample_resumes/Haswanth_Data_Engineer_Profile.pdf`
- **Profile:** Real resume with 2 Azure Data Engineer positions at DatafactZ
- **Skills:** 83 skills including Databricks, PySpark, Azure, SQL, ADF, etc.

### Job Description
- **File:** `data/sample_jds/sample_jd.txt`
- **Role:** Senior Data Engineer
- **Location:** Atlanta, GA / Chicago, IL
- **Required Skills:** 23 (Python, Azure, SQL, Spark, Databricks, Tableau, Power BI, etc.)

---

## Next Phase Options

### Phase 5: Cover Letter Generation ⭐ RECOMMENDED NEXT
Generate tailored cover letters based on:
- Resume content
- Job description
- Semantic matching results

### Phase 6: DOCX Export
Export optimized resume to formatted Word document:
- Professional formatting
- ATS-friendly layout
- Preserve structure and styling
- Ready to submit

### Phase 7: Multi-Resume Management
Manage multiple resume versions for different job types:
- Software Engineer version
- Data Engineer version
- ML Engineer version

### Phase 8: Web UI with Streamlit
Build interactive web interface:
- Upload resume and JD
- Real-time matching scores
- Side-by-side comparison
- One-click optimization

---

## Known Issues & Limitations

### Minor Issues
1. **Skills Section Formatting:** LLM sometimes outputs skills with category labels mixed in (e.g., "Technical Python (PySpark)", "Data Engineering Data Modeling")
   - **Impact:** Low - content is correct, just needs cleaning
   - **Fix:** Add post-processing to clean skill names

2. **Projects Section Parsing:** Projects section gets fragmented during PDF parsing
   - **Impact:** Medium - projects not structured properly
   - **Fix:** Improve resume parser's project detection

### Working As Expected
- ✅ Keyword matching with abbreviations
- ✅ Semantic similarity with RAG
- ✅ LLM optimization with gpt-3.5-turbo
- ✅ Experience bullet optimization
- ✅ Summary optimization
- ✅ JSON export

---

## Code Reference Guide

### To Modify LLM Model
Edit `src/generation/llm_service.py`:
- Line 46: Default model in `__init__`
- Line 239: Model in `get_default_llm_service()`

### To Adjust Skill Matching
Edit `src/analysis/skill_matcher.py`:
- `SKILL_ABBREVIATIONS`: Add new abbreviation mappings
- `SKILL_SYNONYMS`: Add new synonym groups
- `COMMON_SKILLS`: Expand skills library

### To Customize Prompts
Edit `src/generation/prompts.py`:
- `get_bullet_rewrite_prompt()`: Single bullet optimization
- `get_multi_bullet_optimization_prompt()`: Full experience section
- `get_summary_optimization_prompt()`: Professional summary
- `get_skills_optimization_prompt()`: Skills section

### To Change Embedding Model
Edit `src/vectorstore/embeddings.py`:
- Line 13: `model_name` parameter
- Alternative models:
  - `all-MiniLM-L6-v2` (384 dim) - Current, fast
  - `all-mpnet-base-v2` (768 dim) - More accurate, slower

---

## Important Commands

```bash
# Run Phase 3 (full pipeline)
python main.py --rag --generate

# Test API key
python test_api_key.py

# Check what files were generated
ls -la output/

# View optimized resume
cat output/optimized_resume.json | python -m json.tool | less

# Compare original vs optimized
diff <(cat output/resume.json | python -m json.tool) \
     <(cat output/optimized_resume.json | python -m json.tool)
```

---

## Environment

- **Python Version:** 3.8+ (tested on Python 3.8)
- **OS:** macOS (Darwin 25.1.0)
- **Working Directory:** `/Users/hasraj/Resume_Builder`
- **API Budget:** $9 OpenAI credit remaining

---

## Quick Start for New Session

If you're starting a new conversation with Claude:

1. Share this `claude.md` file
2. Mention which phase you want to work on
3. Claude will have full context of:
   - What's been built
   - Current issues
   - File structure
   - How everything works

**Example prompt:**
> "I'm continuing work on the Resume Builder project. I've shared claude.md which has the full context. I want to implement Phase 6 (DOCX Export) next."

---

## Testing Checklist

To verify everything works after making changes:

```bash
# ✅ Test Phase 1 (keyword matching)
python main.py
# Should show: 60.9% match score

# ✅ Test Phase 2 (semantic matching)
python main.py --rag
# Should show: 66.8% semantic similarity

# ✅ Test Phase 3 (LLM generation)
python main.py --rag --generate
# Should generate optimized_resume.json

# ✅ Verify API key
python test_api_key.py
# Should show: ✓ OpenAI API Key: Configured

# ✅ Check outputs
ls output/
# Should see: resume.json, job_description.json, optimized_resume.json
```

---

## Git Status

**Repository:** Not initialized as git repo yet
**Recommendation:** Initialize git and commit current working state:

```bash
git init
git add .
git commit -m "Phase 3 complete - LLM generation working with gpt-3.5-turbo"
```

---

## Session Continuity Tips

### For User
- Keep this `claude.md` file updated when phases are completed
- Add new issues/fixes to "Known Issues" section
- Update "Next Phase Options" when deciding direction

### For Claude
- Read this file first when resuming work
- Update this file when completing new phases
- Document any new issues discovered
- Keep the "Current Status" section accurate

---

**Last Updated:** Phase 4 completion (Interactive Chat)
**Next Recommended Phase:** Phase 5 (Cover Letter Generation) or Phase 6 (DOCX Export)
**Status:** All systems operational ✅

## Phase 4 Testing Results

All question types tested successfully:
- ✅ Skill questions: Correctly identifies related skills and experience
- ✅ Experience questions: Retrieves relevant projects and achievements
- ✅ Match questions: Analyzes resume vs JD with specific recommendations
- ✅ Suggestion questions: Provides actionable skill improvement advice
- ✅ General questions: Summarizes strengths with conversation context

**Test Command:** `python test_chat.py`
