# Resume Builder RAG Pipeline - Project Context

## Project Status: Phase 8 Complete ✓ (Authentication Backend)

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
- **Modification Handler** (`src/chat/modification_handler.py`): Natural language resume modifications

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
- Live resume modifications via natural language

### ✅ Phase 5: DOCX Export (COMPLETE)
- **DOCX Formatter** (`src/export/docx_formatter.py`): Professional Word document export
- **ATS-Friendly Formatting**: Optimized for Applicant Tracking Systems

**Features:**
- ✅ **Clickable Hyperlinks**: GitHub and LinkedIn are clickable blue links
- ✅ **Bold Keyword Formatting**: Parses **markdown** syntax to actual bold
- ✅ **Skills Tables**: Two separate 2-column tables (Technical Skills + GenAI Skills)
- ✅ **Text Justification**: Professional justified text throughout
- ✅ **No Bullet Symbols**: Plain text bullets for ATS compatibility
- ✅ **Structured Sections**: Contact info, summary, experience, projects, skills, education
- ✅ **Professional Styling**: Consistent fonts, spacing, and color scheme

**Export Command:**
```bash
python main.py --rag --generate  # Exports to output/optimized_resume.docx
```

### ✅ Phase 6: Enhanced Chat Modifications (COMPLETE)
- **Education Field Modifications**: Update education details via chat
- **Automatic Application**: Modifications applied to resume generation

**Supported Modifications:**
- Email, phone, name, location
- GitHub and LinkedIn links (auto-formatted to full URLs)
- Years of experience (extracted from summary with regex patterns)
- Skills (add new skills to list)
- Education location, GPA, degree, field of study, graduation date

**Example Commands:**
- "Change my email to john@example.com"
- "My GitHub link is username" → Converts to https://github.com/username
- "Update years of experience to 5"
- "My education location is New York, NY"
- "Set my GPA to 3.85"

### ✅ Phase 7: Project Optimization (COMPLETE)
- **Project Optimization Function** (`generator.py:optimize_project()`): Optimizes project sections like experience bullets

**Features:**
- Generates 5-8 optimized bullets per project using WHR (What-How-Result) format
- Incorporates JD technologies and keywords
- Bold keywords using **markdown** syntax
- Quantifies achievements with metrics
- ATS-friendly formatting (no symbols, 20-25 bullets)

### ✅ Phase 8: User Authentication & Subscription Backend (COMPLETE)
- **FastAPI Backend** (`backend/main.py`): REST API for authentication and subscription management
- **SQLite Database** (`resume_builder.db`): Free-tier database with 5 tables (users, subscriptions, usage_records, resumes, sessions)
- **JWT Authentication** (`backend/utils/security.py`): Secure token-based authentication with bcrypt password hashing
- **Authentication Endpoints** (`backend/routers/auth.py`): Register, login, logout, and user info endpoints
- **Database Models** (`backend/models/`): SQLAlchemy ORM models for all entities
- **Session Management**: Token tracking and revocation in database

**Architecture:**
- **Backend Framework**: FastAPI with async support
- **Database**: SQLite (FREE tier, <1000 users, seamless migration to PostgreSQL later)
- **Authentication**: JWT tokens with 1-hour expiration, bcrypt password hashing
- **Session Tracking**: Database-backed token revocation
- **CORS**: Configured for Streamlit frontend (localhost:8501)

**API Endpoints:**
- `POST /api/auth/register` - User registration with auto free subscription
- `POST /api/auth/login` - Login with JWT token generation
- `POST /api/auth/logout` - Logout with session revocation
- `POST /api/auth/logout-session` - Revoke specific session
- `GET /api/auth/me` - Get current user info (protected)
- `GET /` - API status check
- `GET /health` - Health check with database status

