import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { Button, Card, LoadingSpinner, SubscriptionModal } from '../Shared';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import ResumeEditor from './ResumeEditor';

const AdzunaWorkflowPage = () => {
  const navigate = useNavigate();
  const { user, setUser } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Resume editor state
  const [showParsedEditor, setShowParsedEditor] = useState(false);
  const [parsedResumeData, setParsedResumeData] = useState(null);

  // Subscription modal state
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [subscriptionUsageInfo, setSubscriptionUsageInfo] = useState(null);

  // Step 1: Search Filters
  const [filters, setFilters] = useState({
    query: '',
    location: '',
    experience_level: '', // entry, mid, senior
    work_mode: '', // remote, onsite, hybrid
  });

  // Step 2: Job Results with Pagination
  const [jobResults, setJobResults] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const resultsPerPage = 20;

  // Step 2.5: Resume Selection
  const [currentResume, setCurrentResume] = useState(null);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [showResumeSelection, setShowResumeSelection] = useState(false);

  // Step 3: Optimized Resume
  const [optimizedResume, setOptimizedResume] = useState(null);

  // Sorting
  const [sortBy, setSortBy] = useState('match'); // 'match', 'date'

  // Load current resume on mount
  useEffect(() => {
    if (user?.resume_file_path) {
      const filename = user.resume_file_path.split(/[/\\]/).pop();
      setCurrentResume({
        filename: filename,
        path: user.resume_file_path,
      });
    }
  }, [user]);

  // Debug: Monitor optimizedResume state changes
  useEffect(() => {
    if (optimizedResume) {
      console.log('[DEBUG] optimizedResume state updated:', optimizedResume);
      console.log('[DEBUG] Has match_analysis?', !!optimizedResume.match_analysis);
      if (optimizedResume.match_analysis) {
        console.log('[DEBUG] Match analysis structure:', {
          overall_score: optimizedResume.match_analysis.overall_score,
          keyword_match: optimizedResume.match_analysis.keyword_match,
          semantic_match: optimizedResume.match_analysis.semantic_match,
        });
      } else {
        console.log('[DEBUG] match_analysis is missing or undefined');
      }
    }
  }, [optimizedResume]);

  // Resume upload dropzone
  const resumeDropzone = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 5242880, // 5MB
    multiple: false,
    onDrop: async (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        await handleUploadResume(acceptedFiles[0]);
      }
    },
  });

  const handleUploadResume = async (file) => {
    setUploadingResume(true);
    try {
      const formData = new FormData();
      formData.append('resume', file);

      const response = await api.post('/api/resume/upload', formData);

      setCurrentResume({
        filename: file.name,
        path: response.data.user.resume_file_path,
      });

      setUser(response.data.user);
      toast.success('Resume uploaded successfully!');
    } catch (error) {
      console.error('[UPLOAD] Error:', error);
      toast.error(error.response?.data?.detail || 'Failed to upload resume');
    } finally {
      setUploadingResume(false);
    }
  };

  const handleSaveParsedResumeEdits = async (editedResume) => {
    setLoading(true);
    try {
      const response = await api.put('/api/resume/edit', editedResume);

      setUser({
        ...user,
        resume_parsed_data: response.data.updated_data
      });

      setParsedResumeData(response.data.updated_data);
      setShowParsedEditor(false);
      toast.success('Resume updated successfully!');
    } catch (error) {
      console.error('[EDIT] Error:', error);
      toast.error(error.response?.data?.detail || 'Failed to save changes');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (pageOrEvent = 1) => {
    // Handle case where onClick passes event object
    const page = typeof pageOrEvent === 'number' ? pageOrEvent : 1;

    if (!filters.query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setLoading(true);
    try {
      // Build query params, filtering out empty values
      const params = { page };
      if (filters.query) params.query = filters.query;
      if (filters.location) params.location = filters.location;
      if (filters.experience_level) params.experience_level = filters.experience_level;
      if (filters.work_mode) params.work_mode = filters.work_mode;

      const response = await api.get('/api/jobs/search', { params });

      const jobs = response.data.jobs || [];
      setJobResults(jobs);
      setCurrentPage(page);
      setTotalResults(response.data.total || 0);
      setCurrentStep(2);

      const matchedText = response.data.matched ? ' with match scores' : '';
      toast.success(`Found ${response.data.total || 0} jobs${matchedText}!`);
    } catch (error) {
      console.error('[SEARCH] Error:', error);
      const errorDetail = error.response?.data?.detail;
      let errorMsg = 'Failed to search jobs';

      if (typeof errorDetail === 'string') {
        errorMsg = errorDetail;
      } else if (Array.isArray(errorDetail)) {
        // Handle Pydantic validation errors
        errorMsg = errorDetail.map(err => err.msg || JSON.stringify(err)).join(', ');
      }

      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectJob = (job) => {
    setSelectedJob(job);
  };

  const getSortedJobs = () => {
    const sorted = [...jobResults];
    if (sortBy === 'match') {
      // Sort by similarity_score (highest first)
      sorted.sort((a, b) => (b.similarity_score || 0) - (a.similarity_score || 0));
    } else if (sortBy === 'date') {
      // Sort by created date (newest first)
      sorted.sort((a, b) => {
        const dateA = a.created ? new Date(a.created).getTime() : 0;
        const dateB = b.created ? new Date(b.created).getTime() : 0;
        return dateB - dateA;
      });
    }
    return sorted;
  };

  const handleProceedToResumeSelection = () => {
    if (!selectedJob) {
      toast.error('Please select a job first');
      return;
    }
    setShowResumeSelection(true);
    setCurrentStep(2.5);
  };

  const handleUseProfileResume = async () => {
    if (!currentResume && !user?.resume_file_path) {
      toast.error('No resume found on profile');
      return;
    }
    await handleOptimize();
  };

  const handleOptimize = async () => {
    if (!selectedJob) {
      toast.error('Please select a job first');
      return;
    }

    if (!currentResume && !user?.resume_file_path) {
      toast.error('Please upload a resume first');
      return;
    }

    setLoading(true);
    try {
      console.log('[OPTIMIZE] Sending job data:', selectedJob);

      const response = await api.post('/api/generation/adzuna', {
        job_data: selectedJob,
      });

      console.log('[OPTIMIZE] Response:', response.data);
      console.log('[OPTIMIZE] Match Analysis:', response.data.match_analysis);
      console.log('[OPTIMIZE] Overall Score:', response.data.match_analysis?.overall_score);
      console.log('[OPTIMIZE] Keyword Match:', response.data.match_analysis?.keyword_match);

      setOptimizedResume(response.data);

      // Verify state was set correctly
      console.log('[OPTIMIZE] State set with optimizedResume');

      setShowResumeSelection(false);
      setCurrentStep(3);
      toast.success('Resume optimized successfully!');
    } catch (error) {
      console.error('[OPTIMIZE] Error:', error);

      // Check if it's a usage limit error (403)
      if (error.response?.status === 403 && error.response?.data?.detail?.error === 'usage_limit_exceeded') {
        const usageInfo = error.response.data.detail.usage_info || {};
        setSubscriptionUsageInfo(usageInfo);
        setShowSubscriptionModal(true);
        return;
      }

      const errorMsg = error.response?.data?.detail || 'Failed to optimize resume';
      toast.error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage < 1) return;
    handleSearch(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const totalPages = Math.ceil(totalResults / resultsPerPage);

  const handleDownload = async () => {
    if (!optimizedResume || !optimizedResume.download_url) {
      toast.error('Download URL not available');
      return;
    }

    try {
      const response = await api.get(optimizedResume.download_url, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', optimizedResume.docx_filename || 'optimized_resume.docx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('Resume downloaded successfully!');
    } catch (error) {
      console.error('[DOWNLOAD] Error:', error);
      toast.error('Failed to download resume');
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <div className="min-h-screen bg-neutral-50 py-12 px-4 sm:px-6 lg:px-8">
      {/* Resume Editor Modal */}
      {showParsedEditor && parsedResumeData && (
        <div className="fixed inset-0 bg-black/50 z-50 overflow-y-auto">
          <div className="min-h-screen px-4 py-8">
            <div className="max-w-5xl mx-auto bg-white rounded-lg shadow-xl">
              <div className="sticky top-0 bg-white border-b border-neutral-200 px-6 py-4 rounded-t-lg z-10">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-neutral-900">Edit Resume</h2>
                    <p className="text-sm text-neutral-600 mt-1">
                      Make changes to your resume data
                    </p>
                  </div>
                  <button
                    onClick={() => setShowParsedEditor(false)}
                    className="text-neutral-500 hover:text-neutral-700 transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <div className="p-6 max-h-[calc(100vh-200px)] overflow-y-auto">
                <ResumeEditor
                  resume={parsedResumeData}
                  onSave={handleSaveParsedResumeEdits}
                  onCancel={() => setShowParsedEditor(false)}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-primary hover:text-primary-dark flex items-center gap-2 mb-4"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-neutral-900 mb-2">Adzuna Job Search</h1>
          <p className="text-lg text-neutral-600">
            Search real-time job postings and optimize your resume
          </p>
        </div>

        <div className="mb-12">
          <div className="flex items-center justify-center">
            {[1, 2, 2.5, 3].map((step, idx) => (
              <React.Fragment key={step}>
                <div
                  className={`flex items-center justify-center w-12 h-12 rounded-full font-semibold ${
                    currentStep >= step ? 'bg-success text-white' : 'bg-neutral-200 text-neutral-600'
                  }`}
                >
                  {idx + 1}
                </div>
                {idx < 3 && (
                  <div className={`w-20 h-1 mx-2 ${currentStep > step ? 'bg-success' : 'bg-neutral-200'}`}></div>
                )}
              </React.Fragment>
            ))}
          </div>
          <div className="flex justify-between mt-4 text-sm text-neutral-600 max-w-2xl mx-auto px-4">
            <span className={currentStep === 1 ? 'font-semibold text-success' : ''}>Search</span>
            <span className={currentStep === 2 ? 'font-semibold text-success' : ''}>Select Job</span>
            <span className={currentStep === 2.5 ? 'font-semibold text-success' : ''}>Choose Resume</span>
            <span className={currentStep === 3 ? 'font-semibold text-success' : ''}>Download</span>
          </div>
        </div>

        {/* STEP 1: Search Filters */}
        {currentStep === 1 && (
          <Card className="animate-fadeIn max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-neutral-900 mb-4">Step 1: Search for Jobs</h2>
            <p className="text-neutral-600 mb-6">
              Enter your job preferences to find matching opportunities
            </p>

            <div className="space-y-4 mb-6">
              <div>
                <label className="label">Job Title or Keywords *</label>
                <input
                  type="text"
                  value={filters.query}
                  onChange={(e) => setFilters({ ...filters, query: e.target.value })}
                  className="input"
                  placeholder="e.g. Software Engineer, Data Scientist, Product Manager"
                />
              </div>

              <div>
                <label className="label">Location (Optional)</label>
                <input
                  type="text"
                  value={filters.location}
                  onChange={(e) => setFilters({ ...filters, location: e.target.value })}
                  className="input"
                  placeholder="e.g. New York, NY or San Francisco, CA (leave blank for all locations)"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Experience Level</label>
                  <select
                    value={filters.experience_level}
                    onChange={(e) => setFilters({ ...filters, experience_level: e.target.value })}
                    className="input"
                  >
                    <option value="">Any Experience</option>
                    <option value="entry">Entry Level (0-2 years)</option>
                    <option value="mid">Mid Level (3-5 years)</option>
                    <option value="senior">Senior Level (6+ years)</option>
                  </select>
                </div>
                <div>
                  <label className="label">Work Mode</label>
                  <select
                    value={filters.work_mode}
                    onChange={(e) => setFilters({ ...filters, work_mode: e.target.value })}
                    className="input"
                  >
                    <option value="">Any Mode</option>
                    <option value="remote">Remote</option>
                    <option value="onsite">Onsite</option>
                    <option value="hybrid">Hybrid</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <Button variant="secondary" fullWidth onClick={() => navigate('/dashboard')}>
                Cancel
              </Button>
              <Button variant="success" fullWidth onClick={handleSearch} disabled={!filters.query.trim()}>
                Search Jobs →
              </Button>
            </div>
          </Card>
        )}

        {/* STEP 2: Job Results */}
        {currentStep === 2 && (
          <div className="animate-fadeIn">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-neutral-900">
                  Found {totalResults.toLocaleString()} Jobs
                </h2>
                <p className="text-sm text-neutral-600 mt-1">
                  Showing page {currentPage} of {totalPages}
                  {jobResults.some(j => j.similarity_score !== undefined) && ' • Matched against your resume'}
                </p>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <label className="text-sm text-neutral-600">Sort by:</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="input py-2 text-sm"
                  >
                    <option value="match">Best Match</option>
                    <option value="date">Most Recent</option>
                  </select>
                </div>
                <Button variant="outline" onClick={() => setCurrentStep(1)}>
                  ← New Search
                </Button>
              </div>
            </div>

            {jobResults.length === 0 ? (
              <Card>
                <div className="text-center py-12">
                  <p className="text-neutral-600">No jobs found. Try adjusting your search criteria.</p>
                </div>
              </Card>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {getSortedJobs().map((job, idx) => (
                  <Card
                    key={idx}
                    className={`cursor-pointer transition-all hover:shadow-lg ${
                      selectedJob?.id === job.id ? 'ring-2 ring-success' : ''
                    }`}
                    onClick={() => handleSelectJob(job)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-neutral-900 mb-1">{job.title}</h3>
                        <p className="text-sm text-neutral-600">{job.company}</p>
                      </div>
                      {job.similarity_score !== undefined && (
                        <div className="text-right ml-2">
                          <div className={`text-lg font-bold ${
                            job.similarity_score >= 75 ? 'text-success' :
                            job.similarity_score >= 50 ? 'text-warning' :
                            'text-error'
                          }`}>
                            {Math.round(job.similarity_score)}% Match
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="space-y-2 text-sm text-neutral-600 mb-3">
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {job.location || 'Not specified'}
                      </div>
                      {(job.salary_min || job.salary_max) && (
                        <div className="flex items-center gap-2">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          ${job.salary_min ? job.salary_min.toLocaleString() : '?'} - ${job.salary_max ? job.salary_max.toLocaleString() : '?'}
                        </div>
                      )}
                    </div>

                    {job.description && (
                      <p className="text-sm text-neutral-700 mb-3 line-clamp-3">
                        {job.description.replace(/<[^>]*>/g, '').substring(0, 200)}...
                      </p>
                    )}

                    {selectedJob?.id === job.id && (
                      <div className="flex items-center gap-2 text-success text-sm font-medium">
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        Selected
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}

            {/* Pagination Controls */}
            {jobResults.length > 0 && totalPages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-4">
                <Button
                  variant="outline"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  ← Previous
                </Button>
                <div className="flex items-center gap-2">
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }
                    return (
                      <button
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        className={`w-10 h-10 rounded-lg font-semibold ${
                          currentPage === pageNum
                            ? 'bg-success text-white'
                            : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>
                <Button
                  variant="outline"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next →
                </Button>
              </div>
            )}

            {selectedJob && (
              <div className="mt-8 max-w-3xl mx-auto">
                <Button variant="success" fullWidth onClick={handleProceedToResumeSelection}>
                  Continue with Selected Job →
                </Button>
              </div>
            )}
          </div>
        )}

        {/* STEP 2.5: Resume Selection */}
        {currentStep === 2.5 && showResumeSelection && (
          <Card className="animate-fadeIn max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-neutral-900 mb-4">Step 3: Choose Resume</h2>
            <p className="text-neutral-600 mb-6">
              Select which resume to optimize for: <strong>{selectedJob.title}</strong> at <strong>{selectedJob.company}</strong>
            </p>

            <div className="space-y-4">
              {/* Option 1: Use Resume from Profile */}
              {currentResume && (
                <Card className="bg-neutral-50 hover:bg-neutral-100 cursor-pointer transition-all border-2 border-neutral-200 hover:border-success">
                  <div onClick={handleUseProfileResume} className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">
                        <svg className="w-12 h-12 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-neutral-900 mb-1">Use Resume from Profile</h3>
                        <p className="text-sm text-neutral-600 mb-2">
                          Continue with your uploaded resume: <strong>{currentResume.filename}</strong>
                        </p>
                        <div className="flex gap-3">
                          <Button variant="success" onClick={handleUseProfileResume}>
                            Use This Resume →
                          </Button>
                          {user?.resume_parsed_data && (
                            <Button
                              variant="secondary"
                              onClick={(e) => {
                                e.stopPropagation();
                                setParsedResumeData(user.resume_parsed_data);
                                setShowParsedEditor(true);
                              }}
                              className="flex items-center gap-2"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                              </svg>
                              Edit Resume
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              )}

              {/* Option 2: Upload New Resume */}
              <Card className="bg-neutral-50">
                <div className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <svg className="w-12 h-12 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-neutral-900 mb-1">Upload a Different Resume</h3>
                      <p className="text-sm text-neutral-600 mb-4">
                        Upload a new PDF or DOCX file to use for this optimization
                      </p>
                      <div
                        {...resumeDropzone.getRootProps()}
                        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all ${
                          resumeDropzone.isDragActive
                            ? 'border-success bg-success-50'
                            : 'border-neutral-300 hover:border-primary bg-white'
                        }`}
                      >
                        <input {...resumeDropzone.getInputProps()} />
                        {uploadingResume ? (
                          <LoadingSpinner />
                        ) : (
                          <>
                            <svg className="w-12 h-12 mx-auto text-neutral-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            <p className="text-sm text-neutral-700 mb-1">
                              {resumeDropzone.isDragActive ? 'Drop your resume here' : 'Drag and drop your resume, or click to browse'}
                            </p>
                            <p className="text-xs text-neutral-500">PDF or DOCX (max 5MB)</p>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>

            <div className="mt-6 flex gap-4">
              <Button variant="outline" fullWidth onClick={() => {
                setShowResumeSelection(false);
                setCurrentStep(2);
              }}>
                ← Back to Jobs
              </Button>
            </div>
          </Card>
        )}

        {/* STEP 3: Optimized Resume */}
        {currentStep === 3 && optimizedResume && (
          <Card className="animate-fadeIn max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-neutral-900 mb-4">Step 3: Your Optimized Resume</h2>
            <p className="text-neutral-600 mb-6">
              Your resume has been optimized for: <strong>{optimizedResume.job_info?.title}</strong> at <strong>{optimizedResume.job_info?.company}</strong>
            </p>

            {/* Match Analysis */}
            {optimizedResume.match_analysis && (
              <div className="bg-success-50 border border-success-200 rounded-lg p-5 mb-6">
                <div className="flex items-center gap-3 mb-4">
                  <svg className="w-8 h-8 text-success" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div className="flex-1">
                    <h3 className="font-semibold text-success-900 text-lg">
                      {Math.round(optimizedResume.match_analysis.overall_score)}% ATS Match Score!
                    </h3>
                    <p className="text-sm text-success-800">
                      Your resume has been optimized to match this specific job posting
                    </p>
                  </div>
                </div>

                {/* Match Details */}
                {optimizedResume.match_analysis.keyword_match && (
                  <div className="mt-4 pt-4 border-t border-success-200">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-success-900 font-medium mb-2">
                          ✓ Matched Skills ({optimizedResume.match_analysis.keyword_match.matched_count || 0})
                        </p>
                        {optimizedResume.match_analysis.keyword_match.matched_skills?.slice(0, 5).map((skill, idx) => (
                          <div key={idx} className="text-success-700 text-xs">• {skill}</div>
                        ))}
                        {optimizedResume.match_analysis.keyword_match.matched_skills?.length > 5 && (
                          <div className="text-success-700 text-xs mt-1">
                            +{optimizedResume.match_analysis.keyword_match.matched_skills.length - 5} more
                          </div>
                        )}
                      </div>
                      <div>
                        <p className="text-warning-900 font-medium mb-2">
                          Missing Skills ({optimizedResume.match_analysis.keyword_match.missing_skills?.length || 0})
                        </p>
                        {optimizedResume.match_analysis.keyword_match.missing_skills?.slice(0, 5).map((skill, idx) => (
                          <div key={idx} className="text-warning-700 text-xs">• {skill}</div>
                        ))}
                        {optimizedResume.match_analysis.keyword_match.missing_skills?.length > 5 && (
                          <div className="text-warning-700 text-xs mt-1">
                            +{optimizedResume.match_analysis.keyword_match.missing_skills.length - 5} more
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Usage Info */}
            {optimizedResume.usage_info && (
              <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-4 mb-6">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-neutral-700">Resumes Generated This Month</span>
                  <span className="font-semibold text-neutral-900">
                    {optimizedResume.usage_info.used} / {optimizedResume.usage_info.limit || '∞'}
                  </span>
                </div>
                {optimizedResume.usage_info.remaining !== null && optimizedResume.usage_info.remaining <= 1 && (
                  <p className="text-xs text-warning-700 mt-2">
                    ⚠️ You have {optimizedResume.usage_info.remaining} resume{optimizedResume.usage_info.remaining !== 1 ? 's' : ''} remaining this month
                  </p>
                )}
              </div>
            )}

            {/* Job Info */}
            {optimizedResume.job_info && (
              <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-4 mb-6">
                <h4 className="font-semibold text-neutral-900 mb-3">Job Details</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-neutral-600">Position:</span>
                    <span className="font-medium text-neutral-900">{optimizedResume.job_info.title}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-600">Company:</span>
                    <span className="font-medium text-neutral-900">{optimizedResume.job_info.company}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-600">Location:</span>
                    <span className="font-medium text-neutral-900">{optimizedResume.job_info.location}</span>
                  </div>
                  {optimizedResume.job_info.salary_min && optimizedResume.job_info.salary_max && (
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Salary:</span>
                      <span className="font-medium text-neutral-900">
                        ${optimizedResume.job_info.salary_min.toLocaleString()} - ${optimizedResume.job_info.salary_max.toLocaleString()}
                      </span>
                    </div>
                  )}
                  {optimizedResume.job_info.url && (
                    <div className="pt-2">
                      <a
                        href={optimizedResume.job_info.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:text-primary-dark text-sm flex items-center gap-1"
                      >
                        View Original Job Posting
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-4">
              <Button variant="outline" fullWidth onClick={() => {
                setCurrentStep(1);
                setSelectedJob(null);
                setOptimizedResume(null);
              }}>
                ← New Search
              </Button>
              <Button variant="success" fullWidth onClick={handleDownload}>
                Download Resume (DOCX) →
              </Button>
            </div>
          </Card>
        )}

        {/* Subscription Modal */}
        <SubscriptionModal
          isOpen={showSubscriptionModal}
          onClose={() => setShowSubscriptionModal(false)}
          usageInfo={subscriptionUsageInfo}
        />
      </div>
    </div>
  );
};

export default AdzunaWorkflowPage;
