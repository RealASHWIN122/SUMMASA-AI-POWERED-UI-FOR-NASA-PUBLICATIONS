import os
import time
import requests
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def download_nslsl_pdf(selected_url: str, download_dir: str = "downloads") -> str | None:
    """
    Downloads the PDF attachment (if any) for a selected NSLSL document.

    Args:
        selected_url (str): Full URL of the selected NSLSL document.
        download_dir (str): Directory to save the PDF.

    Returns:
        str | None: Path of the downloaded PDF, or None if no attachment found.
    """

    # --- Setup Chrome in headless mode ---
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    os.makedirs(download_dir, exist_ok=True)
    downloaded_pdf = None

    try:
        print(f"📄 Opening NSLSL document: {selected_url}")
        driver.get(selected_url)

        # Wait for the attachment section or give up after 15 seconds
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h6.detailSubHeader"))
            )
            time.sleep(3)  # give JS a moment to populate attachments
        except TimeoutException:
            print("⚠️ Timeout waiting for page content to load.")
            return None

        # Try to locate any PDF link in the Attachments section
        attachments = driver.find_elements(By.CSS_SELECTOR, "ul li a[href*='/NSLSL/Search/Download/']")
        if not attachments:
            print("⚠️ No attachment found on this page.")
            return None

        # Pick the first PDF link (or you can loop if you want all)
        attachment = attachments[0]
        pdf_href = attachment.get_attribute("href")

        # Convert relative href to absolute URL
        pdf_url = urljoin(selected_url, pdf_href)
        pdf_name = attachment.text.strip() or "document.pdf"
        pdf_path = os.path.join(download_dir, pdf_name)

        print(f"→ Found attachment: {pdf_name}")
        print(f"→ Downloading from: {pdf_url}")

        # Download file
        response = requests.get(pdf_url, stream=True)
        if response.status_code == 200:
            with open(pdf_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            downloaded_pdf = pdf_path
            print(f"✅ Downloaded successfully: {pdf_path}")
        else:
            print(f"⚠️ Failed to download (HTTP {response.status_code})")

    except Exception as e:
        print(f"❌ Error processing document: {e}")
    finally:
        driver.quit()

    return downloaded_pdf


# --- Example standalone usage ---
if __name__ == "__main__":
    # 🔹 Replace this with any NSLSL DetailsForId link that has an attachment
    doc_url = "https://extapps.ksc.nasa.gov/NSLSL/Search/DetailsForID/20820"

    result = download_nslsl_pdf(doc_url)
    if result:
        print(f"\n📂 File saved at: {result}")
    else:
        print("\nℹ️ No PDF found for this document.")
