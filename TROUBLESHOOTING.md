# Troubleshooting Guide

## Authentication Errors

If you see errors like:
```
ERROR:root:Failed to get response from model: 401 Client Error: Unauthorized
Invalid credentials in Authorization header
```

This likely means:

1. **API Key Issue**: 
   - Check that you've added your Gemini API key to the `.env` file
   - Make sure the environment variable is named `NEXT_PUBLIC_GEMINI_API_KEY`
   - Verify that your API key is valid and not expired
   - Try running `python test_gemini.py` to test your API key directly

2. **Wrong API Being Used**:
   - The error refers to Hugging Face, but we're using Gemini
   - This suggests the code might still be trying to use the old API
   - Try deleting `__pycache__` directories if they exist:
     ```
     rm -rf __pycache__
     ```
   - Restart your server completely

## Testing The Integration

1. Run the standalone test script:
   ```bash
   python test_gemini.py
   ```
   This will verify if your Gemini API key is working correctly.

2. Test the API server health:
   ```bash
   curl http://localhost:5000/health
   ```
   Should return: `{"service":"chatbot","status":"ok"}`

3. Test a chat request:
   ```bash
   curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"prompt":"Hello, how are you?", "activeVideoUrl":"https://example.com/video"}' \
     http://localhost:5000/chat
   ```

## Checking Logs

If you're still having issues, check the log files:

1. `debug.log` - Contains logs from the chatbot module
2. `api.log` - Contains logs from the Flask API server

These logs will show more detailed error information that can help diagnose problems.

## Common Issues

1. **ModuleNotFoundError**: Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **Gemini API errors**:
   - Ensure you have billing enabled on your Google Cloud account
   - Check if you've reached your API quota limits
   - Verify your API key has access to the Gemini models

3. **Missing Environment Variables**:
   - Make sure your `.env` file is in the correct location (in the backend directory)
   - Verify it has the correct format:
     ```
     NEXT_PUBLIC_GEMINI_API_KEY=your_api_key_here
     ```

4. **Flask server issues**:
   - Check if another process is using port 5000
   - Try running on a different port:
     ```bash
     flask run --port=5001
     ```

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Sign in with your Google account
3. Navigate to "Get API key" or "API Keys" section
4. Create a new API key or use an existing one
5. Copy the key to your `.env` file

## Still Having Issues?

- Check if the Google Generative AI API is experiencing any outages
- Try with a different API key if possible
- Review the Python package versions in `requirements.txt` and update if needed 