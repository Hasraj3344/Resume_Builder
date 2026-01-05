# Job Portal Application

## Project Overview

A full-stack AI-powered job portal application that helps users search for jobs, match their resumes against job descriptions using machine learning, and optimize their resumes for specific positions using AI.

## Tech Stack

### Frontend
- **Framework**: React 19.1.0
- **Build Tool**: Create React App with React Scripts 5.0.1
- **Routing**: React Router DOM 7.5.0
- **UI Framework**: Material-UI (@mui/icons-material, @emotion/react, @emotion/styled)
- **Styling**: Tailwind CSS 4.1.4, Styled Components 6.1.17
- **Authentication**: Supabase (@supabase/supabase-js 2.49.4)
- **HTTP Client**: Axios 1.8.4
- **PDF Handling**: jsPDF 3.0.1, pdfjs-dist 5.2.133

### Backend

#### Node.js CORS Proxy Server (Port 5050)
- **Framework**: Express.js
- **Purpose**: Acts as a proxy server to handle CORS issues and coordinate API calls
- **Location**: `/cors-proxy/server.js`
- **Key Dependencies**:
  - cors
  - axios
  - openai

#### Python AI/ML Service
- **Purpose**: Resume matching using vector similarity search
- **Location**: `/cors-proxy/match_resume.py` and `/backend/`
- **Key Dependencies**:
  - fastapi 0.115.12
  - sentence-transformers 3.2.1
  - faiss-cpu 1.8.0.post1
  - transformers 4.46.3
  - torch 2.2.2
  - scikit-learn 1.3.2
  - numpy 1.24.4

### External APIs
- **Adzuna Jobs API**: For fetching job listings
- **OpenAI API**: For AI-powered resume rewriting (GPT-3.5-turbo)

## Project Structure

```
job-portal/
├── src/
│   ├── Components/
│   │   ├── Home/              # Landing page
│   │   ├── Navbar/            # Navigation component
│   │   ├── Registration/      # Login & Register components
│   │   ├── jobs/              # Job search functionality
│   │   ├── processing/        # Job application processing
│   │   ├── rewrittenresume/   # Resume rewriting feature
│   │   ├── Profile/           # User profile
│   │   └── Database/          # Supabase client configuration
│   ├── App.js                 # Main app component with routing
│   └── index.js               # Entry point
├── backend/
│   ├── main.py                # FAISS vector search example
│   ├── vector_utils.py        # Utility functions for embeddings
│   └── requirements.txt       # Python dependencies
├── cors-proxy/
│   ├── server.js              # Express proxy server
│   ├── match_resume.py        # ML-based resume matching script
│   └── requirements.txt       # Python dependencies for proxy
├── public/                    # Static assets
├── package.json               # Node.js dependencies
└── .env                       # Environment variables
```

## Key Features

### 1. User Authentication
- User registration and login powered by Supabase
- Session management
- Components: `src/Components/Registration/`

### 2. Job Search
- Search jobs by keyword and location
- Fetches job listings from Adzuna API
- Displays job details (title, company, location, description)
- Components: `src/Components/jobs/jobsearch.js`

### 3. AI-Powered Resume Matching
- Uses sentence transformers (all-MiniLM-L6-v2) to create embeddings
- Implements FAISS vector similarity search
- Matches user resumes against job descriptions
- Returns similarity scores (%)
- Filters results with >10% similarity
- Script: `cors-proxy/match_resume.py`

**Workflow**:
1. User uploads resume text
2. System fetches jobs from Adzuna based on search criteria
3. Resume and job descriptions are converted to embeddings
4. FAISS performs similarity search
5. Returns top 100 matches with similarity percentages

### 4. Resume Rewriting
- AI-powered resume optimization using OpenAI GPT-3.5-turbo
- Tailors resume content to match specific job descriptions
- Endpoint: `POST /api/rewrite-resume`

