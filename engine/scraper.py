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

def get_abstract(driver):
    """Helper function to find an abstract on a page from a list of selectors."""
    selectors = [
        "span#abstract-1", "div#abstract p", "div.abstract", "p[id$='lblAbstract']"
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

def scrape_nslsl(keyword, max_pages=2):
    """Scrapes the NASA Technical Reports Server (NTRS) for a given keyword."""
    print(f"Engine: Starting Selenium scraper for keyword: '{keyword}'")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    
    driver = None
    combined_text = ""
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 20)
        # NOTE: The old NSLSL URL is deprecated. This points to the modern NTRS.
        base_url = "https://ntrs.nasa.gov/search"
        
        driver.get(base_url)
        
        search_box = wait.until(EC.element_to_be_clickable((By.ID, "search-input")))
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        # The NTRS site structure is complex; this is a simplified approach to get titles.
        # A full implementation would require more detailed parsing.
        results = driver.find_elements(By.CSS_SELECTOR, 'app-card-list-item h6 a')
        
        if not results:
            return f"No results found for '{keyword}' on the NASA NTRS website."

        count = 0
        for res in results:
            if count >= 5: # Limit to 5 results for this demo to keep it fast
                break
            try:
                title = res.text
                # In a full version, you would click the link to get the abstract.
                # For this example, we'll use a placeholder.
                abstract = f"Placeholder abstract for '{title}'."
                combined_text += f"Title: {title}\nAbstract: {abstract}\n\n"
                count += 1
            except Exception:
                continue # Skip any item that fails
                
    except Exception as e:
        error_msg = f"An error occurred during scraping: {e}"
        print(error_msg)
        return error_msg
    finally:
        if driver:
            driver.quit()
    
    print("Engine: Scraping finished.")
    return combined_text
