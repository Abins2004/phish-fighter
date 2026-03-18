import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import datetime

class WebScraper:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_html(self, url: str) -> str:
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def extract_lexical_features(self, url: str) -> dict:
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path

        return {
            "url_length": len(url),
            "domain_length": len(domain),
            "has_https": url.startswith("https://"),
            "num_subdomains": domain.count(".") - 1 if domain.count(".") > 1 else 0,
            "has_at_symbol": "@" in url,
            "has_dashes_in_domain": "-" in domain,
            "num_digits_in_url": sum(c.isdigit() for c in url),
            "contains_ip": bool(re.search(r'\d+\.\d+\.\d+\.\d+', domain))
        }

    def parse_dom(self, html: str) -> dict:
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove noisy tags
        for script in soup(["script", "style", "noscript"]):
            script.extract()
            
        forms = soup.find_all('form')
        inputs = soup.find_all('input')
        links = soup.find_all('a')
        iframes = soup.find_all('iframe')
        
        return {
            "num_forms": len(forms),
            "num_inputs": len(inputs),
            "num_password_inputs": len(soup.find_all('input', type='password')),
            "num_links": len(links),
            "num_iframes": len(iframes),
            "visible_text": soup.get_text(separator=' ', strip=True)
        }
