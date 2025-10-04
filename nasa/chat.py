import streamlit as st
import tempfile
import os
from google import genai
from google.genai import types

# =========================================================================
# === WARNING: HARDCODED KEY SECTION - REPLACE WITH YOUR KEY ===
# =========================================================================
# WARNING: DO NOT share this file publicly after pasting your key.
HARDCODED_API_KEY = "AIzaSyA2f64amvhSBD26sDYgzJv6bgTQqlB_hNA"
# =========================================================================
# =========================================================================

# --- Constants ---
MODEL_NAME = 'gemini-2.5-flash'

# --- Initialization & Key Handling ---

st.set_page_config(
    page_title="Gemini AI PDF Summarizer (Hardcoded Key)",
    layout="wide"
)

st.title("📚 PDF Summarizer powered by Gemini")
st.caption("Key loaded directly from script for rapid testing.")

# Check for hardcoded key
if HARDCODED_API_KEY == "YOUR_HARDCODED_GEMINI_API_KEY_HERE":
    st.error("Error: Please replace 'YOUR_HARDCODED_GEMINI_API_KEY_HERE' in the script with your actual API key.")
    st.stop()

# Initialize the Gemini Client using the hardcoded key
try:
    client = genai.Client(api_key=HARDCODED_API_KEY)
except Exception as e:
    st.error(f"Error initializing Gemini Client. Check your API key: {e}")
    st.stop()


# Function to generate the summary from a file
# Note: Caching is not used here due to file upload/delete operations
def get_pdf_summary(uploaded_file, summary_length, current_client):
    """Uploads a PDF file, generates a summary, and cleans up the file."""
    uploaded_file_part = None
    
    # 1. Save the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_file_path = tmp_file.name

    try:
        # 2. Upload the file to the Gemini File API (Mime type in config)
        uploaded_file_part = current_client.files.upload(
            file=temp_file_path, 
            config={'mime_type': 'application/pdf'}
        )
        
        system_instruction = (
            "You are an expert document summarization specialist. Your task is to provide a concise, "
            "accurate summary of the provided PDF document. Focus on key findings, main arguments, "
            "and conclusions. Do not add conversational remarks."
        )
        
        prompt = f"Summarize the uploaded PDF document in a {summary_length} format."
        
        # 3. Generate content by passing both the file and the text prompt
        response = current_client.models.generate_content(
            model=MODEL_NAME,
            contents=[uploaded_file_part, prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2 
            )
        )
        summary = response.text
        
    except Exception as e:
        summary = f"An error occurred during API call: {e}"
        
    finally:
        # 4. Clean up: Delete the temporary file and the file uploaded to the API
        os.unlink(temp_file_path)
        if uploaded_file_part:
            try:
                # Delete the file from the service
                current_client.files.delete(name=uploaded_file_part.name)
            except Exception as e:
                # This is a cleanup task, print the error but don't stop the app
                print(f"File cleanup failed: {e}") 
            
    return summary

# --- Main App Logic ---

st.sidebar.header("Summary Formatting")
summary_length = st.sidebar.selectbox(
    "Choose Summary Length:",
    ["executive summary (200 words)", "3 concise bullet points", "one short paragraph", "detailed report (500 words)"],
    index=0
)

# File uploader widget
uploaded_file = st.file_uploader(
    "Upload a PDF File:",
    type=["pdf"],
    accept_multiple_files=False
)

# Summarize button
if st.button("Generate Summary", use_container_width=True):
    if uploaded_file is not None:
        
        st.subheader(f"Summary ({summary_length}) for: {uploaded_file.name}")
        
        with st.spinner("Gemini is analyzing and summarizing your PDF..."):
            # Pass the uploaded file object and client to the function
            summary = get_pdf_summary(uploaded_file, summary_length, client)
        
        # Display the result
        st.info(summary)
        
    else:
        st.warning("Please upload a PDF file to begin summarization.")