**Database Schema (SQLite):**
- **users**: User accounts (id, email, password_hash, full_name, is_active, created_at)
- **subscriptions**: Plan management (id, user_id, plan_type, status, paypal_subscription_id, start_date, next_billing_date)
- **usage_records**: Monthly usage tracking (id, user_id, month_year, resumes_generated, reset_date)
- **resumes**: Generated resumes (id, user_id, filename, resume_data, job_description_data, optimized_resume_data, file_path, created_at)
- **sessions**: JWT session tracking (id, user_id, token_jti, expires_at, revoked, created_at)

**Subscription Plans:**
- **Free Tier**: 3 resumes/month, basic features
- **Pro Tier**: Unlimited resumes, $9.99/month (PayPal integration pending)

**Cost Strategy:**
- **MVP Phase**: $0/month infrastructure (SQLite + Railway Free Tier)
- **API Costs**: ~$6/month (OpenAI for 300 resumes)
- **Break-even**: Just 1 pro user ($9.99) covers all costs
- **Migration Path**: SQLite → PostgreSQL when >500 users

**Security Features:**
- ✅ Bcrypt password hashing (cost factor 12)
- ✅ JWT tokens with expiration and JTI tracking
- ✅ Session revocation in database
- ✅ Protected endpoints with Bearer token authentication
- ✅ CORS whitelist for Streamlit origin
- ✅ SQLAlchemy ORM (SQL injection prevention)
- ✅ Input validation with Pydantic schemas

**Testing Results:**
- ✅ User registration: Creates user + free subscription
- ✅ User login: Generates JWT token + user info
- ✅ Protected endpoints: Correctly validates tokens
- ✅ Logout: Revokes all user sessions
- ✅ Token revocation: Rejects revoked tokens (401)
- ✅ Database integrity: All tables created, relationships working

**Files Created:**
```
backend/
├── main.py                          # FastAPI app entry point
├── config.py                        # Settings and environment variables
├── database.py                      # SQLAlchemy connection
├── dependencies.py                  # Auth middleware (get_current_user)
├── models/
│   ├── user.py                      # User model
│   ├── subscription.py              # Subscription model
│   ├── usage.py                     # Usage tracking model
│   ├── resume.py                    # Resume storage model
│   └── session.py                   # Session tracking model
├── schemas/
│   └── auth.py                      # Pydantic request/response schemas
├── routers/
│   ├── __init__.py
│   └── auth.py                      # Authentication endpoints
├── services/
│   └── auth_service.py              # Authentication business logic
└── utils/
    └── security.py                  # JWT + bcrypt utilities

requirements_backend.txt             # Backend dependencies
test_auth_endpoints.py               # Authentication testing script
resume_builder.db                    # SQLite database (60KB)
```

**Dependencies Added:**
- fastapi>=0.109.0
- uvicorn[standard]>=0.27.0
- sqlalchemy>=2.0.0
- python-jose[cryptography]>=3.3.0
- passlib[bcrypt]>=1.7.4
- bcrypt==4.1.3 (pinned for compatibility)
- email-validator>=2.1.0
- pydantic-settings>=2.1.0

**Known Issues Fixed:**
1. ✅ **Pydantic validation error** - Added `extra = "allow"` to Config class
2. ✅ **Python 3.8 type hints** - Changed `tuple[...]` to `Tuple[...]`
3. ✅ **email-validator missing** - Added to requirements
4. ✅ **bcrypt compatibility** - Downgraded to 4.1.3 for passlib support

**Next Steps:**
- Create usage tracking service (check limits, increment usage)
- Create PayPal integration service (subscription creation, webhooks)
- Create resume generation API endpoints (integrate existing src/ modules)
- Modify Streamlit app with login/register pages
- Add API call wrapper in Streamlit with token management

---

## Recent Enhancements (Phases 5-7)

### ATS Optimization
- ✅ Changed from STAR to WHR (What-How-Result) format
- ✅ Increased bullets from 5-7 to 20-25 per experience section
- ✅ Removed bullet symbols (• → plain text)
- ✅ Bold keywords using **markdown** syntax
- ✅ All prompts updated for ATS compatibility

