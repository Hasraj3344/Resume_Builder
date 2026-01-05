# Resume Edit Integration Guide

## Overview
This guide shows how to integrate the resume editor into the Manual Workflow page so users can edit their parsed resume before running job match analysis.

## Changes Needed in ManualWorkflowPage.jsx

### 1. Add State Variables (after line 28)

```javascript
// Step 3: Optimized Resume
const [optimizedResume, setOptimizedResume] = useState(null);
const [showEditor, setShowEditor] = useState(false);

// ADD THESE NEW STATES:
const [showParsedEditor, setShowParsedEditor] = useState(false);
const [parsedResumeData, setParsedResumeData] = useState(null);
```

### 2. Add Handler to Save Edited Parsed Resume (after handleUploadResume function)

```javascript
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
```

### 3. Add "Edit Resume" Button in the UI (in Step 1 section, after resume upload display)

Find the section where it shows the uploaded resume (around line 250-300), and add this button:

```javascript
{/* Current Resume Display */}
{currentResume && (
  <Card>
    <div className="flex items-center justify-between mb-4">
      <div>
        <h3 className="font-semibold text-neutral-900">Current Resume</h3>
        <p className="text-sm text-neutral-600">{currentResume.filename}</p>
      </div>
      <div className="flex gap-2">
        {/* ADD THIS BUTTON: */}
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

        <label className="btn btn-secondary cursor-pointer">
          Upload New Resume
          <input type="file" className="hidden" {...resumeDropzone.getInputProps()} />
        </label>
      </div>
    </div>
  </Card>
)}
```

### 4. Add Parsed Resume Editor Modal (before the main content sections)

```javascript
{/* Parsed Resume Editor Modal */}
{showParsedEditor && parsedResumeData && (
  <div className="fixed inset-0 bg-black/50 z-50 overflow-y-auto">
    <div className="min-h-screen px-4 py-8">
      <div className="max-w-5xl mx-auto bg-white rounded-lg shadow-xl">
        <div className="sticky top-0 bg-white border-b border-neutral-200 px-6 py-4 rounded-t-lg z-10">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-neutral-900">Edit Parsed Resume</h2>
            <button
              onClick={() => setShowParsedEditor(false)}
              className="text-neutral-500 hover:text-neutral-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="text-sm text-neutral-600 mt-1">
            Make changes to your resume before running job match analysis
          </p>
        </div>

        <div className="px-6 py-4 max-h-[80vh] overflow-y-auto">
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
```

## Testing the Implementation

1. **Upload a resume** in the Manual Workflow page
2. **Click "Edit Resume"** button that appears after upload
3. **Edit any fields** (contact info, skills, experience, education, projects, certifications)
4. **Click "Save Changes"**
5. **Verify** the changes are persisted by clicking Edit again
6. **Proceed** to paste job description and run analysis with edited resume

## API Endpoints Used

- `POST /api/resume/upload` - Uploads and parses resume (existing)
- `PUT /api/resume/edit` - Saves edited parsed resume data (new)

## Benefits

✅ Users can **fix parsing errors** before analysis
✅ Users can **add missing skills** manually
✅ Users can **correct education/experience** data
✅ Users can **update contact links** (LinkedIn, GitHub)
✅ **Hyperlinks extracted** from PDF/DOCX are preserved
✅ Changes are **saved to database** for future use

## Notes

- The editor shows **parsed resume data** (before optimization)
- This is different from editing the **optimized resume** (after AI generation)
- Both editing workflows can coexist in the application
