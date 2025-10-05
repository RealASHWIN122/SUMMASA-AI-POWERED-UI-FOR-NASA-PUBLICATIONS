import os
import re
import requests
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def scrape_nslsl_search_results(driver, search_term, limit=5):
    """
    Performs a search on the NSLSL database and returns a list of document titles and their detail page URLs.
    This version does NOT scrape abstracts initially to speed up the search result display.
    """
    search_url = "https://extapps.ksc.nasa.gov/NSLSL/Search"
    try:
        print(f"Navigating to search page for term: '{search_term}'")
        driver.get(search_url)
        wait = WebDriverWait(driver, 20)
        
        # Wait for the search box and button to be ready
        search_box = wait.until(EC.presence_of_element_located((By.ID, "searchCriteria")))
        search_button = wait.until(EC.element_to_be_clickable((By.ID, "btnSearchSimple")))

        # Perform the search
        search_box.clear()
        search_box.send_keys(search_term)
        print("Clicking search button...")
        search_button.click()
        
        # Wait for the results to load by looking for the results count text
        print("Waiting for search results to load...")
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'results')]")))
        
        # Find the container for the results and extract links
        results_container = driver.find_element(By.ID, "searchResultList")
        result_links = results_container.find_elements(By.CLASS_NAME, "pubDetail")
        
        documents = []
        for link_element in result_links[:limit]:
            title = link_element.text.strip()
            url = link_element.get_attribute('href')
            if title and url:
                documents.append({"title": title, "url": url})
        
        print(f"Found {len(documents)} documents.")
        return documents

    except TimeoutException:
        print(f"⚠️ Timed out waiting for search results for '{search_term}'. The page might have no results or loaded too slowly.")
        return []
    except Exception as e:
        print(f"❌ An unexpected error occurred during search: {e}")
        # Save a screenshot for debugging if something goes wrong
        driver.save_screenshot('debug_error_search.png')
        return []

def get_abstracts_from_results(driver, documents):
    """
    Takes a list of documents (with URLs) and scrapes the abstract for each one.
    
    Args:
        driver: The Selenium WebDriver instance.
        documents (list): A list of dictionaries, e.g., [{'title': '...', 'url': '...'}]

    Returns:
        list: The updated list of dictionaries, with an 'abstract' key added to each.
    """
    print(f"Scraping abstracts for {len(documents)} documents...")
    for doc in documents:
        try:
            driver.get(doc['url'])
            abstract_wait = WebDriverWait(driver, 10)
            # This CSS selector finds a span whose id starts with 'abstract-'
            abstract_element = abstract_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[id^='abstract-']")))
            abstract_text = abstract_element.text.strip()
            doc['abstract'] = abstract_text if abstract_text else "No abstract content available."
            print(f"✅ Scraped abstract for: {doc['title']}")
        except TimeoutException:
            doc['abstract'] = "No abstract available on the page."
            print(f"⚠️ No abstract found for: {doc['title']}")
        except Exception as e:
            doc['abstract'] = f"An error occurred while scraping abstract: {e}"
            print(f"❌ Error scraping abstract for: {doc['title']}")
    return documents


def download_nslsl_pdf(driver, doc_url, save_dir='downloads'):
    """
    Navigates a document detail page and downloads the associated PDF file.
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    try:
        print(f"Navigating to document page: {doc_url}")
        driver.get(doc_url)
        wait = WebDriverWait(driver, 15)
        
        # The selector for the PDF attachment link
        attachment_selector = (By.CSS_SELECTOR, "a[href*='/NSLSL/Search/Download/']")
        attachment_element = wait.until(EC.presence_of_element_located(attachment_selector))
        
        # Construct the full, absolute URL for the PDF
        pdf_link = urljoin(doc_url, attachment_element.get_attribute('href'))
        print(f"Found PDF link: {pdf_link}")

        # Use requests to download the file to avoid browser-specific download dialogs
        response = requests.get(pdf_link, timeout=30)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Sanitize the filename to remove characters invalid for file systems
        raw_name = attachment_element.text.strip()
        pdf_name = re.sub(r'[\\/*?:"<>|]', "", raw_name) or "NSLSL_Document.pdf"
        if not pdf_name.lower().endswith('.pdf'):
            pdf_name += '.pdf'
        pdf_path = os.path.join(save_dir, pdf_name)
        
        # Write the content to a local file
        with open(pdf_path, "wb") as f:
            f.write(response.content)
            
        print(f"✅ Download complete: {pdf_path}")
        return pdf_path

    except TimeoutException:
        print(f"⚠️ Timed out waiting for the download link on page: {doc_url}")
        return None
    except Exception as e:
        print(f"❌ An error occurred while downloading the PDF: {e}")
        return None

