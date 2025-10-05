import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
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
        print(f"📄 Opening selected NSLSL document: {selected_url}")
        driver.get(selected_url)
        time.sleep(5)  # Wait for the attachment section to load fully

        try:
            # Locate attachment link
            attachment = driver.find_element(By.CSS_SELECTOR, "ul li a[href*='/NSLSL/Search/Download/']")
            pdf_href = attachment.get_attribute("href")
            pdf_name = attachment.text.strip() or "document.pdf"

            # Prepare save path
            pdf_path = os.path.join(download_dir, pdf_name)
            print(f"→ Found attachment: {pdf_name}")

            # Download using requests
            with requests.get(pdf_href, stream=True) as r:
                if r.status_code == 200:
                    with open(pdf_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    downloaded_pdf = pdf_path
                    print(f"✅ Downloaded successfully: {pdf_path}")
                else:
                    print(f"⚠️ Failed to download (HTTP {r.status_code}): {pdf_href}")

        except NoSuchElementException:
            print("⚠️ No attachment found for this document.")

    except Exception as e:
        print(f"❌ Error processing document: {e}")
    finally:
        driver.quit()

    return downloaded_pdf


# --- Example standalone usage ---
if __name__ == "__main__":
    # Example NSLSL document (replace dynamically in your program)
    doc_url = "https://extapps.ksc.nasa.gov/NSLSL/Search/DetailsForId/20820"

    result = download_nslsl_pdf(doc_url)

    if result:
        print(f"\n📂 File saved at: {result}")
    else:
        print("\nℹ️ No PDF found for this document.")
