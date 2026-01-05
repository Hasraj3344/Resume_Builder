# Adzuna Job Search Workflow - Implementation Guide

## Overview

The Adzuna workflow allows users to:
1. **Search for jobs** using the Adzuna API based on keywords and location
2. **Match resume** to jobs using semantic similarity (vector embeddings)
3. **Select a job** from the ranked list
4. **Optimize resume** specifically for that job
5. **Download** the tailored resume as DOCX

---

## Step 1: Get Adzuna API Credentials (FREE)

### Sign Up for Adzuna API

1. Go to https://developer.adzuna.com/
2. Click "Get Your API Key"
3. Fill out the registration form
4. You'll receive:
   - **App ID**: A numeric ID (e.g., `12345678`)
   - **API Key**: A long alphanumeric key (e.g., `abcd1234efgh5678...`)

### Add to .env File

```bash
# Adzuna Job Search API
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_api_key_here
```

### Test API Credentials

```bash
curl "https://api.adzuna.com/v1/api/jobs/us/search/1?app_id=YOUR_APP_ID&app_key=YOUR_API_KEY&what=data+engineer&where=remote"
```

---

## Current Implementation Status

### ✅ Completed (2025-12-22)

1. **Backend Services**
   - `backend/services/adzuna_service.py` - Adzuna API integration ✓
   - `backend/services/matching_service.py` - Resume-to-job matching with embeddings ✓
   - `backend/services/generation_service.py` - Custom filename support for DOCX export ✓

2. **Backend Endpoints**
   - `GET /api/jobs/search` - Search Adzuna jobs with automatic resume matching ✓
   - `POST /api/jobs/match` - Match resume to jobs using vector similarity ✓
   - `POST /api/generation/adzuna` - **FULLY IMPLEMENTED** - Optimize resume for selected job ✓
     * Accepts full job_data in request body
     * Parses job description from Adzuna job
     * Calculates match score (keyword + semantic)
     * Optimizes resume using LLM
     * Exports to DOCX with custom filename (company_jobtitle.docx)
     * Saves to database
     * Increments usage counter
     * Returns optimized resume + match analysis + download link

3. **Frontend Page** - `frontend/src/components/Workflow/AdzunaWorkflowPage.jsx`
   - **Step 1**: Search form with filters (query, location, salary min/max) ✓
   - **Step 2**: Job results with similarity scores, sorting (by match/salary) ✓
   - **Step 3**: Optimized resume with match analysis, job details, download ✓

4. **Job Matching Integration**
   - `/api/jobs/search` automatically scores jobs against user's resume ✓
   - Match percentage displayed for each job (color-coded: green/yellow/red) ✓
   - Jobs sorted by relevance (highest match first) ✓
   - User can toggle sort between "Best Match" and "Highest Salary" ✓

### ✅ Features Implemented

- **Automatic Resume Matching**: Jobs are scored against user's resume using FAISS vector similarity
- **Smart Filename Generation**: DOCX files named as `resume_company_jobtitle.docx`
- **Match Analysis Display**: Shows matched skills, missing skills, and overall score
- **Usage Tracking**: Displays remaining resumes for free tier users
- **Job Details**: Shows position, company, location, salary, and link to original posting
- **Responsive UI**: 3-step wizard with progress indicator
- **Error Handling**: Comprehensive error messages and loading states

### ⏳ Optional Enhancements (Future Work)

1. **Job Bookmarking** - Save interesting jobs to database
2. **Application Tracking** - Mark jobs as "Applied" and track status
3. **Smart Recommendations** - ML model for personalized job suggestions
4. **Batch Optimization** - Generate resumes for multiple jobs at once
5. **Job Alerts** - Email notifications for new matching jobs

---

## Implementation Plan

### Task 1: Complete Backend Adzuna Endpoint

**File:** `backend/routers/generation.py`

**Endpoint:** `POST /api/generation/adzuna`

**Request:**
```json
{
  "job_data": {
    "id": "1234567",
    "title": "Senior Data Engineer",
    "company": "Acme Corp",
    "location": "Remote",
    "description": "Full job description text...",
    "url": "https://www.adzuna.com/...",
    "salary_min": 120000,
    "salary_max": 180000
  }
}
```

**Logic:**
1. Check usage limits (UsageService)
2. Get user's resume from database
3. Parse job description text (jd_service.parse_job_description)
4. Calculate match score (matching_service.calculate_match_score)
5. Optimize resume (generation_service.optimize_resume)
6. Export to DOCX (generation_service.export_to_docx)
7. Save to database (Resume model)
8. Increment usage (UsageService.increment_usage)
9. Return optimized resume + download link

