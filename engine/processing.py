# engine/processing.py

import fitz # PyMuPDF
import os
from transformers import pipeline
from keybert import KeyBERT

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def scrape_nslsl(keyword, max_pages=3):
    """
    Scrape NSLSL (NASA Scientific and Technical Publications) for a given keyword.

    Args:
        keyword (str): The search term.
        max_pages (int): Maximum number of pages to scrape.

    Returns:
        str: Combined text with Title, Abstract, and URL for each publication.
    """
    # Setup Selenium
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)
    combined_text = ""

    def get_abstract():
        selectors = [
            "span#abstract-1",
            "div#abstract p",
            "div.abstract",
            "p[id$='lblAbstract']"
        ]
        for sel in selectors:
            try:
                elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                )
                text = elem.text.strip()
                if text:
                    return text
            except TimeoutException:
                continue
        return "No abstract available"

    try:
        base_url = "https://extapps.ksc.nasa.gov"
        search_url = f"{base_url}/NSLSL/Search"
        driver.get(search_url)
        time.sleep(3)

        # Enter search keyword
        search_box = wait.until(EC.presence_of_element_located((By.ID, "searchCriteria")))
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        page_count = 0
        while True:
            results = driver.find_elements(By.CSS_SELECTOR, "a.pubDetail")
            if not results:
                break

            for res in results:
                title = res.text.strip()
                relative_link = res.get_attribute("href")
                link = relative_link if relative_link.startswith("http") else base_url + relative_link

                # Open link in new tab to get abstract
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)
                time.sleep(2)

                abstract = get_abstract()

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                combined_text += f"Title: {title}\nAbstract: {abstract}\nURL: {link}\n\n"

            page_count += 1
            if page_count >= max_pages:
                break

            # Click Next button
            try:
                next_btn = driver.find_element(By.LINK_TEXT, "Next")
                if "disabled" in next_btn.get_attribute("class"):
                    break
                driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(5)
            except NoSuchElementException:
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

    return combined_text

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    keyword = "quantum"
    text = scrape_nslsl(keyword, max_pages=2)
    with open("nslsl_output.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Scraping done. Output saved to 'nslsl_output.txt'.")


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