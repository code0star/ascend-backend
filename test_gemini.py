"""
Simple test script to verify the Gemini API is working correctly.
Run this script with: python test_gemini.py
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test the Gemini API connection."""
    print("Testing Gemini API connection...")
    
    # Get the API key
    api_key = os.getenv("NEXT_PUBLIC_GEMINI_API_KEY")
    if not api_key:
        print("ERROR: No API key found in .env file")
        print("Please create a .env file with your Gemini API key:")
        print("NEXT_PUBLIC_GEMINI_API_KEY=your_api_key_here")
        return False
    
    # Mask the API key for security (show only first and last 4 characters)
    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
    print(f"Found API key: {masked_key}")
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        print("API configured successfully")
        
        # Create a model instance
        model = genai.GenerativeModel("gemini-2.0-flash")
        print("Model created successfully")
        
        # Test with a simple prompt
        print("Sending test prompt to Gemini...")
        response = model.generate_content("Say 'Hello, I am Gemini!' if you can read this.")
        
        # Print the response
        print("\nResponse from Gemini:")
        print(f"{response.text}")
        
        print("\nTest completed successfully! Gemini API is working correctly.")
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to connect to Gemini API: {str(e)}")
        print("\nPlease check your API key and internet connection.")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    if not success:
        print("\nThe test failed. Please fix the issues before running the server.")
    else:
        print("\nYou're all set! You can now run the chatbot server with 'python app.py'") 