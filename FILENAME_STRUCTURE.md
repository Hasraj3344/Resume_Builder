# Output Filename Structure

All output files now use the original resume filename as a base, making it easy to track which files belong together.

## Filename Format

**Pattern:** `{original_filename}_{suffix}.{extension}`

Where:
- `{original_filename}` = Your resume filename (without extension)
- `{suffix}` = Type of output
- `{extension}` = File type (json, docx)

---

## Examples

### For resume: `John_Doe_Resume.pdf`

**Command Line (main.py):**
```
output/John_Doe_Resume.json                              # Parsed resume
output/John_Doe_Resume_job_description.json              # Job description
output/John_Doe_Resume_optimized_resume.json             # Optimized resume
```

**Streamlit App (app.py):**
```
output/John_Doe_Resume.docx                              # Original resume (DOCX)
output/John_Doe_Resume_optimized_resume.docx             # Optimized resume
output/John_Doe_Resume_data.json                         # Resume data (JSON)
output/John_Doe_Resume_cover_letter_professional.docx    # Cover letter (Professional style)
output/John_Doe_Resume_cover_letter_enthusiastic.docx    # Cover letter (Enthusiastic style)
output/John_Doe_Resume_cover_letter_concise.docx         # Cover letter (Concise style)
output/John_Doe_Resume_combined_application.docx         # Resume + Cover letter
```

### For resume: `Yashaswini Ramasahayam (1).docx`

**Command Line:**
```
output/Yashaswini Ramasahayam (1).json
output/Yashaswini Ramasahayam (1)_job_description.json
output/Yashaswini Ramasahayam (1)_optimized_resume.json
```

**Streamlit App:**
```
output/Yashaswini Ramasahayam (1).docx
output/Yashaswini Ramasahayam (1)_optimized_resume.docx
output/Yashaswini Ramasahayam (1)_cover_letter_professional.docx
output/Yashaswini Ramasahayam (1)_combined_application.docx
```

---

## Benefits

1. ✅ **Easy Identification** - Know which files belong to which resume
2. ✅ **No Overwriting** - Multiple resumes can be processed without conflicts
3. ✅ **Professional** - Clean, organized output structure
4. ✅ **Tracking** - Match optimized versions back to originals
5. ✅ **Automation** - Batch process multiple resumes easily

---

## File Suffixes

| Suffix | Description |
|--------|-------------|
| _(none)_ | Original/parsed resume |
| `_optimized_resume` | LLM-optimized version |
| `_job_description` | Parsed job description |
| `_data` | Resume data in JSON format |
| `_cover_letter_professional` | Professional cover letter |
| `_cover_letter_enthusiastic` | Enthusiastic cover letter |
| `_cover_letter_concise` | Concise cover letter |
| `_combined_application` | Resume + cover letter combined |

---

## Fallback Behavior

If the original filename cannot be determined (edge cases), the system falls back to:
- `resume.json`
- `resume_optimized_resume.json`
- etc.

This ensures the system always produces output even in unusual scenarios.

---

## Implementation Details

**Command Line (main.py):**
- Filename stored in: `optimizer.resume_filename`
- Set during: `load_resume()` method
- Used in: `export_json()` method

**Streamlit App (app.py):**
- Filename stored in: `st.session_state.resume_filename`
- Set during: File upload in `step1_upload()`
- Used in: Export section in `step5_export()`

---

## Code Changes

### main.py
```python
# Store filename on load
self.resume_filename = Path(file_path).stem

# Use in export
base_name = self.resume_filename if self.resume_filename else "resume"
resume_json = output_path / f"{base_name}.json"
opt_resume_json = output_path / f"{base_name}_optimized_resume.json"
```

### app.py
```python
# Store filename on upload
st.session_state.resume_filename = Path(uploaded_file.name).stem

# Use in export
base_name = st.session_state.resume_filename if st.session_state.resume_filename else "resume"
filename = f"{base_name}_optimized_resume.docx"
```

---

**Updated:** December 2024
