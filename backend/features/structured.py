from bs4 import BeautifulSoup
import numpy as np

class StructuredFeatureExtractor:
    def __init__(self):
        # We define a vocabulary of interesting HTML tags for phishing detection
        self.target_tags = ["html", "head", "title", "body", "div", "span", "a", "img", 
                            "form", "input", "button", "iframe", "script", "link", "meta"]
        self.tag_to_idx = {tag: i for i, tag in enumerate(self.target_tags)}
        
    def extract_features(self, html: str) -> np.ndarray:
        if not html:
            return np.zeros(len(self.target_tags))
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Count frequency of structural tags
        tag_counts = np.zeros(len(self.target_tags))
        
        for tag in soup.find_all(True):
            tag_name = tag.name.lower()
            if tag_name in self.tag_to_idx:
                tag_counts[self.tag_to_idx[tag_name]] += 1
                
        # Normalize the counts to frequencies (optional, but good for ML)
        total_tags = np.sum(tag_counts)
        if total_tags > 0:
            tag_freqs = tag_counts / total_tags
        else:
            tag_freqs = tag_counts
            
        return tag_freqs