### DOCX Export Quality
- ✅ **Hyperlinks**: GitHub/LinkedIn clickable (not "GitHub: link")
- ✅ **Bold Formatting**: **text** renders as actual bold, not literal asterisks
- ✅ **Skills Tables**: Two separate tables (Technical + GenAI)
- ✅ **Text Justification**: Professional justified text throughout
- ✅ **Professional Layout**: Consistent fonts, spacing, colors

### Skills Preservation
- ✅ **100% Skill Retention**: All original skills preserved
- ✅ **Category Organization**: Skills grouped by category in tables
- ✅ **Parser Fix**: `_parse_skills_from_response()` preserves structure
- ✅ **Prompt Updates**: "Reorganize" not "Remove irrelevant"

### Chat Enhancements
- ✅ **Education Fields**: Location, GPA, degree, field of study, graduation date
- ✅ **Years Extraction Fix**: Correctly extracts years from complex phrases
- ✅ **Safety Checks**: Validates education list before modifications
- ✅ **Auto-Formatting**: GitHub/LinkedIn usernames → full URLs

### Project Optimization
- ✅ **New Function**: `optimize_project()` in generator.py
- ✅ **WHR Format**: 5-8 bullets per project
- ✅ **JD Integration**: Incorporates job technologies
- ✅ **Metrics**: Quantifies achievements

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
│   │   ├── prompts.py               # WHR-method prompt templates (ATS-optimized)
│   │   ├── chat_prompts.py          # Chat Q&A prompt templates
│   │   └── generator.py             # Resume optimization logic
│   ├── chat/
│   │   ├── chat_service.py          # Interactive Q&A service
│   │   ├── modification_handler.py  # Natural language modifications
│   │   └── __init__.py
│   └── export/
│       └── docx_formatter.py        # DOCX export with ATS-friendly formatting
├── backend/                         # FastAPI backend (Phase 8)
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # Settings and environment variables
│   ├── database.py                  # SQLAlchemy connection
│   ├── dependencies.py              # Auth middleware
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                  # User model
│   │   ├── subscription.py          # Subscription model
│   │   ├── usage.py                 # Usage tracking model
│   │   ├── resume.py                # Resume storage model
│   │   └── session.py               # Session tracking model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── auth.py                  # Auth request/response schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py                  # Authentication endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth_service.py          # Authentication business logic
│   └── utils/
│       ├── __init__.py
│       └── security.py              # JWT + bcrypt utilities
├── data/
│   ├── sample_resumes/
│   │   └── Haswanth_Data_Engineer_Profile.pdf
│   └── sample_jds/
│       └── sample_jd.txt
├── output/                          # Generated files
│   ├── resume.json
│   ├── job_description.json
│   ├── optimized_resume.json
│   └── optimized_resume.docx        # ATS-friendly Word document
├── .env                             # API keys + backend config (gitignored)
├── .env.example                     # Template for API keys
├── main.py                          # Main CLI application
├── chat.py                          # Standalone chat interface
├── test_api_key.py                  # Test API key setup
├── test_auth_endpoints.py           # Test authentication endpoints
├── requirements.txt                 # Frontend dependencies
├── requirements_backend.txt         # Backend dependencies
├── resume_builder.db                # SQLite database (60KB)
└── CLAUDE.md                        # This file
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

# Backend Authentication (Phase 8)
DATABASE_URL=sqlite:///./resume_builder.db
JWT_SECRET_KEY=fa194adc3e0b204f019c7615488c6c9e7af78546198bc613b1bb8e34d6f6a2fd  # 256-bit random key