**Response:**
```json
{
  "id": "resume_123_adzuna_job_1234567",
  "optimized_resume": { ... },
  "match_analysis": {
    "keyword_match": { ... },
    "semantic_match": { ... },
    "overall_score": 75.5
  },
  "docx_filename": "optimized_resume_acme_corp.docx",
  "download_url": "/api/generation/download/optimized_resume_acme_corp.docx",
  "usage_info": {
    "resumes_generated": 2,
    "limit": 3,
    "remaining": 1
  }
}
```

### Task 2: Integrate Resume Matching with Job Search

**File:** `backend/routers/jobs.py`

**Update:** `GET /api/jobs/search`

**New Logic:**
```python
@router.get("/search")
async def search_jobs(
    query: Optional[str] = None,
    location: str = "United States",
    current_user: User = Depends(get_current_user),
):
    # 1. Search Adzuna
    jobs = await adzuna_service.search_jobs(query=query, location=location)

    # 2. Get user's resume
    if current_user.resume_parsed_data:
        resume_text = _extract_resume_text(current_user.resume_parsed_data)

        # 3. Match resume to jobs
        matched_jobs = matching_service.match_resume_to_jobs(
            resume_text=resume_text,
            job_descriptions=jobs
        )

        # matched_jobs now includes similarity_score for each job
        return {"jobs": matched_jobs, "total": len(matched_jobs)}

    return {"jobs": jobs, "total": len(jobs)}
```

### Task 3: Complete Frontend UI

**File:** `frontend/src/components/Workflow/AdzunaWorkflowPage.jsx`

**Step 1: Search Form**
```jsx
<Card>
  <h2>Search for Jobs</h2>
  <input
    placeholder="Job title or keywords (e.g., 'data engineer')"
    value={filters.query}
    onChange={...}
  />
  <input
    placeholder="Location (e.g., 'Atlanta, GA' or 'Remote')"
    value={filters.location}
    onChange={...}
  />
  <Button onClick={handleSearch}>Search Jobs</Button>
</Card>
```

**Step 2: Job Results with Match Scores**
```jsx
{jobResults.map(job => (
  <Card key={job.id} onClick={() => handleSelectJob(job)}>
    <div className="flex justify-between">
      <div>
        <h3>{job.title}</h3>
        <p>{job.company} - {job.location}</p>
      </div>
      <div className="text-right">
        {job.similarity_score && (
          <div className="text-lg font-bold text-primary">
            {Math.round(job.similarity_score)}% Match
          </div>
        )}
        {job.salary_min && job.salary_max && (
          <p className="text-sm text-neutral-600">
            ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}
          </p>
        )}
      </div>
    </div>
    <p className="text-sm text-neutral-700 mt-2">
      {job.description.substring(0, 200)}...
    </p>
  </Card>
))}
```

**Step 3: Optimized Resume**
```jsx
{optimizedResume && (
  <Card>
    <h2>Your Optimized Resume for {selectedJob.title}</h2>
    <div className="bg-success-50 border border-success-200 rounded p-4 mb-4">
      <div className="flex items-center gap-2">
        <svg className="w-6 h-6 text-success">...</svg>
        <div>
          <p className="font-semibold text-success-900">
            {Math.round(optimizedResume.match_analysis.overall_score)}% Match!
          </p>
          <p className="text-sm text-success-700">
            Matched {optimizedResume.match_analysis.keyword_match.matched_count} of {optimizedResume.match_analysis.keyword_match.total_required} required skills
          </p>
        </div>
      </div>
    </div>

    <Button onClick={handleDownload} className="w-full">
      Download Optimized Resume (DOCX)
    </Button>
  </Card>
)}
```

---

## Testing Checklist

### 1. API Credentials Test
- [ ] Adzuna API credentials configured in .env
- [ ] Test API with curl command
- [ ] Backend server can connect to Adzuna API

### 2. Job Search Test
- [ ] Navigate to Adzuna Workflow page
- [ ] Enter search query (e.g., "data engineer")
- [ ] Enter location (e.g., "Remote")
- [ ] Click "Search Jobs"
- [ ] Verify jobs are displayed with match scores

### 3. Job Matching Test
- [ ] Upload resume with known skills (e.g., Python, SQL, AWS)
- [ ] Search for matching jobs
- [ ] Verify match scores are calculated
- [ ] Jobs should be sorted by match score (highest first)

### 4. Resume Optimization Test
- [ ] Select a job from results
- [ ] Click "Optimize Resume"
- [ ] Verify optimized resume is generated
- [ ] Check match analysis shows improvement
- [ ] Download DOCX file
- [ ] Open DOCX to verify formatting

### 5. Usage Limits Test
- [ ] Free tier user generates 3 resumes
- [ ] 4th attempt should be blocked with 403 error
- [ ] Error message should show usage limit info

---

## API Endpoints Reference

### Job Search
```http
GET /api/jobs/search?query=data+engineer&location=remote
Authorization: Bearer {token}
```

