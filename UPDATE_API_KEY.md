# API Key Setup Instructions

## Your API key is currently invalid/expired

To fix this:

### Option 1: OpenAI (Recommended)
1. Visit: https://platform.openai.com/api-keys
2. Create a new API key (you may need to add billing)
3. Copy the key (starts with `sk-proj-...`)
4. Update line 2 in `.env`:
   ```
   OPENAI_API_KEY=sk-proj-YOUR_NEW_KEY_HERE
   ```

### Option 2: Anthropic Claude
1. Visit: https://console.anthropic.com/settings/keys
2. Create a new API key
3. Copy the key (starts with `sk-ant-...`)
4. Update line 3 in `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-YOUR_NEW_KEY_HERE
   ```

### After updating:

**Test your setup:**
```bash
python test_api_key.py
```

**Run the full workflow:**
```bash
python main.py --rag --generate
```

**Or use the Streamlit app:**
```bash
streamlit run app.py
```

---

## Cost Estimates (OpenAI GPT-3.5-turbo)
- Resume parsing: FREE (local)
- Resume optimization: ~$0.01 per resume
- Chat interactions: ~$0.001 per message

## Cost Estimates (GPT-4)
- Resume optimization: ~$0.10 per resume
- Chat interactions: ~$0.01 per message

The app is currently set to use `gpt-4-turbo-preview`. To use the cheaper GPT-3.5:
- Change line 7 in `.env` to: `LLM_MODEL=gpt-3.5-turbo`
