# Gemini-powered Chatbot

This chatbot uses Google's Gemini API to provide context-aware responses based on user prompts and conversation history.

## Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a .env file** with your Gemini API key:
   ```
   NEXT_PUBLIC_GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Run the Flask server**:
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5000`.

## API Usage

Make POST requests to the `/chat` endpoint with a JSON body:

```json
{
  "prompt": "Your question here",
  "activeVideoUrl": "https://www.youtube.com/watch?v=video_id"
}
```

The response will be in JSON format:

```json
{
  "response": "The chatbot's response here"
}
```

## Features

- **Context-aware**: The chatbot maintains conversation history to provide contextual responses.
- **Video context**: When a different video URL is provided, the conversation history is cleared to focus on the new content.
- **Conversation summarization**: For long conversations, the history is automatically summarized to maintain relevance.

## File Structure

- `app.py`: Flask server that handles API requests
- `chatbot.py`: Core chatbot functionality using Gemini API
- `requirements.txt`: Required Python dependencies
- `conversation_history.txt`: Stores the conversation history
- `last_video_url.txt`: Tracks the currently active video URL 