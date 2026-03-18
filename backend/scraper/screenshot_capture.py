import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

class ScreenshotCapture:
    def __init__(self, output_dir="backend/data/screenshots"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1280,720")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")

    def capture(self, url: str) -> str:
        """Captures a screenshot of the given URL and returns the file path."""
        try:
            # Note: requires chromedriver to be installed and in PATH
            # For simplicity in this project, we assume webdriver.Chrome() can find standard driver
            driver = webdriver.Chrome(options=self.options)
            driver.set_page_load_timeout(15)
            
            driver.get(url)
            time.sleep(2) # Give it time to render JS
            
            # Create a safe filename based on URL replacing non-alphanumeric chars
            safe_filename = "".join([c if c.isalnum() else "_" for c in url]) + ".png"
            # Truncate if too long
            safe_filename = safe_filename[:100] + ".png" if len(safe_filename) > 100 else safe_filename
            filepath = os.path.join(self.output_dir, safe_filename)
            
            driver.save_screenshot(filepath)
            driver.quit()
            
            return filepath
            
        except Exception as e:
            print(f"Error capturing screenshot for {url}: {e}")
            return ""