# PayPal Configuration (Sandbox for testing)
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_paypal_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_paypal_sandbox_client_secret
PAYPAL_PRO_PLAN_ID=P-xxxxxxxxxxxx
```

**Generate New JWT Secret:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
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

### 7. ATS Compatibility Issues
**Issue:** Generated resumes not ATS-friendly (bullet symbols •, only 5-7 bullets, unclear bold formatting)
**Fix:** Updated all 8 prompts in `prompts.py`:
- Removed bullet symbols (ATS can't parse them)
- Increased bullets from 5-7 to 20-25 per experience
- Clarified bold formatting using **keyword** syntax
- Emphasized Word compatibility

### 8. Contact Info Not Clickable
**Issue:** GitHub and LinkedIn showing as "GitHub: link" instead of clickable hyperlinks
**Fix:** Created `_add_hyperlink()` method in `docx_formatter.py` using OxmlElement
- Generates proper clickable blue hyperlinks in Word
- Auto-formats partial URLs to full https:// URLs

### 9. Bold Keywords Showing ** Symbols
**Issue:** **keyword** syntax showing literal asterisks instead of bold in DOCX
**Fix:** Created `_add_text_with_markdown_bold()` parser in `docx_formatter.py`
- Parses **text** markdown syntax
- Applies actual bold formatting to runs
- Updated all text rendering methods

### 10. Skills Missing (70% Lost)
**Issue:** Only 10-20 skills showing in output, 70% missing from original resume
**Fix:** Updated prompts to "PRESERVE ALL ORIGINAL SKILLS" instead of "Remove irrelevant skills"
- Changed from filtering to reorganizing by category
- Skills now organized but not removed

### 11. Skills in Paragraph Format
**Issue:** Skills showing as comma-separated paragraph instead of table
**Fix:**
- Created `_parse_skills_categories()` in `docx_formatter.py`
- Renders 2-column table (Category | Skills)
- Fixed `_parse_skills_from_response()` in `generator.py` to preserve category structure

### 12. Years of Experience Extraction Bug
**Issue:** `_extract_years_from_summary()` returning "3+" when summary had "4+ years"
**Fix:** Reordered regex patterns from MOST specific to LEAST specific in `generator.py`
- Added debug logging
- Fixed pattern precedence issue
- Now correctly extracts years from complex phrases

### 13. Education Fields Not Modifiable
**Issue:** Couldn't update education details (location, GPA, degree) via chat
**Fix:** Added education field support in `modification_handler.py`
- Added safety checks for empty education list
- Improved degree detection to avoid false matches
- Enhanced GPA regex pattern

### 14. Pydantic Extra Fields Error (Backend)
**Issue:** Pydantic Settings rejecting extra environment variables from .env file
**Error:** `pydantic_core._pydantic_core.ValidationError: Extra inputs are not permitted`
**Fix:** Added `extra = "allow"` to Config class in `backend/config.py`
- Allows .env file to have additional variables without errors
- Maintains validation for required fields

### 15. Python 3.8 Type Hint Incompatibility (Backend)
**Issue:** `tuple[...]` syntax not supported in Python 3.8, causing TypeError
**Error:** `TypeError: 'type' object is not subscriptable`
**Fix:** Changed all `tuple[...]` to `Tuple[...]` from typing module in `backend/utils/security.py`
- Updated return type hints for Python 3.8 compatibility

### 16. Email Validator Missing (Backend)
**Issue:** Pydantic's `EmailStr` type requires email-validator package
**Error:** `ImportError: email-validator is not installed`
**Fix:** Added `email-validator>=2.1.0` to `requirements_backend.txt`

### 17. Bcrypt Compatibility Issue (Backend)
**Issue:** Passlib 1.7.4 incompatible with bcrypt 5.0
**Error:** `error reading bcrypt version`, `ValueError: password cannot be longer than 72 bytes`
**Fix:** Downgraded bcrypt to 4.1.3 (fully compatible with passlib)
- Updated `requirements_backend.txt` to pin bcrypt==4.1.3
- Prevents future compatibility issues

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

### Phase 9: Usage Tracking & Resume API ⭐ RECOMMENDED NEXT
Complete the backend integration:
- **Usage Tracking Service**: Check monthly limits (3 free, unlimited pro)
- **Resume Generation API**: Integrate existing src/ modules with FastAPI
- **Resume Storage**: Save generated resumes to database
- **Usage Increment**: Track resume generations per user

**Tasks:**
- Create `backend/services/usage_service.py`
- Create `backend/routers/resume.py` with generation endpoints
- Integrate `src/generation/generator.py` with backend
- Add usage limit checks before generation
- Store resume JSON and DOCX in database + filesystem

### Phase 10: PayPal Subscription Integration
Add payment processing:
- **PayPal SDK Integration**: Create/cancel subscriptions
- **Webhook Handler**: Process payment events (activated, cancelled, failed)
- **Subscription Management**: Upgrade/downgrade plans
- **Billing Cycle**: Track next billing dates

**Tasks:**
- Create `backend/utils/paypal.py`
- Create `backend/services/subscription_service.py`
- Create `backend/routers/subscription.py`
- Create `backend/routers/webhook.py` for PayPal webhooks
- Set up PayPal sandbox testing

### Phase 11: Streamlit Frontend Integration
Connect Streamlit app to backend:
- **Login/Register Pages**: Add authentication UI
- **API Call Wrapper**: Token management and refresh
- **Protected Routes**: Require authentication for resume generation
- **Usage Display**: Show remaining resumes in sidebar
- **Subscription UI**: Upgrade to Pro flow

**Tasks:**
- Modify `app.py` with authentication pages
- Create API call wrapper with automatic token refresh
- Update resume generation to use FastAPI backend
- Add usage stats display in sidebar
- Add subscription upgrade UI

### Phase 12: Cover Letter Generation
Generate tailored cover letters based on:
- Resume content
- Job description
- Semantic matching results
- Personalized to company and role

**Suggested Features:**
- Company research integration
- Role-specific customization
- Professional tone matching
- Export to DOCX format

### Phase 13: Multi-Resume Management
Manage multiple resume versions for different job types:
- Software Engineer version
- Data Engineer version
- ML Engineer version
- Store templates and apply different JDs

### Phase 10: Web UI with Streamlit
Build interactive web interface:
- Upload resume and JD
- Real-time matching scores
- Side-by-side comparison
- One-click optimization
- Download DOCX directly

### Phase 11: Resume Templates
Multiple resume layout options:
- Modern template
- Traditional template
- ATS-optimized template
- Creative template

---

## Known Issues & Limitations

### Minor Issues
1. **Projects Section Parsing:** Projects section gets fragmented during PDF parsing
   - **Impact:** Medium - projects not structured properly
   - **Status:** Can be improved in future enhancement
   - **Workaround:** Use chat modifications or manually edit parsed JSON

### Fixed Issues (Previously Known)
1. ✅ **Skills Section Formatting** - FIXED
   - LLM was outputting skills with category labels mixed in
   - **Solution:** Created `_parse_skills_categories()` and table rendering

2. ✅ **Skills in Paragraph Format** - FIXED
   - Skills were showing as comma-separated text
   - **Solution:** Built 2-column table renderer with category structure

3. ✅ **Missing Skills (70% Lost)** - FIXED
   - Only 10-20 skills showing from original resume
   - **Solution:** Updated prompts to preserve all original skills

4. ✅ **Years of Experience Bug** - FIXED
   - Extracting wrong years from summary
   - **Solution:** Reordered regex patterns by specificity

### Working As Expected
- ✅ Keyword matching with abbreviations
- ✅ Semantic similarity with RAG
- ✅ LLM optimization with gpt-3.5-turbo
- ✅ Experience bullet optimization (20-25 bullets per section, WHR format)
- ✅ Project optimization (5-8 bullets per project, WHR format)
- ✅ Summary optimization
- ✅ Skills preservation and categorization (all skills kept, organized in tables)
- ✅ JSON export
- ✅ DOCX export with ATS-friendly formatting
- ✅ Clickable hyperlinks in contact info
- ✅ Bold keyword formatting
- ✅ Text justification throughout
- ✅ Chat-based resume modifications
- ✅ Education field updates via chat
- ✅ Years of experience extraction

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
- `get_multi_bullet_optimization_prompt()`: Full experience section (20-25 bullets)
- `get_summary_optimization_prompt()`: Professional summary
- `get_skills_optimization_prompt()`: Skills section (preserves all skills)
- `get_project_optimization_prompt()`: Project section optimization (5-8 bullets)

All prompts now use WHR (What-How-Result) format and output 20-25 bullets for ATS compatibility.

### To Modify DOCX Export
Edit `src/export/docx_formatter.py`:
- `_add_hyperlink()`: Clickable link creation (lines 94-130)
- `_add_text_with_markdown_bold()`: Parse **bold** syntax (lines 219-239)
- `_parse_skills_categories()`: Skills table parsing (lines 241-265)
- Lines 368, 207, 414, 480: Text justification settings
- Lines 387-444: Technical skills table rendering
- Lines 446-508: GenAI skills table rendering

### To Add Chat Modifications
Edit `src/chat/modification_handler.py`:
- `detect_modification_intent()`: Detect modification keywords (lines 12-42)
- `extract_field_and_value()`: Extract field and new value with regex (lines 44-177)
- `apply_modification()`: Apply changes to resume object (lines 180-261)
- Line 35: Add new fields to `implicit_set_fields` list

### To Fix Years Extraction
Edit `src/generation/generator.py`:
- `_extract_years_from_summary()`: Regex patterns ordered by specificity (lines 86-114)

### To Change Embedding Model
Edit `src/vectorstore/embeddings.py`:
- Line 13: `model_name` parameter
- Alternative models:
  - `all-MiniLM-L6-v2` (384 dim) - Current, fast
  - `all-mpnet-base-v2` (768 dim) - More accurate, slower

---

## Important Commands

### Frontend (Resume Generation)
```bash
# Run Phase 3 (full pipeline)
python main.py --rag --generate

