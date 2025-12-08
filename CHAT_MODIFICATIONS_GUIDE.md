# Chat Modifications Guide

This guide shows all the supported natural language modifications you can make to your resume through the chat interface.

## ✅ Supported Modifications

### 1. **GitHub Link**

All these formats work:
```
✓ my github link is github.com/hasraj
✓ set my github to https://github.com/hasraj
✓ github is hasraj
✓ update github to github.com/hasraj
```

**Result:** Sets GitHub to `https://github.com/hasraj`

---

### 2. **LinkedIn Link**

All these formats work:
```
✓ my linkedin is linkedin.com/in/hasraj
✓ set my linkedin to https://linkedin.com/in/hasraj
✓ linkedin link is hasraj
✓ update linkedin to linkedin.com/in/hasraj
```

**Result:** Sets LinkedIn to `https://linkedin.com/in/hasraj`

---

### 3. **Email**

```
✓ change my email to john@example.com
✓ update my email to john.doe@company.com
✓ my email is john@example.com
✓ set my email to john@example.com
```

**Result:** Updates email address

---

### 4. **Phone Number**

```
✓ change my phone to +1-234-567-8900
✓ update phone to (123) 456-7890
✓ my phone is +1 234 567 8900
✓ set phone to 123-456-7890
```

**Result:** Updates phone number

---

### 5. **Years of Experience**

```
✓ change my years of experience from 3 to 5
✓ update years of experience to 5
✓ set my years to 5
```

**Result:** Updates summary from "3+ years" to "5+ years"

---

### 6. **Name**

```
✓ change my name to John Smith
✓ update name to Jane Doe
✓ set my name to Robert Johnson
```

**Result:** Updates full name

---

### 7. **Location**

```
✓ change my location to New York, NY
✓ update location to San Francisco, CA
✓ my location is Seattle, WA
```

**Result:** Updates location

---

### 8. **Add Skills**

```
✓ add skill: Docker
✓ add skill: Kubernetes
✓ include skill: React
✓ add Docker
```

**Result:** Adds skill to skills list

---

## 🎯 Usage Tips

1. **Be specific**: The more specific you are, the better the detection works
2. **Use natural language**: All common phrasings work (change, update, set, add, etc.)
3. **Links are auto-formatted**: Even if you just provide the username, full URLs are constructed
4. **Multiple modifications**: Make changes one at a time for best results

## 📋 Examples in Context

### Complete Chat Session Example:

```
You: my github link is github.com/johndoe
AI: ✓ GitHub updated to: https://github.com/johndoe

You: linkedin link is johndoe
AI: ✓ LinkedIn updated to: https://linkedin.com/in/johndoe

You: change my years of experience from 3 to 5
AI: ✓ Years of experience updated to: 5+ years

You: add skill: Docker
AI: ✓ Added skill: Docker

You: update my email to john.doe@company.com
AI: ✓ Email updated to: john.doe@company.com
```

---

## 🔍 Regular Questions Still Work

You can still ask questions about your resume:
```
✓ What experience do I have with Python?
✓ What are my top skills?
✓ Do I have cloud experience?
```

These will be answered by the AI assistant without modifying your resume.

---

## ⚡ Quick Reference

| Field | Example Command | Result |
|-------|----------------|--------|
| GitHub | `github is username` | `https://github.com/username` |
| LinkedIn | `linkedin is username` | `https://linkedin.com/in/username` |
| Email | `email is john@example.com` | `john@example.com` |
| Phone | `phone is +1-234-567-8900` | `+1-234-567-8900` |
| Years | `change years from 3 to 5` | Updates summary |
| Name | `name is John Doe` | `John Doe` |
| Location | `location is New York, NY` | `New York, NY` |
| Skills | `add skill: Docker` | Adds to skills list |

---

## 🚀 Ready to Use!

The modification handler is now fully integrated into the Streamlit app.

Run the app with:
```bash
streamlit run app.py
```

Go to **Step 3: Interactive Chat** and start making changes!
