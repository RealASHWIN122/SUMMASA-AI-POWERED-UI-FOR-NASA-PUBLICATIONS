# engine/processing.py

import fitz # PyMuPDF
import os
from transformers import pipeline
from keybert import KeyBERT

def extract_text_from_pdfs(pdf_folder_path):
    """Extracts text from all PDFs in a given folder."""
    # ... (code from previous answer) ...
    full_text = ""
    for filename in os.listdir(pdf_folder_path):
        if filename.endswith(".pdf"):
            with fitz.open(os.path.join(pdf_folder_path, filename)) as doc:
                for page in doc:
                    full_text += page.get_text()
    return full_text

def summarize_text(text):
    """Generates a summary of the text."""
    # ... (code from previous answer) ...
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text[:4096], max_length=250, min_length=100, do_sample=False)
    return summary[0]['summary_text']

def extract_keywords(text):
    """Extracts keywords and keyphrases from the text."""
    # ... (code from previous answer) ...
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=15)
    return [kw[0] for kw in keywords]

# --- Master Function ---
def run_nlp_pipeline(pdf_folder_path):
    """
    Runs the full text processing pipeline.
    This is the main function the app will call.
    """
    print("Step 1: Extracting text from PDFs...")
    full_text = extract_text_from_pdfs(pdf_folder_path)
    
    print("Step 2: Summarizing text...")
    summary = summarize_text(full_text)
    
    print("Step 3: Extracting keywords...")
    keywords = extract_keywords(full_text)
    
    return summary, keywords, full_text