# Interactive chat interface
python main.py --chat
# OR
python chat.py

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

### Backend (Authentication & API)
```bash
# Install backend dependencies
pip install -r requirements_backend.txt

# Start FastAPI backend server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Start backend with auto-reload (development)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Test authentication endpoints
python test_auth_endpoints.py

# Check backend API status
curl http://localhost:8000/
curl http://localhost:8000/health

# Check database tables
sqlite3 resume_builder.db ".tables"

# Query users
sqlite3 resume_builder.db "SELECT id, email, full_name FROM users;"

# Query subscriptions
sqlite3 resume_builder.db "SELECT user_id, plan_type, status FROM subscriptions;"

# View API documentation (when backend is running)
open http://localhost:8000/docs
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

**Repository:** ✅ Initialized and pushed to GitHub
**Remote:** https://github.com/Hasraj3344/Resume_Builder.git
**Branch:** main

**Recent Commits:**
- "Initial commit: AI-Powered Resume Builder" (67b92d9)

**To Push New Changes:**
```bash
git add .
git commit -m "Phase 7 complete - Project optimization and DOCX enhancements"
git push origin main
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

**Last Updated:** Phase 8 completion (User Authentication & Subscription Backend)
**Next Recommended Phase:** Phase 9 (Usage Tracking & Resume API)
**Status:** All systems operational ✅
**Backend Status:** FastAPI server operational on port 8000, SQLite database with 5 tables

