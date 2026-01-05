import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '../../context/AuthContext';
import { Button, Card } from '../Shared';
import api from '../../services/api';
import ResumeEditor from '../Workflow/ResumeEditor';

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user, setUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);

  // Resume editor state
  const [showResumeEditor, setShowResumeEditor] = useState(false);
  const [parsedResumeData, setParsedResumeData] = useState(null);

  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    address: user?.address || '',
  });

  const profilePicDropzone = useDropzone({
    accept: { 'image/jpeg': ['.jpg', '.jpeg'], 'image/png': ['.png'] },
    maxSize: 2097152,
    multiple: false,
    onDrop: async (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        await handleUploadProfilePic(acceptedFiles[0]);
      }
    },
  });

  const resumeDropzone = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 5242880,
    multiple: false,
    onDrop: async (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        await handleUploadResume(acceptedFiles[0]);
      }
    },
  });

  const handleUploadProfilePic = async (file) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('profile_pic', file);

      console.log('[PROFILE PIC] Uploading file:', file.name, file.type);

      const response = await api.post('/api/profile/upload-picture', formData);

      console.log('[PROFILE PIC] Response received:', response.status, response.statusText);
      console.log('[PROFILE PIC] Response data:', response.data);

      if (!response.data || !response.data.user) {
        throw new Error('Invalid response structure');
      }

      setUser(response.data.user);
      toast.success('Profile picture updated successfully!');
      console.log('[PROFILE PIC] Profile picture path:', response.data.user.profile_pic_path);
    } catch (error) {
      console.error('[PROFILE PIC] Upload error:', error);
      console.error('[PROFILE PIC] Error response:', error.response?.data);
      console.error('[PROFILE PIC] Error message:', error.message);
      toast.error(error.response?.data?.detail || error.message || 'Failed to upload profile picture');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadResume = async (file) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('resume', file);

      console.log('[RESUME] Uploading file:', file.name, file.type);

      // Don't set Content-Type manually - axios will set it with boundary
      const response = await api.post('/api/resume/upload', formData);

      console.log('[RESUME] Response received:', response.status, response.statusText);
      console.log('[RESUME] Response data:', response.data);
      console.log('[RESUME] User data:', response.data.user);

      if (!response.data || !response.data.user) {
        throw new Error('Invalid response structure');
      }

      setUser(response.data.user);
      toast.success('Resume uploaded and parsed successfully!');
      console.log('[RESUME] Parsed data keys:', Object.keys(response.data.parsed_data || {}));
    } catch (error) {
      console.error('[RESUME] Upload error:', error);
      console.error('[RESUME] Error response:', error.response?.data);
      console.error('[RESUME] Error message:', error.message);
      toast.error(error.response?.data?.detail || error.message || 'Failed to upload resume');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    setLoading(true);
    try {
      const response = await api.put('/api/profile/update', profileData);
      setUser(response.data.user);
      setEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setProfileData({
      full_name: user?.full_name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      address: user?.address || '',
    });
    setEditing(false);
  };

  const handleSaveResumeEdits = async (editedResume) => {
    setLoading(true);
    try {
      const response = await api.put('/api/resume/edit', editedResume);

      setUser({
        ...user,
        resume_parsed_data: response.data.updated_data
      });

      setParsedResumeData(response.data.updated_data);
      setShowResumeEditor(false);
      toast.success('Resume updated successfully!');
    } catch (error) {
      console.error('[EDIT] Error:', error);
      toast.error(error.response?.data?.detail || 'Failed to save changes');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50 py-12 px-4 sm:px-6 lg:px-8">
      {/* Resume Editor Modal */}
      {showResumeEditor && parsedResumeData && (
        <div className="fixed inset-0 bg-black/50 z-50 overflow-y-auto">
          <div className="min-h-screen px-4 py-8">
            <div className="max-w-5xl mx-auto bg-white rounded-lg shadow-xl">
              <div className="sticky top-0 bg-white border-b border-neutral-200 px-6 py-4 rounded-t-lg z-10">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-neutral-900">Edit Resume</h2>
                    <p className="text-sm text-neutral-600 mt-1">
                      Make changes to your parsed resume data
                    </p>
                  </div>
                  <button
                    onClick={() => setShowResumeEditor(false)}
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
                  onSave={handleSaveResumeEdits}
                  onCancel={() => setShowResumeEditor(false)}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-5xl mx-auto">
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
          <h1 className="text-4xl font-bold text-neutral-900 mb-2">My Profile</h1>
          <p className="text-lg text-neutral-600">Manage your account information and resume</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Profile Picture & Quick Actions */}
          <div className="space-y-6">
            <Card>
              <h3 className="font-semibold text-neutral-900 mb-4">Profile Picture</h3>
              <div
                {...profilePicDropzone.getRootProps()}
                className="cursor-pointer hover:opacity-80 transition-opacity"
              >
                <input {...profilePicDropzone.getInputProps()} />
                <div className="flex flex-col items-center">
                  {user?.profile_pic_path ? (
                    <img
                      src={`${process.env.REACT_APP_API_URL}/${user.profile_pic_path}`}
                      alt="Profile"
                      className="w-32 h-32 rounded-full object-cover mb-4 border-4 border-neutral-200"
                    />
                  ) : (
                    <div className="w-32 h-32 rounded-full bg-primary-100 flex items-center justify-center mb-4">
                      <svg className="w-16 h-16 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                  )}
                  <p className="text-sm text-neutral-600 text-center">
                    Click to upload new photo<br />
                    <span className="text-xs text-neutral-500">JPG or PNG, max 2MB</span>
                  </p>
                </div>
              </div>
            </Card>

            <Card>
              <h3 className="font-semibold text-neutral-900 mb-4">Account Info</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-neutral-500">Member Since</span>
                  <div className="font-medium text-neutral-900">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) : 'N/A'}
                  </div>
                </div>
                <div>
                  <span className="text-neutral-500">Account Status</span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="w-2 h-2 rounded-full bg-success"></span>
                    <span className="font-medium text-neutral-900">Active</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Right Column - Profile Information & Resume */}
          <div className="lg:col-span-2 space-y-6">
            {/* Profile Information */}
            <Card>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-neutral-900">Profile Information</h3>
                {!editing && (
                  <Button variant="outline" onClick={() => setEditing(true)}>
                    Edit Profile
                  </Button>
                )}
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="label">Full Name</label>
                    {editing ? (
                      <input
                        type="text"
                        value={profileData.full_name}
                        onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                        className="input"
                      />
                    ) : (
                      <div className="text-neutral-900">{user?.full_name || 'Not provided'}</div>
                    )}
                  </div>
                  <div>
                    <label className="label">Email</label>
                    <div className="text-neutral-900">{user?.email}</div>
                    {editing && <p className="text-xs text-neutral-500 mt-1">Email cannot be changed</p>}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="label">Phone</label>
                    {editing ? (
                      <input
                        type="tel"
                        value={profileData.phone}
                        onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                        className="input"
                      />
                    ) : (
                      <div className="text-neutral-900">{user?.phone || 'Not provided'}</div>
                    )}
                  </div>
                  <div>
                    <label className="label">Address</label>
                    {editing ? (
                      <input
                        type="text"
                        value={profileData.address}
                        onChange={(e) => setProfileData({ ...profileData, address: e.target.value })}
                        className="input"
                      />
                    ) : (
                      <div className="text-neutral-900">{user?.address || 'Not provided'}</div>
                    )}
                  </div>
                </div>

                {editing && (
                  <div className="flex gap-4 pt-4">
                    <Button variant="secondary" fullWidth onClick={handleCancelEdit}>
                      Cancel
                    </Button>
                    <Button variant="primary" fullWidth onClick={handleSaveProfile} loading={loading}>
                      Save Changes
                    </Button>
                  </div>
                )}
              </div>
            </Card>

            {/* Resume */}
            <Card>
              <h3 className="text-xl font-semibold text-neutral-900 mb-4">Resume</h3>

              {user?.resume_file_path ? (
                <div className="mb-6">
                  <div className="flex items-center justify-between p-4 bg-success-50 border border-success-200 rounded-lg mb-4">
                    <div className="flex items-center gap-3">
                      <svg className="w-8 h-8 text-success" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                      </svg>
                      <div className="flex-1">
                        <div className="font-medium text-success-900">Resume Uploaded</div>
                        <div className="text-sm text-success-700">
                          {user.resume_file_path.split(/[/\\]/).pop()}
                        </div>
                      </div>
                    </div>
                    {user?.resume_parsed_data && (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setParsedResumeData(user.resume_parsed_data);
                          setShowResumeEditor(true);
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
                <div className="mb-6 p-4 bg-neutral-100 border border-neutral-300 rounded-lg">
                  <p className="text-neutral-600 text-center">No resume uploaded yet</p>
                </div>
              )}

              <div
                {...resumeDropzone.getRootProps()}
                className="border-2 border-dashed border-neutral-300 rounded-lg p-6 text-center cursor-pointer hover:border-primary transition-colors"
              >
                <input {...resumeDropzone.getInputProps()} />
                <svg className="w-12 h-12 mx-auto mb-3 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-neutral-700 mb-1">
                  {user?.resume_file_path ? 'Upload new resume' : 'Upload your resume'}
                </p>
                <p className="text-sm text-neutral-500">PDF or DOCX, max 5MB</p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
