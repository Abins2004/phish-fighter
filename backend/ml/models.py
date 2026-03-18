import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
import numpy as np
import os
import joblib
import pandas as pd

class ClassificationModels:
    def __init__(self, model_dir=None):
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), '..', 'data', 'models')
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)
            
        self.log_reg = LogisticRegression(max_iter=1000)
        self.svm = SVC(kernel='linear', probability=True)
        self.lgbm = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.05)
        
        self.is_trained = False

    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Trains the base models on historical data using GridSearchCV."""
        if len(y_train) < 5:
            print("Dataset too small for formal training. Skipping.")
            return

        print("Tuning and Training Logistic Regression... 🚀")
        param_grid_lr = {'C': [0.1, 1.0, 10.0]}
        grid_lr = GridSearchCV(LogisticRegression(max_iter=1000), param_grid_lr, cv=min(3, len(y_train)//2))
        grid_lr.fit(X_train, y_train)
        self.log_reg = grid_lr.best_estimator_
        
        print("Training Linear SVM...")
        self.svm.fit(X_train, y_train)
        
        print("Tuning and Training LightGBM... 🚀")
        param_grid_lgb = {
            'n_estimators': [50, 100],
            'learning_rate': [0.01, 0.05, 0.1]
        }
        grid_lgb = GridSearchCV(lgb.LGBMClassifier(), param_grid_lgb, cv=min(3, len(y_train)//2))
        grid_lgb.fit(X_train, y_train)
        self.lgbm = grid_lgb.best_estimator_
        
        self.is_trained = True
        self.save_models()

    def predict_proba(self, X: np.ndarray) -> dict:
        """Returns predictions from all base models."""
        if not self.is_trained:
            # Fallback for untrained models
            return {
                "logistic_regression": [0.5, 0.5],
                "svm": [0.5, 0.5],
                "lightgbm": [0.5, 0.5]
            }
            
        return {
            "logistic_regression": self.log_reg.predict_proba(X)[0].tolist(),
            "svm": self.svm.predict_proba(X)[0].tolist(),
            "lightgbm": self.lgbm.predict_proba(X)[0].tolist()
        }
        
    def get_feature_importance(self) -> np.ndarray:
        if self.is_trained:
            return self.lgbm.feature_importances_
        return np.array([])
        
    def save_models(self):
        joblib.dump(self.log_reg, os.path.join(self.model_dir, 'log_reg.pkl'))
        joblib.dump(self.svm, os.path.join(self.model_dir, 'svm.pkl'))
        joblib.dump(self.lgbm, os.path.join(self.model_dir, 'lgbm.pkl'))

    def load_models(self):
        log_reg_path = os.path.join(self.model_dir, 'log_reg.pkl')
        if os.path.exists(log_reg_path):
            self.log_reg = joblib.load(log_reg_path)
            self.svm = joblib.load(os.path.join(self.model_dir, 'svm.pkl'))
            self.lgbm = joblib.load(os.path.join(self.model_dir, 'lgbm.pkl'))
            self.is_trained = True
