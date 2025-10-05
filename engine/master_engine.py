import pandas as pd
import numpy as np

# Import your other engine components
from engine.scraper import scrape_nslsl
from engine.processing import summarize_text, extract_keywords

def run_master_pipeline(search_text: str, live_scrape: bool = False):
    """
    Orchestrates the backend logic.
    - If live_scrape is True, it runs the scraper and then the NLP models.
    - Otherwise, it would use an internal database (simulated here).
    """
    print(f"Engine: Master pipeline triggered. Live Scrape: {live_scrape}")

    if live_scrape:
        # --- SCRAPE & PROCESS WORKFLOW ---
        if not search_text:
            raise ValueError("A search keyword is required for live scraping.")
        
        # 1. Run the slow scraping task
        source_text = scrape_nslsl(search_text)
        if "failed" in source_text or "No results" in source_text:
             return {'title': 'Scraping Issue', 'summary': source_text, 'experiments': [], 'graph_elements': []}

        # 2. Feed the scraped text into your NLP models
        summary = summarize_text(source_text)
        keywords = extract_keywords(source_text)

        # 3. Format the results for the frontend
        return {
            'title': f"Live Web Analysis for: '{search_text}'",
            'summary': summary,
            'experiments': pd.DataFrame({'Keywords': keywords, 'Relevance': np.random.rand(len(keywords))}).to_dict('records'),
            'graph_elements': [{'data': {'id': kw, 'label': kw}} for kw in keywords]
        }
    else:
        # --- INTERNAL KNOWLEDGE BASE WORKFLOW (SIMULATED) ---
        summary = f"This is a summary from our internal knowledge base about '{search_text}'."
        keywords = ["Internal", "Database", "Result"]
        
        return {
            'title': f"Knowledge Base Analysis for: '{search_text}'",
            'summary': summary,
            'experiments': pd.DataFrame({'Source': keywords, 'Count': [10, 8, 5]}).to_dict('records'),
            'graph_elements': [{'data': {'id': kw, 'label': kw}} for kw in keywords]
        }