---

## Comprehensive Testing Results

### Phase 1-3: Core Pipeline ✅
```bash
python main.py --rag --generate
```
- ✅ Keyword matching: 60.9%
- ✅ Semantic matching: 66.8%
- ✅ Resume optimization with gpt-3.5-turbo
- ✅ JSON export
- ✅ DOCX export

### Phase 4: Chat Interface ✅
```bash
python main.py --chat
# OR
python chat.py
```
All question types tested successfully:
- ✅ Skill questions: Correctly identifies related skills and experience
- ✅ Experience questions: Retrieves relevant projects and achievements
- ✅ Match questions: Analyzes resume vs JD with specific recommendations
- ✅ Suggestion questions: Provides actionable skill improvement advice
- ✅ General questions: Summarizes strengths with conversation context

### Phase 5-7: DOCX Export & Enhancements ✅
Generated DOCX verified to have:
- ✅ Clickable hyperlinks for GitHub/LinkedIn
- ✅ Bold keywords (not ** symbols)
- ✅ Two separate skills tables (Technical + GenAI)
- ✅ Justified text throughout
- ✅ 20-25 bullets per experience section
- ✅ No bullet symbols (ATS-friendly)
- ✅ All original skills preserved
- ✅ Chat modifications applied to generation
- ✅ Project optimization working

