import os
import logging
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# File to store conversation history
CONVERSATION_FILE = 'conversation_history.txt'

def clear_conversation_history():
    """Clear the conversation history file."""
    try:
        with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
            f.write("")
        logger.info("Conversation history cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")

def load_gemini_client():
    """Initialize and return a Gemini model client."""
    try:
        # Get API key from environment
        api_key = os.getenv("NEXT_PUBLIC_GEMINI_API_KEY")
        
        if not api_key:
            logger.error("Gemini API key not found in environment variables")
            raise ValueError("Gemini API key not found in environment variables")
        
        # Log that we found the key (without showing the actual key)
        logger.info(f"Found Gemini API key: {api_key[:4]}...{api_key[-4:]}")
        
        # Configure the Google Generative AI library
        genai.configure(api_key=api_key)
        
        # Create and return the model instance
        model = genai.GenerativeModel("gemini-2.0-flash")
        logger.info("Gemini model initialized successfully")
        
        # Test the model with a simple prompt
        test_response = model.generate_content("Say 'Hello, I am functioning correctly' if you can read this.")
        logger.info(f"Test response: {test_response.text}")
        
        return model
    
    except Exception as e:
        logger.error(f"Error initializing Gemini client: {e}")
        raise

def save_to_memory(user_input, bot_response):
    """Save the conversation exchange to the history file."""
    try:
        with open(CONVERSATION_FILE, 'a', encoding='utf-8') as f:
            f.write(f"User: {user_input}\n")
            f.write(f"Bot: {bot_response}\n")
        logger.info("Conversation saved to memory")
    except Exception as e:
        logger.error(f"Error saving conversation to memory: {e}")

def load_conversation_history():
    """Load and return the conversation history from the file."""
    try:
        if not os.path.exists(CONVERSATION_FILE):
            logger.info("Conversation history file does not exist, creating new file")
            with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
                pass
            return ""
            
        with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
            history = f.read()
        logger.info(f"Loaded conversation history: {len(history)} characters")
        return history
    except Exception as e:
        logger.error(f"Error loading conversation history: {e}")
        return ""

def chat_with_gemini(prompt, model):
    """Generate a response to the user's prompt using the Gemini model."""
    try:
        logger.info(f"Received prompt: {prompt[:50]}...")
        
        # Load conversation history
        conversation_history = load_conversation_history()
        logger.info("Loaded conversation history")
        
        # Create safety settings
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Prepare the full prompt with conversation history context
        full_prompt = f"""
        Previous conversation:
        {conversation_history}
        
        User's new question: {prompt}
        
        Please provide a helpful, accurate, and concise response to the user's question.
        """
        
        # Generate the response
        logger.info("Generating response with Gemini...")
        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
        
        # Extract the text response
        response_text = response.text
        logger.info(f"Generated response: {response_text[:50]}...")
        
        # Save the conversation
        save_to_memory(prompt, response_text)
        
        return response_text
        
    except Exception as e:
        logger.error(f"Error in chat_with_gemini: {str(e)}")
        return f"I'm sorry, I encountered an error: {str(e)}"
