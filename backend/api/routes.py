from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database.models import SessionLocal, ScanLog
from scraper.web_scraper import WebScraper
from scraper.screenshot_capture import ScreenshotCapture
from scraper.metadata import MetadataExtractor
from features.structured import StructuredFeatureExtractor
from features.visual import VisualFeatureExtractor
from features.semantic import SemanticFeatureExtractor, BrandDetector
from ml.models import ClassificationModels
from ml.email_models import EmailTextClassifier
from ml.fusion import FusionPipeline
from ml.explainer import Explainer
from ml.dataset import DatasetManager
from features.uci_extractor import extract_uci_features
from features.threat_intel import ThreatIntelligence

router = APIRouter(prefix="/api")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class URLRequest(BaseModel):
    url: str
    raw_text: Optional[str] = None

class TrainRequest(BaseModel):
    url: str
    label: int

# Initialize Scrapers & Extractors
web_scraper = WebScraper()
screenshot_capturer = ScreenshotCapture()
meta_extractor = MetadataExtractor()
struct_ext = StructuredFeatureExtractor()
vis_ext = VisualFeatureExtractor()
sem_ext = SemanticFeatureExtractor()
brand_detector = BrandDetector()
explain_engine = Explainer()
dataset_manager = DatasetManager()
threat_intel = ThreatIntelligence()

# Initialize Models
ml_models = ClassificationModels()
email_classifier = EmailTextClassifier()
fusion_model = FusionPipeline()

try:
    ml_models.load_models()
    fusion_model.load_model()
    
    # Init Email Classifier (Kaggle Dataset Trainer)
    import os
    kaggle_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'email_datasets.csv')
    flag_file = os.path.join(email_classifier.model_dir, 'email_kaggle_trained.flag')
    
    if os.path.exists(kaggle_csv) and not os.path.exists(flag_file):
        print("Massive Kaggle Dataset detected! Commencing background NLP Model Retraining...")
        email_classifier.train(kaggle_csv)
        with open(flag_file, 'w') as f:
            f.write("trained_on_kaggle")
    else:
        email_classifier.load_models()
except Exception as e:
    print(f"Warning: Models not fully loaded. {e}")

@router.post("/analyze-url")
def analyze_url(request: URLRequest, db: Session = Depends(get_db)):
    url = request.url
    
    # 1. Provide fast preliminary response if URL is malformed
    if not url.startswith("http"):
        url = "http://" + url
        
    try:
        # 1. Data Acquisition
        html = web_scraper.fetch_html(url)
        screenshot_path = screenshot_capturer.capture(url)
        ssl_info = meta_extractor.extract_ssl_info(url)
        lexical = web_scraper.extract_lexical_features(url)
        
        # 2. Feature Extraction
        struct_feats = web_scraper.parse_dom(html)
        visible_text = struct_feats.get("visible_text", "")
        
        # Convert to arrays/tensors for models
        struct_arr = struct_ext.extract_features(html)
        
        # 3. Semantic Analysis (NLP on Raw Email body OR Webpage text)
        text_to_analyze = request.raw_text if request.raw_text else visible_text
        semantic_feats = sem_ext.extract_features(text_to_analyze)
        brand_check = brand_detector.check_forgery(url, text_to_analyze)
        
        # Base Machine Learning Logic
        import torch
        struct_tensor = torch.tensor(struct_arr, dtype=torch.float32)

        # 3. Model Inference
        # Get base model scores based on the live 30 dynamically extracted UCI features
        uci_vector = extract_uci_features(url, html)
        base_scores = ml_models.predict_proba([uci_vector])
        
        # Override the PyTorch fusion simulator to just use the hyper-accurate LightGBM UCI model prediction directly
        # since it is now highly trained on 11,000 real-world examples!
        if "lightgbm" in base_scores:
            fusion_score = base_scores["lightgbm"][1]
        elif "logistic_regression" in base_scores:
            fusion_score = base_scores["logistic_regression"][1]
        else:
            fusion_score = 0.5
        
        classification = "Phishing" if fusion_score >= 0.55 else "Suspicious" if fusion_score > 0.3 else "Safe"
        
        # NLP Manipulation Override (If raw text was provided)
        nlp_alert = []
        if request.raw_text:
            # Pass the raw text through the new TF-IDF LightGBM Dataset-trained model
            email_phishing_prob = email_classifier.predict_proba(request.raw_text)
            
            if email_phishing_prob > 0.5:
                # The ML model flagged it! Extract exactly which words triggered the model:
                nlp_alert = email_classifier.get_suspicious_words_in_text(request.raw_text)
                if not nlp_alert:
                    nlp_alert = ["AI detected suspicious semantic patterns"]
                    
                classification = "Phishing"
                # Combine the model scores
                fusion_score = max(fusion_score, email_phishing_prob)
        
        # Cross-reference with global threat intelligence (if API key configured)
        vt_results = threat_intel.check_url(url)
        
        if vt_results.get("status") == "success" and vt_results.get("malicious_votes", 0) > 0:
            # If globally blacklisted, override local AI heuristics to guarantee safety
            classification = "Phishing"
            fusion_score = max(fusion_score, 0.99)
        
        # 4. Explainability
        explain_data = {
            "lexical": lexical,
            "structured": struct_feats,
            "ssl_info": ssl_info,
            "brand_check": brand_check,
            "threat_intel": vt_results,
            "nlp_alert": nlp_alert
        }
        explanation = explain_engine.explain(ml_models.get_feature_importance(), explain_data)
        
        # 5. Save to Log
        log = ScanLog(url=url, score=fusion_score, classification=classification, is_https=lexical["has_https"])
        db.add(log)
        db.commit()
        
        return {
            "url": url,
            "score": round(fusion_score, 4),
            "classification": classification,
            "base_model_scores": {k: round(v[1], 4) for k, v in base_scores.items()},
            "explainability": explanation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train-model")
def train_model(request: TrainRequest, background_tasks: BackgroundTasks):
    """Adds a new labeled entry to the dataset and triggers retraining in the background."""
    # First get features
    html = web_scraper.fetch_html(request.url)
    features = web_scraper.parse_dom(html)
    
    dataset_manager.add_entry(request.url, features, request.label)
    
    # Trigger training in background
    def retrain():
        print("Starting background training...")
        X, y = dataset_manager.get_training_data()
        if len(y) > 0:
            ml_models.train(X, y)
            print("Retraining completed.")
            
    background_tasks.add_task(retrain)
    
    return {"message": "Data added and retraining triggered.", "num_samples": len(dataset_manager.data)}

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Returns historical scan analytics."""
    try:
        total = db.query(ScanLog).count()
        phishing = db.query(ScanLog).filter(ScanLog.classification == "Phishing").count()
        safe = db.query(ScanLog).filter(ScanLog.classification == "Safe").count()
        suspicious = db.query(ScanLog).filter(ScanLog.classification == "Suspicious").count()
        
        recent = db.query(ScanLog).order_by(ScanLog.timestamp.desc()).limit(15).all()
        
        return {
            "metrics": {
                "total": total,
                "phishing": phishing,
                "safe": safe,
                "suspicious": suspicious
            },
            "recent": [
                {
                    "url": r.url,
                    "score": round(r.score * 100, 1),
                    "classification": r.classification,
                    "date": r.timestamp.strftime("%Y-%m-%d %H:%M")
                }
                for r in recent
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
