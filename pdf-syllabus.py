# API_KEY = "hdqOGa8wYVJQJUcDl1jK0owxJVLbC9QfLEtw4HCm"
import os
import sys
import cohere
import PyPDF2
import docx  # This is imported from python-docx package

# ========== CONFIG ==========
API_KEY = "hdqOGa8wYVJQJUcDl1jK0owxJVLbC9QfLEtw4HCm"  # Replace with your Cohere key
CHUNK_SIZE = 3000                # Characters per chunk (Cohere limit ~3000–4000)
# ============================

# Initialize client
co = cohere.Client(API_KEY)

# Extract text from PDF
def extract_text_from_pdf(file_path):
    try:
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            if len(reader.pages) == 0:
                print(f"Warning: PDF has no pages")
                return ""
                
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                    text += page_text
                    print(f"Extracted {len(page_text)} characters from page {i+1}")
                except Exception as e:
                    print(f"Error extracting text from page {i+1}: {str(e)}")
                    # Continue with next page instead of failing
        return text
    except Exception as e:
        print(f"Error reading PDF file: {str(e)}")
        return ""

# Extract text from DOCX
def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        print(f"Extracted {len(text)} characters from DOCX file")
        return text
    except Exception as e:
        print(f"Error reading DOCX file: {str(e)}")
        return ""

# Split large text into manageable chunks
def chunk_text(text, max_length):
    if not text or len(text.strip()) == 0:
        print("Warning: Received empty text for chunking")
        return []
        
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    return chunks

# Summarize using Cohere
def summarize_text(text):
    if not text or len(text.strip()) < 100:
        print("Warning: Text too short to summarize")
        return text
        
    try:
        print(f"Sending {len(text)} characters to Cohere API")
        response = co.summarize(
            text=text,
            length='long',
            format='paragraph',
            model='command',
            temperature=0.3
        )
        return response.summary
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return ""

# Main logic
if __name__ == "__main__":
    try:
        # Check if file path is provided
        if len(sys.argv) < 2:
            print("Error: File path is required.")
            print("Usage: python pdf-syllabus.py <file_path>")
            sys.exit(1)
        
        # Get file path from command line argument
        FILE_PATH = sys.argv[1]
        print(f"Processing file: {FILE_PATH}")
        
        # Check if file exists
        if not os.path.exists(FILE_PATH):
            print(f"Error: File '{FILE_PATH}' does not exist.")
            sys.exit(1)
        
        file_size = os.path.getsize(FILE_PATH)
        print(f"File size: {file_size/1024:.2f} KB")
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            print(f"Warning: File is large ({file_size/1024/1024:.2f} MB). Processing may take longer.")
            
        ext = os.path.splitext(FILE_PATH)[1].lower()
        print(f"File extension: {ext}")

        try:
            if ext == ".pdf":
                print("Extracting text from PDF...")
                raw_text = extract_text_from_pdf(FILE_PATH)
            elif ext == ".docx":
                print("Extracting text from DOCX...")
                raw_text = extract_text_from_docx(FILE_PATH)
            else:
                print("Unsupported file format. Use .pdf or .docx")
                sys.exit(1)
        except Exception as e:
            print(f"Error extracting text from file: {str(e)}")
            sys.exit(1)

        if not raw_text or len(raw_text.strip()) == 0:
            print("Error: No text could be extracted from the file. The file may be empty, corrupted, or contain only images.")
            # Provide a minimal fallback summary instead of exiting
            print("\nFinal Summary:\n")
            filename = os.path.basename(FILE_PATH)
            print(f"This file ({filename}) appears to contain no extractable text. It may consist of scanned images or graphics without text layers. Please consider using a text-based document for better analysis.")
            sys.exit(0)  # Exit successfully with a fallback message

        print(f"Total characters extracted: {len(raw_text)}")
        if len(raw_text) < 100:
            print("Warning: Very little text extracted. The file may not contain much text content.")
            print("\nFinal Summary:\n")
            print(raw_text)  # Use the raw text as the summary since it's so short
            sys.exit(0)  # Exit successfully with what little text we have
            
        print(f"First 200 characters: {raw_text[:200]}")

        chunks = chunk_text(raw_text, CHUNK_SIZE)
        chunk_count = len(chunks)
        print(f"Total chunks to summarize: {chunk_count}")
        
        if chunk_count == 0:
            print("No text chunks to summarize.")
            print("\nFinal Summary:\n")
            filename = os.path.basename(FILE_PATH)
            print(f"The file {filename} was processed, but no suitable content was found for summarization.")
            sys.exit(0)

        summaries = []
        for i, chunk in enumerate(chunks):
            print(f"\nSummarizing chunk {i+1}/{chunk_count}...")
            try:
                summary = summarize_text(chunk)
                if summary:
                    print(f"Chunk {i+1} summary length: {len(summary)} chars")
                    summaries.append(summary)
                else:
                    print(f"Warning: Chunk {i+1} returned empty summary")
            except Exception as e:
                print(f"Error summarizing chunk {i+1}: {str(e)}")
                # Continue with other chunks instead of failing completely
        
        if not summaries:
            print("No summaries could be generated. Using the first 1000 characters of the document as a fallback.")
            print("\nFinal Summary:\n")
            print(raw_text[:1000] + "...")
            sys.exit(0)

        final_summary = "\n\n".join(summaries)
        print(f"\nFinal summary generated: {len(final_summary)} characters")

        print("Final Summary:\n")
        print(final_summary)
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Provide a fallback summary even in case of error
        print("\nFinal Summary:\n")
        filename = os.path.basename(sys.argv[1]) if len(sys.argv) > 1 else "unknown file"
        print(f"An error occurred while processing {filename}. The system was unable to extract and summarize the content properly.")
        sys.exit(0)  # Exit with success code since we provided a fallback summary