**Test Commands:**
```bash
python test_api_key.py      # Verify API setup
python test_chat.py          # Test chat functionality
python main.py --chat        # Test modifications + generation
```

### Phase 8: Backend Authentication ✅
```bash
# Start backend server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Test authentication endpoints
python test_auth_endpoints.py
```

All authentication tests passed:
- ✅ User Registration (201 Created): User + free subscription created
- ✅ User Login (200 OK): JWT token generated, user info returned
- ✅ Get Current User (200 OK): Token validation working
- ✅ Logout (200 OK): All sessions revoked successfully
- ✅ Access After Logout (401 Unauthorized): Token correctly rejected

**Database Verification:**
```bash
sqlite3 resume_builder.db "SELECT email, full_name FROM users;"
# Result: test@example.com|Test User

sqlite3 resume_builder.db "SELECT plan_type, status FROM subscriptions;"
# Result: free|active

sqlite3 resume_builder.db "SELECT revoked FROM sessions;"
# Result: 1 (correctly revoked after logout)
```

**API Endpoints Available:**
- `GET /` - API status check
- `GET /health` - Health check
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - Logout all sessions
- `POST /api/auth/logout-session` - Logout specific session
- `GET /api/auth/me` - Get current user (protected)
- `GET /docs` - Interactive API documentation (Swagger UI)

---

## Quick Reference

### Essential Commands
```bash
# Full pipeline (generates JSON + DOCX)
python main.py --rag --generate

# Interactive chat with modifications
python main.py --chat

# Test API configuration
python test_api_key.py
```

### Key Features
| Feature | Status | Location |
|---------|--------|----------|
| Keyword Matching | ✅ 60.9% | `skill_matcher.py` |
| Semantic Matching | ✅ 66.8% | `retriever.py` |
| LLM Optimization | ✅ gpt-3.5-turbo | `generator.py` |
| DOCX Export | ✅ ATS-friendly | `docx_formatter.py` |
| Chat Modifications | ✅ 11+ fields | `modification_handler.py` |
| Project Optimization | ✅ WHR format | `generator.py:optimize_project()` |

### File Outputs
- `output/resume.json` - Parsed resume data
- `output/job_description.json` - Parsed JD data
- `output/optimized_resume.json` - LLM-optimized resume
- `output/optimized_resume.docx` - **ATS-friendly Word document** ⭐

### Chat Modification Examples
```
"Change my email to john@example.com"
"My GitHub link is username"              → https://github.com/username
"Update years of experience to 5"
"Add skill: Docker"
"My education GPA is 3.85"
"Set my location to New York, NY"
```

### Important Notes
- ✅ All prompts use WHR (What-How-Result) format
- ✅ 20-25 bullets per experience section for ATS
- ✅ All original skills preserved in output
- ✅ Chat modifications automatically applied to generation
- ✅ DOCX has clickable hyperlinks and proper bold formatting