### 5. Job Application Processing
- Apply to jobs directly through the platform
- Components: `src/Components/processing/`

## API Endpoints

### CORS Proxy Server (http://localhost:5050)

#### GET /api/jobs
Fetches job listings from Adzuna API.

**Query Parameters**:
- `what`: Job title or keyword (optional)
- `where`: Location (required)

**Response**: Array of job objects with details

#### POST /api/match-resume
Matches resume against job listings using ML.

**Request Body**:
```json
{
  "resumeText": "string",
  "query": "string",
  "location": "string"
}
```

**Response**: Array of matched jobs with similarity scores
```json
[
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "company": "string",
    "location": "string",
    "url": "string",
    "similarity": 85.5
  }
]
```

#### POST /api/rewrite-resume
Rewrites resume to match job description using AI.

**Request Body**:
```json
{
  "jobDescription": "string",
  "resume": "string"
}
```

**Response**:
```json
{
  "rewrittenResume": "string"
}
```

## Environment Variables

Create a `.env` file in the root directory:

```env
# Adzuna API Credentials
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key

# OpenAI API Key
REACT_APP_OPENAI_API_KEY=your_openai_api_key

# Supabase Configuration
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Also create a `.env` file in the `cors-proxy/` directory with the same variables.

## Installation & Setup

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8+
- npm or yarn

### Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm start
# Runs on http://localhost:3000
```

### CORS Proxy Server Setup
```bash
# Navigate to cors-proxy directory
cd cors-proxy

# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Start the proxy server
node server.js
# Runs on http://localhost:5050
```

### Backend Python Service Setup
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Test the FAISS implementation
python main.py
```

## Machine Learning Implementation

### Embedding Model
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Purpose**: Converts text into 384-dimensional dense vectors
- **Advantages**: Lightweight, fast, good semantic understanding

### Vector Search
- **Library**: FAISS (Facebook AI Similarity Search)
- **Index Type**: IndexFlatIP (Inner Product for normalized vectors)
- **Normalization**: L2 normalization for cosine similarity
- **Search Depth**: Top 100 matches

### Process Flow
```
Resume Text → Sentence Transformer → Embedding Vector (384d)
                                           ↓
Job Descriptions → Sentence Transformer → Embedding Vectors (384d)
                                           ↓
                                    FAISS Index
                                           ↓
                                   Similarity Search
                                           ↓
                              Top Matches with Scores
```

## Deployment Considerations

### Frontend
- Build command: `npm run build`
- Output directory: `build/`
- Current deployment: Vercel (https://job-app-portal.vercel.app)

### Backend Services
- CORS proxy server needs to be deployed separately
- Python ML service can run as a subprocess (current setup) or as a separate microservice
- Ensure Python dependencies are available in production environment
- Consider using containerization (Docker) for easier deployment

### Performance Optimizations
- Job descriptions truncated to 2048 characters
- Batch processing for embeddings (batch_size=8)
- Embedding normalization for faster similarity computation
- FAISS uses efficient indexing for fast searches

## Development Notes

### Known Issues
- README.md has merge conflict markers (lines 1-75)
- OpenAI client initialization appears incomplete in server.js:142

### Security Considerations
- API keys must be stored securely in environment variables
- Never commit `.env` files to version control
- Implement rate limiting on API endpoints
- Validate and sanitize user inputs
- Use HTTPS in production

### Future Enhancements
- Add user profile management
- Implement resume storage and history
- Add job bookmarking/favoriting
- Enhance matching algorithm with more features
- Add email notifications for job matches
- Implement pagination for large result sets
- Add unit and integration tests

## Routes

- `/` - Home page
- `/register` - User registration
- `/login` - User login
- `/jobsearch` - Job search interface
- `/processing` - Job processing dashboard
- `/apply/:jobId` - Job application page

## Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm test -- --watch
```

## Build

```bash
# Create production build
npm run build
```

## License

Private project

## Contact

For questions or issues, refer to the project documentation or contact the development team.
