import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { Button, Card, LoadingSpinner, ChatWindow } from '../Shared';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import ResumeEditor from './ResumeEditor';

const ManualWorkflowPage = () => {
  const navigate = useNavigate();
  const { user, setUser } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Resume state
  const [currentResume, setCurrentResume] = useState(null);
  const [uploadingResume, setUploadingResume] = useState(false);

  // Step 1: Job Description
  const [jobDescription, setJobDescription] = useState('');

  // Step 2: Match Analysis Results
  const [matchResults, setMatchResults] = useState(null);

  // Step 3: Optimized Resume
  const [optimizedResume, setOptimizedResume] = useState(null);
  const [showEditor, setShowEditor] = useState(false);

  // Parsed Resume Editor (before analysis)
  const [showParsedEditor, setShowParsedEditor] = useState(false);
  const [parsedResumeData, setParsedResumeData] = useState(null);

  // Load current resume on mount
  useEffect(() => {
    if (user?.resume_file_path) {
      // Extract filename from path (handles both forward and back slashes)
      const filename = user.resume_file_path.split(/[/\\]/).pop();
      setCurrentResume({
        filename: filename,
        path: user.resume_file_path,
      });
    }
  }, [user]);

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

      console.log('[WORKFLOW] Uploading file:', file.name, file.type);

      const response = await api.post('/api/resume/upload', formData);

      console.log('[WORKFLOW] Response received:', response.status, response.statusText);
      console.log('[WORKFLOW] Response data:', response.data);

      if (!response.data || !response.data.user) {
        throw new Error('Invalid response structure');
      }

      setCurrentResume({
        filename: file.name,
        path: response.data.user.resume_file_path,
      });

      setUser(response.data.user);
      toast.success('Resume uploaded successfully!');
      console.log('[WORKFLOW] Resume updated:', response.data.user.resume_file_path);
    } catch (error) {
      console.error('[WORKFLOW] Upload error:', error);
      console.error('[WORKFLOW] Error response:', error.response?.data);
      console.error('[WORKFLOW] Error message:', error.message);
      toast.error(error.response?.data?.detail || error.message || 'Failed to upload resume');
    } finally {
      setUploadingResume(false);
    }
  };

  const handleSaveParsedResumeEdits = async (editedResume) => {
    setLoading(true);
    try {
      console.log('[EDIT] Saving edited parsed resume...');

      // Call backend to update parsed resume data
      const response = await api.put('/api/resume/edit', editedResume);

      console.log('[EDIT] Save successful:', response.data);

      // Update user context with new parsed data
      setUser({
        ...user,
        resume_parsed_data: response.data.updated_data
      });

      // Update local state
      setParsedResumeData(response.data.updated_data);
      setShowParsedEditor(false);

      toast.success('Resume updated successfully!');
    } catch (error) {
      console.error('[EDIT] Save error:', error);
      toast.error(error.response?.data?.detail || 'Failed to save resume edits');
    } finally {
      setLoading(false);
    }
  };

  const handlePasteJD = async () => {
    // Check if user has a resume
    if (!currentResume && !user?.resume_file_path) {
      toast.error('Please upload a resume first');
      return;
    }
    if (!jobDescription.trim()) {
      toast.error('Please paste a job description');
      return;
    }

    setLoading(true);
    try {
      // Call backend to analyze match
      const response = await api.post('/api/generation/manual', {
        job_description: jobDescription,
      });

      setMatchResults(response.data);
      setCurrentStep(2);
      toast.success('Job description analyzed successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to analyze job description');
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async () => {
    setLoading(true);
    try {
      console.log('[OPTIMIZE] Starting optimization...');
      console.log('[OPTIMIZE] Job description length:', jobDescription?.length);
      console.log('[OPTIMIZE] Match results:', matchResults);

      // Call backend to optimize resume
      const response = await api.post('/api/generation/optimize', {
        job_description: jobDescription,
        match_results: matchResults,
      });

      console.log('[OPTIMIZE] Success! Response:', response.data);
      setOptimizedResume(response.data);
      setCurrentStep(3);
      toast.success('Resume optimized successfully!');
    } catch (error) {
      console.error('[OPTIMIZE] Error:', error);
      console.error('[OPTIMIZE] Error response:', error.response?.data);
      console.error('[OPTIMIZE] Error status:', error.response?.status);
      toast.error(error.response?.data?.detail || 'Failed to optimize resume');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      // Download optimized resume as DOCX using the download_url from response
      const downloadUrl = optimizedResume.download_url || `/api/generation/download/${optimizedResume.docx_filename}`;

      const response = await api.get(downloadUrl, {
        responseType: 'blob',
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', optimizedResume.docx_filename || 'optimized_resume.docx');
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Resume downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download resume');
    }
  };

  const handleSaveResumeEdits = async (editedResume) => {
    setLoading(true);
    try {
      console.log('[SAVE] Regenerating resume with edits...');

      // Call backend to regenerate DOCX with edited data
      const response = await api.post('/api/generation/regenerate', {
        resume_data: editedResume
      });

      console.log('[SAVE] Regeneration successful:', response.data);

      // Update optimized resume with new data and download URL
      setOptimizedResume({
        ...optimizedResume,
        optimized_resume: editedResume,
        data: editedResume,
        docx_filename: response.data.docx_filename,
        download_url: response.data.download_url
      });

      setShowEditor(false);
      toast.success('Resume saved and DOCX regenerated!');
    } catch (error) {
      console.error('[SAVE] Error:', error);
      toast.error(error.response?.data?.detail || 'Failed to save changes');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <div className="min-h-screen bg-neutral-50 py-12 px-4 sm:px-6 lg:px-8">
      {/* Parsed Resume Editor Modal */}
      {showParsedEditor && parsedResumeData && (
        <div className="fixed inset-0 bg-black/50 z-50 overflow-y-auto">
          <div className="min-h-screen px-4 py-8">
            <div className="max-w-5xl mx-auto bg-white rounded-lg shadow-xl">
              <div className="sticky top-0 bg-white border-b border-neutral-200 px-6 py-4 rounded-t-lg z-10">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-neutral-900">Edit Parsed Resume</h2>
                    <p className="text-sm text-neutral-600 mt-1">
                      Make changes to your resume before running job match analysis
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

              <div className="px-6 py-4 max-h-[calc(100vh-200px)] overflow-y-auto">
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

      <div className="max-w-5xl mx-auto">
        {/* Header */}
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
          <h1 className="text-4xl font-bold text-neutral-900 mb-2">Manual Job Description Workflow</h1>
          <p className="text-lg text-neutral-600">
            Paste a job description and optimize your resume for the role
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex items-center justify-center">
            {[1, 2, 3].map((step) => (
              <React.Fragment key={step}>
                <div
                  className={`flex items-center justify-center w-12 h-12 rounded-full font-semibold ${
                    currentStep >= step
                      ? 'bg-primary text-white'
                      : 'bg-neutral-200 text-neutral-600'
                  }`}
                >
                  {step}
                </div>
                {step < 3 && (
                  <div
                    className={`w-24 h-1 mx-2 ${
                      currentStep > step ? 'bg-primary' : 'bg-neutral-200'
                    }`}
                  ></div>
                )}
              </React.Fragment>
            ))}
          </div>
          <div className="flex justify-between mt-4 text-sm text-neutral-600 max-w-lg mx-auto">
            <span className={currentStep === 1 ? 'font-semibold text-primary' : ''}>
              Paste JD
            </span>
            <span className={currentStep === 2 ? 'font-semibold text-primary' : ''}>
              Match Analysis
            </span>
            <span className={currentStep === 3 ? 'font-semibold text-primary' : ''}>
              Optimized Resume
            </span>
          </div>
        </div>

        {/* STEP 1: Resume & Job Description */}
        {currentStep === 1 && (
          <div className="space-y-6 animate-fadeIn">
            {/* Current Resume Card */}
            <Card>
              <h2 className="text-xl font-bold text-neutral-900 mb-4">Your Resume</h2>

              {currentResume ? (
                <div className="mb-4">
                  <div className="flex items-center justify-between p-4 bg-success-50 border border-success-200 rounded-lg">
                    <div className="flex items-center gap-3">
                      <svg className="w-8 h-8 text-success" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                      </svg>
                      <div>
                        <div className="font-medium text-success-900">Resume Loaded</div>
                        <div className="text-sm text-success-700">{currentResume.filename}</div>
                      </div>
                    </div>
                    {user?.resume_parsed_data && (
                      <Button
                        variant="secondary"
                        onClick={() => {
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
              ) : (
                <div className="mb-4 p-4 bg-warning-50 border border-warning-200 rounded-lg">
                  <p className="text-warning-800 text-sm">
                    <strong>No resume found.</strong> Please upload your resume to continue.
                  </p>
                </div>
              )}

              {/* Upload new resume */}
              <div
                {...resumeDropzone.getRootProps()}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  uploadingResume ? 'border-neutral-300 bg-neutral-50' : 'border-neutral-300 hover:border-primary'
                }`}
              >
                <input {...resumeDropzone.getInputProps()} disabled={uploadingResume} />
                {uploadingResume ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary"></div>
                    <span className="text-neutral-600">Uploading...</span>
                  </div>
                ) : (
                  <>
                    <svg className="w-12 h-12 mx-auto mb-3 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="text-neutral-700 mb-1">
                      {currentResume ? 'Upload a different resume' : 'Upload your resume'}
                    </p>
                    <p className="text-sm text-neutral-500">PDF or DOCX, max 5MB</p>
                  </>
                )}
              </div>
            </Card>

            {/* Job Description Card */}
            <Card>
              <h2 className="text-2xl font-bold text-neutral-900 mb-4">Paste Job Description</h2>
              <p className="text-neutral-600 mb-6">
                Copy and paste the full job description you want to apply for.
              </p>

              <div className="mb-6">
                <label className="label">Job Description *</label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  rows={15}
                  className="input font-mono text-sm"
                  placeholder="Paste the job description here..."
                />
                <div className="flex justify-between items-center mt-2">
                  <span className="text-sm text-neutral-500">
                    {jobDescription.length} characters
                  </span>
                </div>
              </div>

              <div className="flex gap-4">
                <Button
                  variant="secondary"
                  fullWidth
                  onClick={() => navigate('/dashboard')}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  fullWidth
                  onClick={handlePasteJD}
                  disabled={!jobDescription.trim() || (!currentResume && !user?.resume_file_path)}
                >
                  Analyze Match →
                </Button>
              </div>
            </Card>
          </div>
        )}

        {/* STEP 2: Match Analysis */}
        {currentStep === 2 && matchResults && (
          <Card className="animate-fadeIn">
            <h2 className="text-2xl font-bold text-neutral-900 mb-4">Step 2: Match Analysis</h2>
            <p className="text-neutral-600 mb-6">
              Here's how your current resume matches the job description
            </p>

            {/* Overall Score */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-neutral-900">Overall Match Score</span>
                <span className="text-3xl font-bold text-primary">
                  {Math.round(matchResults.overall_score || 0)}%
                </span>
              </div>
              <div className="w-full bg-neutral-200 rounded-full h-4">
                <div
                  className="bg-primary h-4 rounded-full transition-all duration-1000"
                  style={{ width: `${matchResults.overall_score || 0}%` }}
                ></div>
              </div>
            </div>

            {/* Matched Skills */}
            {matchResults.matched_skills && matchResults.matched_skills.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold text-neutral-900 mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5 text-success" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Matched Skills ({matchResults.matched_skills.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {matchResults.matched_skills.slice(0, 10).map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-success-50 text-success-700 rounded-full text-sm font-medium border border-success-200"
                    >
                      {typeof skill === 'object' ? (skill.required || skill.matched_as || skill.skill || skill) : skill}
                    </span>
                  ))}
                  {matchResults.matched_skills.length > 10 && (
                    <span className="px-3 py-1 bg-neutral-100 text-neutral-600 rounded-full text-sm">
                      +{matchResults.matched_skills.length - 10} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Missing Skills */}
            {matchResults.missing_skills && matchResults.missing_skills.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold text-neutral-900 mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5 text-warning" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Missing Skills ({matchResults.missing_skills.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {matchResults.missing_skills.slice(0, 10).map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-warning-50 text-warning-700 rounded-full text-sm font-medium border border-warning-200"
                    >
                      {typeof skill === 'string' ? skill : (typeof skill === 'object' ? (skill.required || skill.skill || JSON.stringify(skill)) : skill)}
                    </span>
                  ))}
                  {matchResults.missing_skills.length > 10 && (
                    <span className="px-3 py-1 bg-neutral-100 text-neutral-600 rounded-full text-sm">
                      +{matchResults.missing_skills.length - 10} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {matchResults.recommendations && matchResults.recommendations.length > 0 && (
              <div className="mb-6 p-4 bg-primary-50 border border-primary-200 rounded-lg">
                <h3 className="font-semibold text-primary-900 mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
                  </svg>
                  Recommendations
                </h3>
                <ul className="space-y-2">
                  {matchResults.recommendations.map((rec, idx) => (
                    <li key={idx} className="text-sm text-primary-800 flex items-start gap-2">
                      <span className="text-primary-600 mt-0.5">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex gap-4">
              <Button
                variant="secondary"
                fullWidth
                onClick={() => setCurrentStep(1)}
              >
                ← Back
              </Button>
              <Button
                variant="primary"
                fullWidth
                onClick={handleOptimize}
              >
                Optimize Resume →
              </Button>
            </div>
          </Card>
        )}

        {/* STEP 3: Optimized Resume */}
        {currentStep === 3 && optimizedResume && (
          <div className="space-y-6 animate-fadeIn">
            {/* ATS Score Display */}
            {optimizedResume.match_analysis && (
              <Card>
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
                        Your resume has been optimized to match the job requirements
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
              </Card>
            )}

            {/* Success Banner + Action Buttons */}
            <Card>
              <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-4 mb-6">
                <div className="flex items-center gap-3">
                  <svg className="w-8 h-8 text-neutral-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div className="flex-1">
                    <h3 className="font-semibold text-neutral-900">Optimization Complete!</h3>
                    <p className="text-sm text-neutral-700">
                      Your resume is ready for download
                    </p>
                  </div>
                </div>
              </div>

              {/* Toggle and Download Buttons */}
              <div className="flex gap-3 mb-6">
                <Button
                  variant={!showEditor ? "primary" : "outline"}
                  onClick={() => setShowEditor(false)}
                  className="flex-1"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  Preview
                </Button>
                <Button
                  variant={showEditor ? "primary" : "outline"}
                  onClick={() => setShowEditor(true)}
                  className="flex-1"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Edit
                </Button>
                <Button
                  variant="success"
                  onClick={handleDownload}
                  className="flex-1"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download DOCX
                </Button>
              </div>
            </Card>

            {/* Editor or Preview */}
            {showEditor ? (
              <ResumeEditor
                resume={optimizedResume.optimized_resume || optimizedResume.data}
                onSave={handleSaveResumeEdits}
                onCancel={() => setShowEditor(false)}
              />
            ) : (
              <Card>
              {/* Resume Preview */}
              {optimizedResume.optimized_resume && (
                <div className="border border-neutral-200 rounded-lg p-6 mb-6 bg-white max-h-96 overflow-y-auto">
                  <h3 className="font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Resume Preview
                  </h3>

                  {/* Contact Info */}
                  {optimizedResume.optimized_resume.contact_info && (
                    <div className="mb-4 pb-4 border-b border-neutral-200">
                      <h4 className="font-bold text-lg text-neutral-900">
                        {optimizedResume.optimized_resume.contact_info.name || 'Name'}
                      </h4>
                      <p className="text-sm text-neutral-600 space-x-2">
                        {optimizedResume.optimized_resume.contact_info.email && (
                          <span>{optimizedResume.optimized_resume.contact_info.email}</span>
                        )}
                        {optimizedResume.optimized_resume.contact_info.phone && (
                          <span>• {optimizedResume.optimized_resume.contact_info.phone}</span>
                        )}
                        {optimizedResume.optimized_resume.contact_info.location && (
                          <span>• {optimizedResume.optimized_resume.contact_info.location}</span>
                        )}
                      </p>
                    </div>
                  )}

                  {/* Professional Summary */}
                  {optimizedResume.optimized_resume.professional_summary && (
                    <div className="mb-4">
                      <h4 className="font-semibold text-neutral-900 mb-2">Professional Summary</h4>
                      <p className="text-sm text-neutral-700 leading-relaxed">
                        {optimizedResume.optimized_resume.professional_summary}
                      </p>
                    </div>
                  )}

                  {/* Skills Preview */}
                  {optimizedResume.optimized_resume.skills && optimizedResume.optimized_resume.skills.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-semibold text-neutral-900 mb-2">Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {optimizedResume.optimized_resume.skills.slice(0, 15).map((skill, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-primary-50 text-primary-700 rounded text-xs border border-primary-200"
                          >
                            {skill}
                          </span>
                        ))}
                        {optimizedResume.optimized_resume.skills.length > 15 && (
                          <span className="px-2 py-1 bg-neutral-100 text-neutral-600 rounded text-xs">
                            +{optimizedResume.optimized_resume.skills.length - 15} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Experience Count */}
                  {optimizedResume.optimized_resume.experience && (
                    <div className="text-sm text-neutral-600">
                      <span className="font-medium">{optimizedResume.optimized_resume.experience.length}</span> experience entries optimized
                    </div>
                  )}
                </div>
              )}
              </Card>
            )}
          </div>
        )}
      </div>

      {/* Chat Window - Available from Step 2 onwards */}
      {currentStep >= 2 && (
        <ChatWindow
          resume={optimizedResume?.optimized_resume || optimizedResume?.data || user?.resume_parsed_data}
          jobDescription={jobDescription}
        />
      )}
    </div>
  );
};

export default ManualWorkflowPage;
