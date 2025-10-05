## File: nslsl_scraper.py (Restructured Version)
import os
import re
import requests
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def sanitize_filename(filename):
    """Removes characters that are invalid for filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def scrape_nslsl_search_results(driver, search_term, limit=25):
    """
    Performs a search on the NSLSL website and returns a list of found documents.
    This function ONLY scrapes the main search results page.
    
    Args:
        driver: An active Selenium WebDriver instance.
        search_term (str): The term to search for.
        limit (int): The maximum number of results to return.

    Returns:
        list: A list of dictionaries, each containing 'title' and 'url'.
    """
    search_url = "https://extapps.ksc.nasa.gov/NSLSL/Search"
    results = []
    
    try:
        print(f"Navigating to search page for term: '{search_term}'")
        driver.get(search_url)
        
        wait = WebDriverWait(driver, 20)
        
        search_box = wait.until(EC.presence_of_element_located((By.ID, "searchCriteria")))
        search_button = wait.until(EC.element_to_be_clickable((By.ID, "btnSearchSimple")))

        print(f"Entering search term: '{search_term}'")
        search_box.send_keys(search_term)
        
        print("Clicking search button...")
        search_button.click()
        
        print("Waiting for search results to load...")
        results_count_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'results')]"))
        )
        print(f"Results count found: {results_count_element.text}")
        
        results_container = driver.find_element(By.ID, "searchResultList")
        result_links = results_container.find_elements(By.CLASS_NAME, "pubDetail")
        
        print(f"Found {len(result_links)} result links on the page. Processing up to {limit}.")
        
        # Use a slice to respect the limit
        for link_element in result_links[:limit]:
            title = link_element.text.strip()
            url = link_element.get_attribute('href')
            if title and url:
                results.append({"title": title, "url": url})
                
        return results

    except TimeoutException:
        print("❌ TIMEOUT: The scraper failed to find the search results.")
        driver.save_screenshot('debug_screenshot.png')
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        return []
    except Exception as e:
        print(f"❌ An unexpected error occurred during search: {e}")
        return []

def get_abstract_for_doc(driver, doc_url):
    """
    Navigates to a single document URL and scrapes its abstract.
    
    Args:
        driver: An active Selenium WebDriver instance.
        doc_url (str): The URL of the document detail page.

    Returns:
        str: The abstract text, or a default message if not found.
    """
    try:
        print(f"Navigating to detail page: {doc_url}")
        driver.get(doc_url)
        wait = WebDriverWait(driver, 10)

        # The abstract is in a span with an ID that starts with 'abstract-'
        abstract_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[id^='abstract-']"))
        )
        abstract_text = abstract_element.text.strip()
        print("✅ Abstract found.")
        return abstract_text if abstract_text else "No abstract content available."

    except TimeoutException:
        print("⚠️ Abstract not found on page (timed out).")
        return "No abstract available for this document."
    except Exception as e:
        print(f"❌ Error scraping abstract: {e}")
        return "An error occurred while fetching the abstract."


# The download_nslsl_pdf function remains unchanged
def download_nslsl_pdf(driver, doc_url, save_dir='downloads'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    try:
        driver.get(doc_url)
        wait = WebDriverWait(driver, 15)
        attachment_selector = (By.CSS_SELECTOR, "a[href*='/NSLSL/Search/Download/']")
        attachment_element = wait.until(EC.presence_of_element_located(attachment_selector))
        relative_link = attachment_element.get_attribute('href')
        raw_name = attachment_element.text.strip()
        pdf_link = urljoin(doc_url, relative_link)
        pdf_name = sanitize_filename(raw_name) or "NSLSL_Document.pdf"
        pdf_path = os.path.join(save_dir, pdf_name)
        print(f"⬇️  Downloading '{pdf_name}'...")
        response = requests.get(pdf_link, timeout=30)
        response.raise_for_status()
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Download complete: {pdf_path}")
        return pdf_path
    except TimeoutException:
        print(f"⚠️ Timed out waiting for PDF attachment link on page: {doc_url}")
        return None
    except Exception as e:
        print(f"❌ An error occurred while processing {doc_url}: {e}")
        return None