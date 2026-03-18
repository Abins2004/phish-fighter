import os
import json
import random
import numpy as np
from typing import List, Dict

class DatasetManager:
    def __init__(self, data_file="backend/data/dataset.json"):
        self.data_file = data_file
        self.data: List[Dict] = []
        
        # Create dir if not exists
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        self.load()
        
        if not self.data:
            self._generate_mock_data()

    def load(self):
        # Explicitly look for the user's specific sample CSV file
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'phishing_sample.csv')
        if os.path.exists(csv_path):
            try:
                import pandas as pd
                df = pd.read_csv(csv_path)
                self.data = []
                
                # Dynamic Support for UCI Kaggle Dataset (30 Phishing Features)
                if 'class' in df.columns or 'UsingIP' in df.columns:
                    uci_cols = ['UsingIP', 'LongURL', 'ShortURL', 'Symbol@', 'Redirecting//', 'PrefixSuffix-', 'SubDomains', 'HTTPS', 'DomainRegLen', 'Favicon', 'NonStdPort', 'HTTPSDomainURL', 'RequestURL', 'AnchorURL', 'LinksInScriptTags', 'ServerFormHandler', 'InfoEmail', 'AbnormalURL', 'WebsiteForwarding', 'StatusBarCust', 'DisableRightClick', 'UsingPopupWindow', 'IframeRedirection', 'AgeofDomain', 'DNSRecording', 'WebsiteTraffic', 'PageRank', 'GoogleIndex', 'LinksPointingToPage', 'StatsReport']
                    for _, row in df.iterrows():
                        vec = [int(row[col]) for col in uci_cols]
                        
                        # UCI dataset: -1 is usually phishing, 1 is legitimate. Our model: 1 is phishing, 0 is safe
                        label_val = int(row['class'])
                        our_label = 1 if label_val == -1 else 0
                        
                        self.data.append({
                            "url": "dataset_url",
                            "features_vector": vec,
                            "label": our_label
                        })
                    print(f"Loaded {len(self.data)} robust UCI examples from CSV.")
                    return
                else:
                    for _, row in df.iterrows():
                        self.data.append({
                            "url": row['url'],
                            "features": {
                                "num_forms": int(row['num_forms']),
                                "num_inputs": int(row['num_inputs']),
                                "num_password_inputs": int(row['num_password_inputs']),
                                "num_links": int(row['num_links']),
                                "num_iframes": int(row['num_iframes'])
                            },
                            "label": int(row['label'])
                        })
                    print(f"Loaded {len(self.data)} standard examples from CSV.")
                    return
            except Exception as e:
                print(f"Error loading CSV dataset: {e}")
                
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"Error loading JSON dataset: {e}")
                self.data = []

    def save(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_entry(self, url: str, features: dict, label: int):
        """Adds a new pattern to dataset (Self-Updating Mechanism)"""
        self.data.append({
            "url": url,
            "features": features,
            "label": label # 0: Safe, 1: Phishing
        })
        self.save()

    def get_training_data(self):
        """Returns X and y arrays from the JSON dataset."""
        if not self.data:
            return np.array([]), np.array([])
            
        X = []
        y = []
        for entry in self.data:
            if "features_vector" in entry:
                X.append(entry["features_vector"])
            else:
                # Flatten structured features into a list for training the base ML models
                ft = entry.get("features", {})
                flat_features = [
                    ft.get("num_forms", 0),
                    ft.get("num_inputs", 0),
                    ft.get("num_password_inputs", 0),
                    ft.get("num_links", 0),
                    ft.get("num_iframes", 0)
                ]
                X.append(flat_features)
            y.append(entry.get("label", 0))
            
        return np.array(X), np.array(y)

    def _generate_mock_data(self):
        """Generates mock data for initial training."""
        for i in range(100):
            is_phishing = random.random() > 0.5
            
            features = {
                "num_forms": random.randint(1, 3) if is_phishing else random.randint(0, 1),
                "num_inputs": random.randint(3, 10) if is_phishing else random.randint(1, 5),
                "num_password_inputs": 1 if is_phishing and random.random() > 0.3 else 0,
                "num_links": random.randint(5, 50),
                "num_iframes": random.randint(1, 3) if is_phishing else 0
            }
            
            self.data.append({
                "url": f"http{'s' if not is_phishing else ''}://example{i}.{ 'com' if not is_phishing else 'xyz' }",
                "features": features,
                "label": 1 if is_phishing else 0
            })
            
        self.save()
        print(f"Generated {len(self.data)} mock training samples.")
