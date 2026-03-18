import socket
import ssl
from urllib.parse import urlparse
import datetime

class MetadataExtractor:
    def __init__(self, timeout=5):
        self.timeout = timeout

    def extract_ssl_info(self, url: str) -> dict:
        parsed = urlparse(url)
        hostname = parsed.netloc
        if ":" in hostname:
            hostname = hostname.split(":")[0]

        if not hostname:
            return {"ssl_valid": False, "days_to_expiry": 0, "issuer": ""}

        context = ssl.create_default_context()
        try:
            with socket.create_connection((hostname, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as wrapped_sock:
                    cert = wrapped_sock.getpeercert()
                    
                    # Extract expiry date
                    not_after = cert.get('notAfter')
                    if not_after:
                        # Format commonly: "Dec 31 23:59:59 2024 GMT"
                        expiry_date = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                        days_to_expiry = (expiry_date - datetime.datetime.utcnow()).days
                        
                        issuer = dict(x[0] for x in cert['issuer'])
                        issuer_org = issuer.get('organizationName', '')
                        
                        return {
                            "ssl_valid": True,
                            "days_to_expiry": max(0, days_to_expiry),
                            "issuer": issuer_org
                        }
        except Exception as e:
            # E.g. connection refused, timeout, SSL error
            pass

        return {"ssl_valid": False, "days_to_expiry": 0, "issuer": ""}