### Job Matching
```http
POST /api/jobs/match
Authorization: Bearer {token}
Content-Type: application/json

{
  "resume_text": "...",
  "jobs": [...]
}
```

### Resume Optimization (Adzuna)
```http
POST /api/generation/adzuna
Authorization: Bearer {token}
Content-Type: application/json

{
  "job_data": {
    "id": "1234567",
    "title": "Senior Data Engineer",
    "description": "...",
    ...
  }
}
```

---

## Future Enhancements

1. **Job Bookmarking**
   - Save interesting jobs to database
   - View saved jobs later
   - Get notifications when similar jobs posted

2. **Application Tracking**
   - Mark jobs as "Applied"
   - Track application status
   - Set reminders for follow-ups

3. **Smart Recommendations**
   - ML model trained on user's job selections
   - Recommend jobs based on past preferences
   - Suggest skill improvements for better matches

4. **Batch Optimization**
   - Select multiple jobs
   - Generate optimized resume for each
   - Download as ZIP file

5. **Job Alerts**
   - Set up search alerts
   - Email notifications for new matching jobs
   - Weekly digest of top matches

---

## Testing the Adzuna Workflow

### Prerequisites

1. **Get Adzuna API Credentials** (FREE):
   - Go to https://developer.adzuna.com/
   - Click "Get Your API Key"
   - Fill out registration form
   - Copy App ID and API Key

2. **Add Credentials to .env**:
   ```bash
   ADZUNA_APP_ID=your_app_id_here
   ADZUNA_APP_KEY=your_api_key_here
   ```

3. **Restart Backend Server**:
   ```bash
   cd /Users/hasraj/Resume_Builder
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start Frontend** (if not running):
   ```bash
   cd frontend
   npm start
   ```

### Test Steps

1. **Login to Application**:
   - Navigate to http://localhost:3000
   - Login with your test account
   - Ensure you have a resume uploaded and parsed

2. **Navigate to Adzuna Workflow**:
   - From dashboard, click "Adzuna Job Search"
   - OR navigate directly to `/adzuna-workflow`

3. **Step 1: Search for Jobs**:
   - Enter job query: "data engineer" or "software engineer"
   - Enter location: "Remote" or "San Francisco"
   - (Optional) Set salary filters
   - Click "Search Jobs →"
   - **Expected**: List of jobs with match scores (if resume is uploaded)

4. **Step 2: Select a Job**:
   - Browse job cards sorted by match score
   - Click on a job card to select it
   - Try changing sort order (Best Match ↔ Highest Salary)
   - Click "Optimize Resume for Selected Job →"
   - **Expected**: Progress to Step 3 with optimized resume

5. **Step 3: Download Resume**:
   - Review match analysis (matched/missing skills)
   - Check usage stats (X/3 for free tier)
   - View job details
   - Click "Download Resume (DOCX) →"
   - **Expected**: DOCX file downloads as `resume_company_jobtitle.docx`

6. **Verify DOCX**:
   - Open downloaded file in Microsoft Word
   - Check formatting, hyperlinks, and content
   - Verify skills, experience bullets are optimized for job

### Common Issues & Solutions

**Issue**: "Adzuna API credentials not configured"
- **Solution**: Add ADZUNA_APP_ID and ADZUNA_APP_KEY to .env file and restart backend

**Issue**: No match scores showing on jobs
- **Solution**: Ensure you have uploaded and parsed a resume first

**Issue**: "Usage limit exceeded"
- **Solution**: Free tier allows 3 resumes/month. Wait for monthly reset or upgrade to Pro

**Issue**: Job descriptions are empty
- **Solution**: Adzuna sometimes returns jobs with minimal descriptions. Try different search terms.

**Issue**: Download fails with 404
- **Solution**: Check that `output/resumes/` directory exists and backend has write permissions

### Verification Checklist

- [ ] Adzuna API credentials configured
- [ ] Backend server running on port 8000
- [ ] Frontend running on port 3000
- [ ] User logged in with resume uploaded
- [ ] Job search returns results with match scores
- [ ] Job selection works (green border on selected card)
- [ ] Resume optimization completes successfully
- [ ] Match analysis displays correctly
- [ ] DOCX download works
- [ ] Filename format is `resume_company_jobtitle.docx`
- [ ] Usage counter increments after generation

---

## Implementation Complete! 🎉

**Date**: December 22, 2025
**Status**: Fully Functional

All core features of the Adzuna Job Search workflow are now implemented and ready for testing. The workflow provides:

✅ Real-time job search via Adzuna API
✅ Automatic resume-to-job matching with vector similarity
✅ LLM-powered resume optimization
✅ Professional DOCX export with smart naming
✅ Usage tracking and limits enforcement
✅ Beautiful 3-step UI with progress tracking

Ready to help users find jobs and optimize their resumes!
