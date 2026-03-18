import re
from urllib.parse import urlparse
import ipaddress

def extract_uci_features(url: str, html: str = "") -> list:
    """
    Extracts the 30 UCI Phishing features dynamically for a live URL.
    Returns: A list of 30 integers (-1, 0, or 1).
    -1 usually indicates phishing risk, 1 indicates safe.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
    except:
        domain = ""
        path = ""
        
    # 1. UsingIP (-1 false, 1 true)
    try:
        ipaddress.ip_address(domain)
        using_ip = -1
    except:
        using_ip = 1
        
    # 2. LongURL (1 < 54, 0 54-75, -1 > 75)
    ul = len(url)
    long_url = 1 if ul < 54 else (0 if ul <= 75 else -1)
    
    # 3. ShortURL (-1 if bit.ly etc)
    short_map = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'is.gd']
    short_url = -1 if any(s in domain for s in short_map) else 1
    
    # 4. Symbol@ (-1 if @ is present)
    symbol_at = -1 if '@' in url else 1
    
    # 5. Redirecting// (-1 if // in path)
    redirecting = -1 if '//' in path else 1
    
    # 6. PrefixSuffix- (-1 if - in domain)
    prefix_suffix = -1 if '-' in domain else 1
    
    # 7. SubDomains (1 if 1, 0 if 2, -1 if 3+)
    dots = domain.count('.')
    subdomains = 1 if dots <= 1 else (0 if dots == 2 else -1)
    
    # 8. HTTPS (-1 if http)
    https = 1 if url.startswith("https") else -1
    
    # 9. DomainRegLen (mock: 1)
    domain_reg = 1
    
    # 10. Favicon
    favicon = -1 if re.search(r'<link[^>]+rel="icon"[^>]+href="http', html, re.I) else 1
    
    # 11. NonStdPort
    port = parsed.port
    non_std_port = -1 if port and port not in [80, 443] else 1
    
    # 12. HTTPSDomainURL
    https_domain = -1 if 'https' in domain else 1
    
    # 13. RequestURL
    req_url = -1 if '<img src="http' in html.lower() else 1
    
    # 14. AnchorURL
    anchor_url = -1 if '<a href="#"' in html.lower() else 1
    
    # 15. LinksInScriptTags
    links_in_script = -1 if '<script src="http' in html.lower() else 1
    
    # 16. ServerFormHandler
    sfh = -1 if re.search(r'action="(|about:blank|#)"', html, re.I) else 1
    
    # 17. InfoEmail
    info_email = -1 if 'mailto:' in html else 1
    
    # 18. AbnormalURL
    abnormal_url = 1
    
    # 19. WebsiteForwarding
    forwarding = 1
    
    # 20. StatusBarCust
    statusbar = -1 if 'onmouseover="window.status' in html else 1
    
    # 21. DisableRightClick
    right_click = -1 if 'event.button==2' in html else 1
    
    # 22. UsingPopupWindow
    popup = -1 if 'window.open(' in html else 1
    
    # 23. IframeRedirection
    iframe = -1 if '<iframe' in html.lower() else 1
    
    # 24-30: WHOIS/Traffic Characteristics (Defaulting to 1 for live scanning)
    age = 1
    dns = 1
    traffic = 1
    pagerank = 1
    google_idx = 1
    links_pointing = 1
    stats = 1
    
    return [
        using_ip, long_url, short_url, symbol_at, redirecting, prefix_suffix,
        subdomains, https, domain_reg, favicon, non_std_port, https_domain,
        req_url, anchor_url, links_in_script, sfh, info_email, abnormal_url,
        forwarding, statusbar, right_click, popup, iframe, age, dns, traffic,
        pagerank, google_idx, links_pointing, stats
    ]
