import React, { useState, useEffect } from 'react';
import { Button, Card } from '../Shared';

const ResumeEditor = ({ resume, onSave, onCancel }) => {
  const [editedResume, setEditedResume] = useState(null);
  const [isModified, setIsModified] = useState(false);

  useEffect(() => {
    if (resume) {
      setEditedResume(JSON.parse(JSON.stringify(resume))); // Deep clone
    }
  }, [resume]);

  if (!editedResume) {
    return <div className="text-center py-8">Loading resume...</div>;
  }

  const handleChange = (section, field, value) => {
    setEditedResume(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
    setIsModified(true);
  };

  const handleArrayChange = (section, index, field, value) => {
    setEditedResume(prev => {
      const newArray = [...prev[section]];
      newArray[index] = {
        ...newArray[index],
        [field]: value,
        // Also update alternate field names for compatibility
        ...(field === 'title' && { job_title: value }),
        ...(field === 'job_title' && { title: value }),
      };
      return {
        ...prev,
        [section]: newArray
      };
    });
    setIsModified(true);
  };

  const handleBulletChange = (section, itemIndex, bulletIndex, value) => {
    setEditedResume(prev => {
      const newArray = [...prev[section]];
      // Read from bullets OR responsibilities to match rendering logic
      const currentBullets = newArray[itemIndex].bullets || newArray[itemIndex].responsibilities || [];
      const newBullets = [...currentBullets];
      newBullets[bulletIndex] = value;
      newArray[itemIndex] = {
        ...newArray[itemIndex],
        bullets: newBullets,
        responsibilities: newBullets // Keep both in sync
      };
      return {
        ...prev,
        [section]: newArray
      };
    });
    setIsModified(true);
  };

  const addBullet = (section, itemIndex) => {
    setEditedResume(prev => {
      const newArray = [...prev[section]];
      // Read from bullets OR responsibilities to match rendering logic
      const currentBullets = newArray[itemIndex].bullets || newArray[itemIndex].responsibilities || [];
      const newBullets = [...currentBullets, ''];
      newArray[itemIndex] = {
        ...newArray[itemIndex],
        bullets: newBullets,
        responsibilities: newBullets // Keep both in sync
      };
      return {
        ...prev,
        [section]: newArray
      };
    });
    setIsModified(true);
  };

  const removeBullet = (section, itemIndex, bulletIndex) => {
    setEditedResume(prev => {
      const newArray = [...prev[section]];
      // Read from bullets OR responsibilities to match rendering logic
      const currentBullets = newArray[itemIndex].bullets || newArray[itemIndex].responsibilities || [];
      const newBullets = [...currentBullets];
      newBullets.splice(bulletIndex, 1);
      newArray[itemIndex] = {
        ...newArray[itemIndex],
        bullets: newBullets,
        responsibilities: newBullets // Keep both in sync
      };
      return {
        ...prev,
        [section]: newArray
      };
    });
    setIsModified(true);
  };

  const handleBulletKeyDown = (e, section, itemIndex, bulletIndex, currentValue) => {
    // Handle backspace on empty bullet - delete the bullet point
    if (e.key === 'Backspace' && currentValue === '' && e.target.selectionStart === 0) {
      e.preventDefault();
      removeBullet(section, itemIndex, bulletIndex);

      // Focus on previous bullet if it exists
      if (bulletIndex > 0) {
        setTimeout(() => {
          const prevTextarea = e.target.parentElement.previousElementSibling?.querySelector('textarea');
          if (prevTextarea) {
            prevTextarea.focus();
            prevTextarea.setSelectionRange(prevTextarea.value.length, prevTextarea.value.length);
          }
        }, 0);
      }
    }
  };

  const handleSave = () => {
    onSave(editedResume);
    setIsModified(false);
  };

  return (
    <div className="space-y-6">
      {/* Header with Save/Cancel */}
      <div className="sticky top-0 z-10 bg-neutral-50 py-4 border-b border-neutral-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900">Edit Optimized Resume</h2>
            {isModified && (
              <p className="text-sm text-warning-600 mt-1">You have unsaved changes</p>
            )}
          </div>
          <div className="flex gap-3">
            {onCancel && (
              <Button variant="secondary" onClick={onCancel}>
                Cancel
              </Button>
            )}
            <Button
              variant="primary"
              onClick={handleSave}
              disabled={!isModified}
            >
              Save Changes
            </Button>
          </div>
        </div>
      </div>

      {/* Contact Information */}
      {editedResume.contact_info && (
        <Card>
          <h3 className="text-xl font-semibold text-neutral-900 mb-4">Contact Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Full Name</label>
              <input
                type="text"
                value={editedResume.contact_info.name || editedResume.contact_info.full_name || ''}
                onChange={(e) => handleChange('contact_info', 'name', e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="label">Email</label>
              <input
                type="email"
                value={editedResume.contact_info.email || ''}
                onChange={(e) => handleChange('contact_info', 'email', e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="label">Phone</label>
              <input
                type="text"
                value={editedResume.contact_info.phone || ''}
                onChange={(e) => handleChange('contact_info', 'phone', e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="label">Location</label>
              <input
                type="text"
                value={editedResume.contact_info.location || ''}
                onChange={(e) => handleChange('contact_info', 'location', e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="label">LinkedIn</label>
              <input
                type="text"
                value={editedResume.contact_info.linkedin || ''}
                onChange={(e) => handleChange('contact_info', 'linkedin', e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="label">GitHub</label>
              <input
                type="text"
                value={editedResume.contact_info.github || ''}
                onChange={(e) => handleChange('contact_info', 'github', e.target.value)}
                className="input"
              />
            </div>
          </div>
        </Card>
      )}

      {/* Professional Summary */}
      {editedResume.professional_summary && (
        <Card>
          <h3 className="text-xl font-semibold text-neutral-900 mb-4">Professional Summary</h3>
          <textarea
            value={editedResume.professional_summary}
            onChange={(e) => setEditedResume({ ...editedResume, professional_summary: e.target.value })}
            rows={4}
            className="input"
          />
        </Card>
      )}

      {/* Experience */}
      {editedResume.experience && editedResume.experience.length > 0 && (
        <Card>
          <h3 className="text-xl font-semibold text-neutral-900 mb-4">Professional Experience</h3>
          <div className="space-y-6">
            {editedResume.experience.map((exp, expIndex) => (
              <div key={expIndex} className="border-l-4 border-primary-200 pl-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                  <div>
                    <label className="label text-sm">Job Title</label>
                    <input
                      type="text"
                      value={exp.job_title || exp.title || ''}
                      onChange={(e) => handleArrayChange('experience', expIndex, 'title', e.target.value)}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label text-sm">Company</label>
                    <input
                      type="text"
                      value={exp.company || ''}
                      onChange={(e) => handleArrayChange('experience', expIndex, 'company', e.target.value)}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label text-sm">Location</label>
                    <input
                      type="text"
                      value={exp.location || ''}
                      onChange={(e) => handleArrayChange('experience', expIndex, 'location', e.target.value)}
                      className="input"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="label text-sm">Start Date</label>
                      <input
                        type="text"
                        value={exp.start_date || ''}
                        onChange={(e) => handleArrayChange('experience', expIndex, 'start_date', e.target.value)}
                        className="input"
                      />
                    </div>
                    <div>
                      <label className="label text-sm">End Date</label>
                      <input
                        type="text"
                        value={exp.end_date || ''}
                        onChange={(e) => handleArrayChange('experience', expIndex, 'end_date', e.target.value)}
                        className="input"
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-3">
                  <label className="label text-sm">Responsibilities</label>
                  <div className="space-y-2">
                    {(exp.bullets || exp.responsibilities || []).map((bullet, bulletIndex) => (
                      <div key={bulletIndex} className="flex gap-2">
                        <textarea
                          value={bullet}
                          onChange={(e) => handleBulletChange('experience', expIndex, bulletIndex, e.target.value)}
                          onKeyDown={(e) => handleBulletKeyDown(e, 'experience', expIndex, bulletIndex, bullet)}
                          rows={2}
                          className="input flex-1 text-sm"
                        />
                        <button
                          onClick={() => removeBullet('experience', expIndex, bulletIndex)}
                          className="text-error hover:text-error-dark"
                          title="Remove bullet"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={() => addBullet('experience', expIndex)}
                      className="text-sm text-primary hover:text-primary-dark flex items-center gap-1"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      Add Bullet
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Education */}
      {editedResume.education && editedResume.education.length > 0 && (
        <Card>
          <h3 className="text-xl font-semibold text-neutral-900 mb-4">Education</h3>
          <div className="space-y-4">
            {editedResume.education.map((edu, eduIndex) => (
              <div key={eduIndex} className="border-l-4 border-primary-200 pl-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="label text-sm">Degree</label>
                    <input
                      type="text"
                      value={edu.degree || ''}
                      onChange={(e) => handleArrayChange('education', eduIndex, 'degree', e.target.value)}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label text-sm">Field of Study</label>
                    <input
                      type="text"
                      value={edu.field_of_study || ''}
                      onChange={(e) => handleArrayChange('education', eduIndex, 'field_of_study', e.target.value)}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label text-sm">Institution</label>
                    <input
                      type="text"
                      value={edu.institution || ''}
                      onChange={(e) => handleArrayChange('education', eduIndex, 'institution', e.target.value)}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label text-sm">Location</label>
                    <input
                      type="text"
                      value={edu.location || ''}
                      onChange={(e) => handleArrayChange('education', eduIndex, 'location', e.target.value)}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label text-sm">Graduation Date</label>
                    <input
                      type="text"
                      value={edu.graduation_date || ''}
                      onChange={(e) => handleArrayChange('education', eduIndex, 'graduation_date', e.target.value)}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label text-sm">GPA</label>
                    <input
                      type="text"
                      value={edu.gpa || ''}
                      onChange={(e) => handleArrayChange('education', eduIndex, 'gpa', e.target.value)}
                      className="input"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Projects */}
      {editedResume.projects && editedResume.projects.length > 0 && (
        <Card>
          <h3 className="text-xl font-semibold text-neutral-900 mb-4">Projects</h3>
          <div className="space-y-6">
            {editedResume.projects.map((proj, projIndex) => (
              <div key={projIndex} className="border-l-4 border-primary-200 pl-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                  <div>
                    <label className="label text-sm">Project Title</label>
                    <input
                      type="text"
                      value={proj.title || proj.name || ''}
                      onChange={(e) => handleArrayChange('projects', projIndex, 'title', e.target.value)}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label text-sm">Link/URL</label>
                    <input
                      type="text"
                      value={proj.link || proj.url || ''}
                      onChange={(e) => handleArrayChange('projects', projIndex, 'link', e.target.value)}
                      className="input"
                    />
                  </div>
                </div>
                <div className="mb-3">
                  <label className="label text-sm">Description</label>
                  <textarea
                    value={proj.description || ''}
                    onChange={(e) => handleArrayChange('projects', projIndex, 'description', e.target.value)}
                    rows={3}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label text-sm">Technologies</label>
                  <input
                    type="text"
                    value={Array.isArray(proj.technologies) ? proj.technologies.join(', ') : (proj.technologies || '')}
                    onChange={(e) => handleArrayChange('projects', projIndex, 'technologies', e.target.value.split(',').map(t => t.trim()))}
                    className="input"
                    placeholder="Separate technologies with commas"
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Skills */}
      {editedResume.skills && editedResume.skills.length > 0 && (
        <Card>
          <h3 className="text-xl font-semibold text-neutral-900 mb-4">Skills</h3>
          <textarea
            value={Array.isArray(editedResume.skills) ? editedResume.skills.join(', ') : editedResume.skills}
            onChange={(e) => setEditedResume({ ...editedResume, skills: e.target.value.split(',').map(s => s.trim()).filter(s => s) })}
            rows={4}
            className="input"
            placeholder="Enter skills separated by commas"
          />
          <p className="text-sm text-neutral-500 mt-2">
            Separate skills with commas. Total: {Array.isArray(editedResume.skills) ? editedResume.skills.length : 0} skills
          </p>
        </Card>
      )}

      {/* Certifications */}
      {editedResume.certifications && editedResume.certifications.length > 0 && (
        <Card>
          <h3 className="text-xl font-semibold text-neutral-900 mb-4">Certifications</h3>
          <textarea
            value={Array.isArray(editedResume.certifications) ? editedResume.certifications.join(', ') : editedResume.certifications}
            onChange={(e) => setEditedResume({ ...editedResume, certifications: e.target.value.split(',').map(c => c.trim()).filter(c => c) })}
            rows={3}
            className="input"
            placeholder="Enter certifications separated by commas"
          />
          <p className="text-sm text-neutral-500 mt-2">
            Separate certifications with commas. Total: {Array.isArray(editedResume.certifications) ? editedResume.certifications.length : 0} certifications
          </p>
        </Card>
      )}

      {/* Sticky bottom buttons */}
      <div className="sticky bottom-0 bg-neutral-50 py-4 border-t border-neutral-200">
        <div className="flex gap-3 justify-end">
          {onCancel && (
            <Button variant="secondary" onClick={onCancel}>
              Cancel
            </Button>
          )}
          <Button
            variant="primary"
            onClick={handleSave}
            disabled={!isModified}
          >
            {isModified ? 'Save Changes' : 'No Changes'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ResumeEditor;
