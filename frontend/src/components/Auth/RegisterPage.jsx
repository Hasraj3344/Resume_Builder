import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '../../context/AuthContext';
import { Button, Card, LoadingSpinner } from '../Shared';
import api from '../../services/api';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, loading: authLoading } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [parsing, setParsing] = useState(false);

  // Step 1: Basic Info
  const [basicInfo, setBasicInfo] = useState({
    full_name: '',
    email: '',
    phone: '',
    address: '',
    profile_pic: null,
    password: '',
    confirmPassword: '',
  });

  // Step 2: Resume Upload
  const [resume, setResume] = useState(null);

  // Step 3: Parsed Resume Data
  const [parsedData, setParsedData] = useState({
    education: [],
    experience: [],
    projects: [],
    certifications: [],
    skills: [],
  });

  const [errors, setErrors] = useState({});

  // Profile Picture Dropzone
  const profilePicDropzone = useDropzone({
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxSize: 2097152, // 2MB
    multiple: false,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setBasicInfo((prev) => ({ ...prev, profile_pic: acceptedFiles[0] }));
        toast.success('Profile picture uploaded');
      }
    },
    onDropRejected: () => {
      toast.error('Invalid image file (max 2MB, JPG/PNG only)');
    },
  });

  // Resume Dropzone
  const resumeDropzone = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 5242880, // 5MB
    multiple: false,
    onDrop: async (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        setResume(file);
        toast.success('Resume uploaded. Parsing...');
        await parseResume(file);
      }
    },
    onDropRejected: (fileRejections) => {
      const error = fileRejections[0]?.errors[0];
      if (error?.code === 'file-too-large') {
        toast.error('File size must be less than 5MB');
      } else {
        toast.error('Only PDF and DOCX files are allowed');
      }
    },
  });

  // Parse resume using backend API
  const parseResume = async (file) => {
    setParsing(true);
    try {
      const formData = new FormData();
      formData.append('resume', file);

      // Call backend resume parsing endpoint
      const response = await api.post('/api/resume/parse', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = response.data;

      // Set parsed data
      setParsedData({
        education: data.education || [],
        experience: data.experience || [],
        projects: data.projects || [],
        certifications: data.certifications || [],
        skills: data.skills || [],
      });

      // Auto-fill name, email, phone if found in resume
      if (data.contact_info) {
        setBasicInfo((prev) => ({
          ...prev,
          full_name: data.contact_info.name || prev.full_name,
          email: data.contact_info.email || prev.email,
          phone: data.contact_info.phone || prev.phone,
        }));
      }

      toast.success('Resume parsed successfully!');
      setCurrentStep(3); // Move to review step
    } catch (error) {
      toast.error(error.message || 'Failed to parse resume');
    } finally {
      setParsing(false);
    }
  };

  const handleBasicInfoChange = (e) => {
    const { name, value } = e.target;
    setBasicInfo((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validateStep1 = () => {
    const newErrors = {};

    if (!basicInfo.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    }

    if (!basicInfo.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(basicInfo.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!basicInfo.phone) {
      newErrors.phone = 'Phone number is required';
    }

    if (!basicInfo.password) {
      newErrors.password = 'Password is required';
    } else if (basicInfo.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (basicInfo.password !== basicInfo.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    if (!resume) {
      toast.error('Please upload your resume');
      return false;
    }
    return true;
  };

  const handleNextStep = () => {
    if (currentStep === 1 && validateStep1()) {
      setCurrentStep(2);
    } else if (currentStep === 2 && validateStep2()) {
      // Resume parsing happens automatically in dropzone
    }
  };

  const handlePrevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Register user with all data
      await register({
        full_name: basicInfo.full_name,
        email: basicInfo.email,
        password: basicInfo.password,
        phone: basicInfo.phone,
        address: basicInfo.address,
        profile_pic: basicInfo.profile_pic,
        resume: resume,
        parsed_data: parsedData,
      });

      toast.success('Registration successful!');
      navigate('/login');
    } catch (error) {
      toast.error(error.message || 'Registration failed');
    }
  };

  if (authLoading || parsing) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <div className="min-h-screen bg-neutral-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-neutral-900 mb-2">Create Your Account</h2>
          <p className="text-neutral-600">Get started with ResumeAI for free</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center">
            {[1, 2, 3].map((step) => (
              <React.Fragment key={step}>
                <div
                  className={`flex items-center justify-center w-10 h-10 rounded-full font-semibold ${
                    currentStep >= step
                      ? 'bg-primary text-white'
                      : 'bg-neutral-200 text-neutral-600'
                  }`}
                >
                  {step}
                </div>
                {step < 3 && (
                  <div
                    className={`w-16 h-1 mx-2 ${
                      currentStep > step ? 'bg-primary' : 'bg-neutral-200'
                    }`}
                  ></div>
                )}
              </React.Fragment>
            ))}
          </div>
          <div className="flex justify-between mt-4 text-sm text-neutral-600 max-w-md mx-auto">
            <span className={currentStep === 1 ? 'font-semibold text-primary' : ''}>
              Basic Info
            </span>
            <span className={currentStep === 2 ? 'font-semibold text-primary' : ''}>
              Upload Resume
            </span>
            <span className={currentStep === 3 ? 'font-semibold text-primary' : ''}>
              Review & Confirm
            </span>
          </div>
        </div>

        <Card>
          <form onSubmit={handleSubmit}>
            {/* STEP 1: Basic Information */}
            {currentStep === 1 && (
              <div className="space-y-6 animate-fadeIn">
                <h3 className="text-xl font-semibold text-neutral-900 mb-4">Basic Information</h3>

                {/* Profile Picture */}
                <div>
                  <label className="label">Profile Picture (Optional)</label>
                  <div
                    {...profilePicDropzone.getRootProps()}
                    className="border-2 border-dashed border-neutral-300 rounded-md p-4 text-center cursor-pointer hover:border-primary transition-colors"
                  >
                    <input {...profilePicDropzone.getInputProps()} />
                    {basicInfo.profile_pic ? (
                      <div className="flex items-center justify-center gap-2">
                        <img
                          src={URL.createObjectURL(basicInfo.profile_pic)}
                          alt="Profile"
                          className="w-16 h-16 rounded-full object-cover"
                        />
                        <span className="text-sm text-success">{basicInfo.profile_pic.name}</span>
                      </div>
                    ) : (
                      <div className="text-neutral-600">
                        <svg className="w-12 h-12 mx-auto mb-2 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        <p className="text-sm">Click to upload profile picture</p>
                        <p className="text-xs text-neutral-500 mt-1">JPG or PNG, max 2MB</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Full Name */}
                <div>
                  <label htmlFor="full_name" className="label">
                    Full Name *
                  </label>
                  <input
                    id="full_name"
                    name="full_name"
                    type="text"
                    value={basicInfo.full_name}
                    onChange={handleBasicInfoChange}
                    className={`input ${errors.full_name ? 'input-error' : ''}`}
                    placeholder="John Doe"
                  />
                  {errors.full_name && <p className="error-message">{errors.full_name}</p>}
                </div>

                {/* Email */}
                <div>
                  <label htmlFor="email" className="label">
                    Email Address *
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={basicInfo.email}
                    onChange={handleBasicInfoChange}
                    className={`input ${errors.email ? 'input-error' : ''}`}
                    placeholder="you@example.com"
                  />
                  {errors.email && <p className="error-message">{errors.email}</p>}
                </div>

                {/* Phone */}
                <div>
                  <label htmlFor="phone" className="label">
                    Phone Number *
                  </label>
                  <input
                    id="phone"
                    name="phone"
                    type="tel"
                    value={basicInfo.phone}
                    onChange={handleBasicInfoChange}
                    className={`input ${errors.phone ? 'input-error' : ''}`}
                    placeholder="+1 (555) 123-4567"
                  />
                  {errors.phone && <p className="error-message">{errors.phone}</p>}
                </div>

                {/* Address */}
                <div>
                  <label htmlFor="address" className="label">
                    Address
                  </label>
                  <textarea
                    id="address"
                    name="address"
                    rows="3"
                    value={basicInfo.address}
                    onChange={handleBasicInfoChange}
                    className="input"
                    placeholder="123 Main St, City, State, ZIP"
                  />
                </div>

                {/* Password */}
                <div>
                  <label htmlFor="password" className="label">
                    Password *
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    value={basicInfo.password}
                    onChange={handleBasicInfoChange}
                    className={`input ${errors.password ? 'input-error' : ''}`}
                    placeholder="••••••••"
                  />
                  {errors.password && <p className="error-message">{errors.password}</p>}
                </div>

                {/* Confirm Password */}
                <div>
                  <label htmlFor="confirmPassword" className="label">
                    Confirm Password *
                  </label>
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    value={basicInfo.confirmPassword}
                    onChange={handleBasicInfoChange}
                    className={`input ${errors.confirmPassword ? 'input-error' : ''}`}
                    placeholder="••••••••"
                  />
                  {errors.confirmPassword && <p className="error-message">{errors.confirmPassword}</p>}
                </div>

                <Button type="button" variant="primary" fullWidth onClick={handleNextStep}>
                  Next: Upload Resume →
                </Button>
              </div>
            )}

            {/* STEP 2: Resume Upload */}
            {currentStep === 2 && (
              <div className="space-y-6 animate-fadeIn">
                <h3 className="text-xl font-semibold text-neutral-900 mb-4">Upload Your Resume</h3>
                <p className="text-neutral-600 mb-4">
                  Upload your resume and we'll automatically extract your education, experience, skills, and more.
                </p>

                <div
                  {...resumeDropzone.getRootProps()}
                  className={`border-2 border-dashed rounded-md p-8 text-center cursor-pointer transition-colors ${
                    resumeDropzone.isDragActive
                      ? 'border-primary bg-primary-50'
                      : 'border-neutral-300 hover:border-primary'
                  }`}
                >
                  <input {...resumeDropzone.getInputProps()} />
                  {resume ? (
                    <div className="flex flex-col items-center gap-3">
                      <svg className="w-16 h-16 text-success" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="font-medium text-success">{resume.name}</span>
                      <p className="text-sm text-neutral-600">Click to change file</p>
                    </div>
                  ) : (
                    <div className="text-neutral-600">
                      <svg className="w-16 h-16 mx-auto mb-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <p className="text-lg font-medium mb-2">
                        {resumeDropzone.isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
                      </p>
                      <p className="text-sm text-neutral-500">or click to browse files</p>
                      <p className="text-xs text-neutral-500 mt-2">PDF or DOCX, max 5MB</p>
                    </div>
                  )}
                </div>

                <div className="flex gap-4">
                  <Button type="button" variant="secondary" fullWidth onClick={handlePrevStep}>
                    ← Back
                  </Button>
                  <Button
                    type="button"
                    variant="primary"
                    fullWidth
                    onClick={handleNextStep}
                    disabled={!resume}
                  >
                    Parse Resume →
                  </Button>
                </div>
              </div>
            )}

            {/* STEP 3: Review & Edit Parsed Data */}
            {currentStep === 3 && (
              <div className="space-y-6 animate-fadeIn max-h-[600px] overflow-y-auto scrollbar-thin">
                <div className="sticky top-0 bg-white pb-4 border-b">
                  <h3 className="text-xl font-semibold text-neutral-900">Review & Edit Your Information</h3>
                  <p className="text-neutral-600 text-sm mt-1">
                    Please review and edit the extracted information. Click on any field to modify it.
                  </p>
                </div>

                {/* Contact Info (Editable) */}
                <div>
                  <h4 className="font-semibold text-neutral-900 mb-3">Contact Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="label">Full Name</label>
                      <input
                        type="text"
                        value={basicInfo.full_name}
                        onChange={(e) => setBasicInfo({...basicInfo, full_name: e.target.value})}
                        className="input"
                      />
                    </div>
                    <div>
                      <label className="label">Email</label>
                      <input
                        type="email"
                        value={basicInfo.email}
                        onChange={(e) => setBasicInfo({...basicInfo, email: e.target.value})}
                        className="input"
                      />
                    </div>
                    <div>
                      <label className="label">Phone</label>
                      <input
                        type="tel"
                        value={basicInfo.phone}
                        onChange={(e) => setBasicInfo({...basicInfo, phone: e.target.value})}
                        className="input"
                      />
                    </div>
                    <div>
                      <label className="label">Address</label>
                      <input
                        type="text"
                        value={basicInfo.address}
                        onChange={(e) => setBasicInfo({...basicInfo, address: e.target.value})}
                        className="input"
                        placeholder="City, State"
                      />
                    </div>
                  </div>
                </div>

                {/* Education (Editable) */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-neutral-900">Education ({parsedData.education.length})</h4>
                    <button
                      type="button"
                      onClick={() => setParsedData({
                        ...parsedData,
                        education: [...parsedData.education, {
                          institution: '',
                          degree: '',
                          field_of_study: '',
                          graduation_date: '',
                          gpa: null,
                          location: ''
                        }]
                      })}
                      className="text-primary hover:text-primary-dark text-sm font-medium"
                    >
                      + Add Education
                    </button>
                  </div>
                  <div className="space-y-3">
                    {parsedData.education.map((edu, idx) => (
                      <div key={idx} className="p-4 bg-neutral-50 rounded border border-neutral-200">
                        <div className="flex justify-between items-start mb-3">
                          <span className="text-sm font-medium text-neutral-600">Entry {idx + 1}</span>
                          <button
                            type="button"
                            onClick={() => {
                              const newEdu = parsedData.education.filter((_, i) => i !== idx);
                              setParsedData({...parsedData, education: newEdu});
                            }}
                            className="text-error hover:text-error-dark text-sm"
                          >
                            Remove
                          </button>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          <input
                            type="text"
                            value={edu.institution || ''}
                            onChange={(e) => {
                              const newEdu = [...parsedData.education];
                              newEdu[idx].institution = e.target.value;
                              setParsedData({...parsedData, education: newEdu});
                            }}
                            placeholder="Institution"
                            className="input text-sm"
                          />
                          <input
                            type="text"
                            value={edu.degree || ''}
                            onChange={(e) => {
                              const newEdu = [...parsedData.education];
                              newEdu[idx].degree = e.target.value;
                              setParsedData({...parsedData, education: newEdu});
                            }}
                            placeholder="Degree"
                            className="input text-sm"
                          />
                          <input
                            type="text"
                            value={edu.field_of_study || ''}
                            onChange={(e) => {
                              const newEdu = [...parsedData.education];
                              newEdu[idx].field_of_study = e.target.value;
                              setParsedData({...parsedData, education: newEdu});
                            }}
                            placeholder="Field of Study"
                            className="input text-sm"
                          />
                          <input
                            type="text"
                            value={edu.graduation_date || ''}
                            onChange={(e) => {
                              const newEdu = [...parsedData.education];
                              newEdu[idx].graduation_date = e.target.value;
                              setParsedData({...parsedData, education: newEdu});
                            }}
                            placeholder="Graduation Date"
                            className="input text-sm"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Experience (Editable) */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-neutral-900">Experience ({parsedData.experience.length})</h4>
                    <button
                      type="button"
                      onClick={() => setParsedData({
                        ...parsedData,
                        experience: [...parsedData.experience, {
                          company: '',
                          job_title: '',
                          location: '',
                          start_date: '',
                          end_date: '',
                          responsibilities: []
                        }]
                      })}
                      className="text-primary hover:text-primary-dark text-sm font-medium"
                    >
                      + Add Experience
                    </button>
                  </div>
                  <div className="space-y-3">
                    {parsedData.experience.map((exp, idx) => (
                      <div key={idx} className="p-4 bg-neutral-50 rounded border border-neutral-200">
                        <div className="flex justify-between items-start mb-3">
                          <span className="text-sm font-medium text-neutral-600">Position {idx + 1}</span>
                          <button
                            type="button"
                            onClick={() => {
                              const newExp = parsedData.experience.filter((_, i) => i !== idx);
                              setParsedData({...parsedData, experience: newExp});
                            }}
                            className="text-error hover:text-error-dark text-sm"
                          >
                            Remove
                          </button>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          <input
                            type="text"
                            value={exp.company || ''}
                            onChange={(e) => {
                              const newExp = [...parsedData.experience];
                              newExp[idx].company = e.target.value;
                              setParsedData({...parsedData, experience: newExp});
                            }}
                            placeholder="Company"
                            className="input text-sm"
                          />
                          <input
                            type="text"
                            value={exp.job_title || ''}
                            onChange={(e) => {
                              const newExp = [...parsedData.experience];
                              newExp[idx].job_title = e.target.value;
                              setParsedData({...parsedData, experience: newExp});
                            }}
                            placeholder="Job Title"
                            className="input text-sm"
                          />
                          <input
                            type="text"
                            value={exp.start_date || ''}
                            onChange={(e) => {
                              const newExp = [...parsedData.experience];
                              newExp[idx].start_date = e.target.value;
                              setParsedData({...parsedData, experience: newExp});
                            }}
                            placeholder="Start Date"
                            className="input text-sm"
                          />
                          <input
                            type="text"
                            value={exp.end_date || ''}
                            onChange={(e) => {
                              const newExp = [...parsedData.experience];
                              newExp[idx].end_date = e.target.value;
                              setParsedData({...parsedData, experience: newExp});
                            }}
                            placeholder="End Date or 'Present'"
                            className="input text-sm"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Skills (Editable with tags) */}
                <div>
                  <h4 className="font-semibold text-neutral-900 mb-3">Skills ({parsedData.skills.length})</h4>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {parsedData.skills.map((skill, idx) => (
                      <span key={idx} className="badge badge-primary flex items-center gap-2">
                        {skill}
                        <button
                          type="button"
                          onClick={() => {
                            const newSkills = parsedData.skills.filter((_, i) => i !== idx);
                            setParsedData({...parsedData, skills: newSkills});
                          }}
                          className="text-primary-dark hover:text-error"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Add a skill and press Enter"
                      className="input flex-1 text-sm"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && e.target.value.trim()) {
                          setParsedData({
                            ...parsedData,
                            skills: [...parsedData.skills, e.target.value.trim()]
                          });
                          e.target.value = '';
                        }
                      }}
                    />
                  </div>
                </div>

                {/* Projects (Simplified view) */}
                {parsedData.projects.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-neutral-900 mb-2">
                      Projects ({parsedData.projects.length}) - Preview
                    </h4>
                    <div className="text-sm text-neutral-600 mb-2">
                      {parsedData.projects.map((p, i) => p.title).join(', ')}
                    </div>
                    <p className="text-xs text-neutral-500">You can edit projects in your profile after registration</p>
                  </div>
                )}

                {/* Certifications (Simplified) */}
                {parsedData.certifications.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-neutral-900 mb-2">
                      Certifications ({parsedData.certifications.length}) - Preview
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {parsedData.certifications.map((cert, idx) => (
                        <span key={idx} className="badge badge-success">
                          {cert}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-primary-50 border border-primary-200 rounded-md p-4">
                  <p className="text-sm text-primary-900">
                    ✓ All information looks good? Click "Complete Registration" below to finish creating your account.
                  </p>
                </div>

                <div className="flex gap-4">
                  <Button type="button" variant="secondary" fullWidth onClick={handlePrevStep}>
                    ← Back
                  </Button>
                  <Button type="submit" variant="primary" fullWidth loading={authLoading}>
                    Complete Registration
                  </Button>
                </div>
              </div>
            )}
          </form>

          {/* Login Link */}
          <div className="text-center mt-6">
            <p className="text-sm text-neutral-600">
              Already have an account?{' '}
              <Link to="/login" className="text-primary hover:text-primary-dark font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default RegisterPage;
