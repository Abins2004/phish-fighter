import os
import json
import numpy as np
from datetime import datetime

class Explainer:
    def __init__(self, feature_names=None):
        if feature_names is None:
            self.feature_names = [
                "uses_ip_address", "long_url", "short_url", "contains_at_symbol", "redirecting_double_slash", 
                "prefix_suffix_hyphen", "excessive_subdomains", "uses_https", "domain_registration_length", 
                "external_favicon", "non_standard_port", "https_in_domain", "request_url_assets", 
                "anchor_url_routing", "links_in_script_tags", "server_form_handler", "info_email_mailto", 
                "abnormal_url", "website_forwarding", "status_bar_customization", "disables_right_click", 
                "uses_popup_window", "iframe_redirection", "domain_age", "dns_record", "web_traffic",
                "page_rank", "google_index", "links_pointing_to_page", "statistical_report"
            ]
        else:
            self.feature_names = feature_names

    def explain(self, model_importances: np.ndarray, extracted_features: dict) -> dict:
        """
        Provides reasoning for the prediction based on feature impacts.
        """
        explanation = {
            "highlighted_elements": [],
            "keywords": ["login", "verify", "secure", "update", "account"], # Mocked keywords
            "risk_factors": [],
            "predictive_basis": []
        }
        
        # Pass through threat intelligence to frontend
        if "threat_intel" in extracted_features:
            explanation["threat_intel"] = extracted_features["threat_intel"]
            
        # Parse LightGBM Feature Importances
        if model_importances is not None and len(model_importances) == len(self.feature_names):
            importances = list(zip(self.feature_names, model_importances))
            # Sort by absolute weight (highest impact)
            importances.sort(key=lambda x: abs(float(x[1])), reverse=True)
            
            # Select top 3 features
            explanation["predictive_basis"] = [
                {"feature": name.replace('_', ' ').title(), "weight": round(float(weight), 4)} 
                for name, weight in importances[:3] if weight > 0
            ]
            
            # Dynamically push the #1 risk factor to the UI if it's extremely high
            if importances[0][1] > 0:
                top_feature = importances[0][0].replace('_', ' ').title()
                explanation["risk_factors"].append(f"AI Matrix flagged {top_feature} as the primary anomaly metric.")
                
        # Check NLP Sentiments
        if extracted_features.get("nlp_alert"):
            words = ", ".join(extracted_features["nlp_alert"])
            explanation["risk_factors"].append(f"AI NLP Engine detected highly manipulative social engineering vocabulary: {words}")
            
        # Check basic heuristics
        if extracted_features.get("structured", {}).get("num_password_inputs", 0) > 0:
            if not extracted_features.get("lexical", {}).get("has_https", True):
                explanation["highlighted_elements"].append({
                    "tag": "form",
                    "reason": "Contains password input but connection is not HTTPS."
                })
                explanation["risk_factors"].append("Insecure Password Form")
                
        if extracted_features.get("lexical", {}).get("num_subdomains", 0) > 2:
            explanation["risk_factors"].append("Suspiciously long subdomain chain.")
            
        if extracted_features.get("lexical", {}).get("contains_ip", False):
             explanation["risk_factors"].append("URL uses an IP address instead of domain name.")
             
        if extracted_features.get("brand_check", {}).get("is_forgery"):
            brand = extracted_features["brand_check"]["brand"]
            explanation["risk_factors"].append(f"Major Forgery Risk: Claims to be '{brand}' but domain does not match official {brand} domains.")
            explanation["highlighted_elements"].append({
                "tag": "body",
                "reason": f"Text impersonates {brand}."
            })

        # In a real scenario, use SHAP values. For now, rely on heuristics.
        return explanation
