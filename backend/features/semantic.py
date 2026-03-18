import torch
from transformers import AutoTokenizer, AutoModel
import re
from urllib.parse import urlparse

class BrandDetector:
    def __init__(self):
        self.monitored_brands = {
            "paypal": ["paypal", "paypalinc", "xoom"],
            "microsoft": ["microsoft", "live", "outlook", "office365", "windows"],
            "apple": ["apple", "icloud", "itunes"],
            "google": ["google", "gmail", "youtube", "android"],
            "amazon": ["amazon", "aws", "prime"],
            "netflix": ["netflix"],
            "facebook": ["facebook", "meta", "instagram", "whatsapp"],
            "bank of america": ["bofa", "bankofamerica"]
        }
        
    def check_forgery(self, url: str, visible_text: str) -> dict:
        """Checks if a brand is heavily mentioned in the text but the domain doesn't match."""
        if not visible_text:
            return {"is_forgery": False, "brand": None}
            
        text_lower = visible_text.lower()
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for brand, legitimate_domains in self.monitored_brands.items():
            # If the brand name appears in the page text
            if brand in text_lower:
                # Check if the domain matches any known legitimate domain for that brand
                is_legit = any(legit in domain for legit in legitimate_domains)
                if not is_legit:
                    return {"is_forgery": True, "brand": brand.capitalize()}
                    
        return {"is_forgery": False, "brand": None}

class SemanticFeatureExtractor:
    def __init__(self, model_name="nreimers/MiniLM-L6-H384-uncased"):
        # Using a small, fast sentence-transformers model for extracting semantic embeddings of the visible text
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name).to(self.device)
            self.model.eval()
            self.is_loaded = True
        except Exception as e:
            print(f"Warning: Semantic model {model_name} could not be loaded. {e}")
            self.is_loaded = False

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def extract_features(self, text: str) -> torch.Tensor:
        if not text or len(text.strip()) == 0 or not getattr(self, 'is_loaded', False):
            return torch.zeros(384).to(self.device) # Dimension of MiniLM

        # Truncate text to max length
        encoded_input = self.tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors='pt').to(self.device)

        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # Perform pooling
        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        
        return sentence_embeddings.squeeze(0)
