import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

class ThreatIntelligence:
    def __init__(self):
        self.api_key = os.getenv("VIRUSTOTAL_API_KEY")

    def check_url(self, url: str) -> dict:
        """
        Cross-references the URL with the global VirusTotal threat database.
        Returns the number of security vendors who flagged it.
        """
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            return {"status": "disabled", "message": "VirusTotal API key not configured in .env"}

        # Calculate URL identifier for VirusTotal v3 API
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        
        headers = {
            "accept": "application/json",
            "x-apikey": self.api_key
        }
        
        try:
            response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                stats = data['data']['attributes']['last_analysis_stats']
                malicious = stats.get('malicious', 0) + stats.get('suspicious', 0)
                total = sum(stats.values())
                return {
                    "status": "success",
                    "malicious_votes": malicious,
                    "total_votes": total,
                    "permalink": f"https://www.virustotal.com/gui/url/{url_id}"
                }
            elif response.status_code == 404:
                return {"status": "success", "malicious_votes": 0, "total_votes": 0, "message": "Clean (Not found in threat database)"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
        return {"status": "error", "message": f"API Error: {response.status_code}"}
