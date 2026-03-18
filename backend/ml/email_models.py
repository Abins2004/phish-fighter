import lightgbm as lgb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import os
import joblib

class EmailTextClassifier:
    def __init__(self, model_dir=None):
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), '..', 'data', 'models')
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)
            
        # Converts raw English text into mathematical word frequencies
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
        # Dedicated LightGBM for Text
        self.lgbm = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.05)
        
        self.is_trained = False
        
    def train(self, csv_path: str):
        """Trains the text classifier using a dataset of Enron/Phishing emails."""
        print(f"Loading email dataset from {csv_path}...")
        try:
            df = pd.read_csv(csv_path)
            
            # Ensure dataset has text/body and label columns
            text_col = 'text' if 'text' in df.columns else 'body' if 'body' in df.columns else None
            label_col = 'label' if 'label' in df.columns else None
            
            if not text_col or not label_col:
                print(f"Error: Dataset must contain text/body and label columns. Found: {df.columns}")
                return False
                
            # If dataset is massive, sample it down to prevent MemoryErrors during live UI training
            if len(df) > 50000:
                print(f"Dataset has {len(df)} rows. Sampling down to 50,000 pristine examples to prevent memory exhaustion...")
                df = df.sample(n=50000, random_state=42)
                
            X_text = df[text_col].fillna('').values
            y = df[label_col].values
            
            print("Vectorizing text using TF-IDF (identifying critical linguistic heuristics)...")
            X_matrix = self.vectorizer.fit_transform(X_text)
            
            print("Training LightGBM NLP Model on email dataset...")
            # We skip GridSearchCV here for speed, but the architecture is the same
            self.lgbm.fit(X_matrix.astype(np.float32), y)
            
            self.is_trained = True
            self.save_models()
            print("Email Text Classification Model trained successfully! ✅")
            return True
            
        except Exception as e:
            print(f"Failed to train email model: {e}")
            return False
            
    def predict_proba(self, text: str) -> float:
        """Returns the probability (0.0 to 1.0) that the email text is a phishing attempt."""
        if not self.is_trained or not text.strip():
            return 0.0
            
        # Convert the new text into the exact mathematical shape the model was trained on
        X_matrix = self.vectorizer.transform([text])
        
        # lgbm.predict_proba returns [[prob_safe, prob_phishing]]
        prediction = self.lgbm.predict_proba(X_matrix.astype(np.float32))
        return float(prediction[0][1])
        
    def get_suspicious_words_in_text(self, text: str) -> list:
        """Finds the specific words in a given text that the model learned are highly correlated with phishing."""
        if not self.is_trained or not text.strip():
            return []
            
        feature_names = self.vectorizer.get_feature_names_out()
        importances = self.lgbm.feature_importances_
        
        # Extract words actually present in this text
        text_lower = text.lower()
        found_suspicious = []
        for i, word in enumerate(feature_names):
            if importances[i] > 0 and word in text_lower:
                found_suspicious.append((word, importances[i]))
                
        # Sort by importance and return top 5
        found_suspicious.sort(key=lambda x: x[1], reverse=True)
        return [word for word, weight in found_suspicious[:5]]
        
    def save_models(self):
        joblib.dump(self.vectorizer, os.path.join(self.model_dir, 'email_tfidf.pkl'))
        joblib.dump(self.lgbm, os.path.join(self.model_dir, 'email_lgbm.pkl'))

    def load_models(self):
        tfidf_path = os.path.join(self.model_dir, 'email_tfidf.pkl')
        lgbm_path = os.path.join(self.model_dir, 'email_lgbm.pkl')
        
        if os.path.exists(tfidf_path) and os.path.exists(lgbm_path):
            self.vectorizer = joblib.load(tfidf_path)
            self.lgbm = joblib.load(lgbm_path)
            self.is_trained = True
            return True
        return False
