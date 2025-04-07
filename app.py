from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import traceback
from chatbot import chat_with_gemini, load_gemini_client, clear_conversation_history
from youtube_transcript_api import YouTubeTranscriptApi


# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", origins=["https://your-frontend.vercel.app"], supports_credentials=True) 

# Files for storing URL and conversation history
LAST_VIDEO_URL_FILE = 'last_video_url.txt'
CONVERSATION_FILE = 'conversation_history.txt'

# Initialize Gemini model
try:
    logger.info("Initializing Gemini model...")
    model = load_gemini_client()
    logger.info("Gemini model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {str(e)}")
    logger.error(traceback.format_exc())
    # We'll continue running the app, but API calls will fail

def load_last_video_url():
    try:
        if os.path.exists(LAST_VIDEO_URL_FILE):
            with open(LAST_VIDEO_URL_FILE, 'r') as f:
                return f.read().strip()
        return None
    except Exception as e:
        logger.error(f"Error loading last video URL: {str(e)}")
        return None

def save_last_video_url(url):
    try:
        with open(LAST_VIDEO_URL_FILE, 'w') as f:
            f.write(url)
        logger.info(f"Saved new video URL: {url[:20]}...")
    except Exception as e:
        logger.error(f"Error saving video URL: {str(e)}")

def clear_history():
    open(CONVERSATION_FILE, 'w').close()  # Clears the conversation history file

def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        result = "\n".join([entry['text'] for entry in transcript])
        return {"transcript": result}
    except Exception as e:
        logger.error(f"Transcript error: {str(e)}")
        return {"error": str(e)}

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Log that we received a request
        logger.info("Received chat request")
        
        # Validate content type
        if request.content_type != 'application/json':
            logger.warning("Invalid content type")
            return jsonify({"error": "Content-Type must be application/json"}), 400

        # Parse request data
        data = request.get_json(force=True)
        logger.info(f"Request data: {data}")

        # Validate request data
        if not data or 'prompt' not in data:
            logger.warning("Missing prompt in request")
            return jsonify({"error": "Prompt not provided"}), 400

        # Extract prompt and video URL
        prompt = data['prompt']
        active_video_url = data.get('activeVideoUrl')

        # Log what we received
        logger.info(f"Prompt: {prompt[:50]}...")
        logger.info(f"Active Video URL: {active_video_url[:50] if active_video_url else 'None'}")

        # Check if URL has changed
        last_url = load_last_video_url()
        if active_video_url and (active_video_url != last_url):
            logger.info("Video URL changed, clearing conversation history")
            clear_history()
            save_last_video_url(active_video_url)
        
        # Process the prompt and get a response
        logger.info("Calling Gemini to generate response")
        response_text = chat_with_gemini(prompt, model)
        logger.info(f"Response generated: {response_text[:50]}...")
        
        # Return the response
        return jsonify({"response": response_text})
    
    except Exception as e:
        # Log the full exception
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return an error response
        return jsonify({
            "error": f"Server error: {str(e)}",
            "message": "Please check server logs for details"
        }), 500
    
@app.route('/ping', methods=['GET'])
def ping():
    return "Flask server is alive!", 200

@app.route('/transcribe', methods=['GET'])
def transcribe():
    video_id = request.args.get('videoId')
    if not video_id:
        return jsonify({"error": "Missing videoId"}), 400

    logger.info(f"Transcribing video ID: {video_id}")
    transcript_result = fetch_transcript(video_id)
    
    if "error" in transcript_result:
        return jsonify(transcript_result), 500

    return jsonify(transcript_result)

if __name__ == '__main__':
    logger.info("Starting Flask server on port 5000...")
    app.run(host='0.0.0.0', port=5000)
