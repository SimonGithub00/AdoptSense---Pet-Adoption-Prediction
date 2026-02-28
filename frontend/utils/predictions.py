"""
Predictions module - handles feature engineering and model predictions
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.features_tabular import TabularFeatures
from frontend.utils.model_loader import get_model_loader


class AdoptionPredictor:
    """Make adoption speed predictions for pets."""
    
    ADOPTION_SPEED_LABELS = {
        0: "Same day",
        1: "1-7 days",
        2: "8-30 days",
        3: "31-90 days",
        4: "No adoption"
    }
    
    ADOPTION_SPEED_EMOJI = {
        0: "⭐⭐⭐⭐⭐",
        1: "⭐⭐⭐⭐",
        2: "⭐⭐⭐",
        3: "⭐⭐",
        4: "⭐"
    }
    
    def __init__(self):
        """Initialize predictor with model and feature engineering."""
        self.model_loader = get_model_loader()
        self.feature_engineer = TabularFeatures()
        self.scaler = self.model_loader.get_scaler()
        self.model = self.model_loader.get_xgb_model()
        self.feature_columns = self.model_loader.get_features()
    
    def predict(self, pet_data: pd.DataFrame) -> dict:
        """
        Make adoption speed prediction for pet(s).
        
        Args:
            pet_data: DataFrame with pet information
            
        Returns:
            Dictionary with predictions and probabilities
        """
        # Engineer features
        X = self.feature_engineer.feature_engineering_tabular(pet_data)
        
        # Ensure all expected features are present
        X = self._align_features(X)
        
        # Scale numeric features
        numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
        X_scaled = X.copy()
        X_scaled[numeric_features] = self.scaler.transform(X[numeric_features])
        
        # Make predictions
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        # Format results
        results = []
        for idx, (pred, probs) in enumerate(zip(predictions, probabilities)):
            result = {
                'pet_index': idx,
                'prediction': int(pred),
                'prediction_label': self.ADOPTION_SPEED_LABELS[int(pred)],
                'prediction_emoji': self.ADOPTION_SPEED_EMOJI[int(pred)],
                'confidence': float(probs[int(pred)]),
                'probabilities': {
                    i: float(probs[i]) 
                    for i in range(len(self.ADOPTION_SPEED_LABELS))
                },
                'original_data': pet_data.iloc[idx].to_dict() if len(pet_data) > idx else {}
            }
            results.append(result)
        
        return {
            'success': True,
            'predictions': results,
            'count': len(results)
        }
    
    def _align_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Align feature columns with model expectations.
        Add missing columns or drop extra columns.
        """
        for col in self.feature_columns:
            if col not in X.columns:
                # Add missing column with 0
                X[col] = 0
        
        # Keep only expected columns in order
        X = X[self.feature_columns]
        
        return X
    
    @staticmethod
    def get_adoption_speed_info() -> dict:
        """Get information about adoption speed classes."""
        return {
            'labels': AdoptionPredictor.ADOPTION_SPEED_LABELS,
            'emojis': AdoptionPredictor.ADOPTION_SPEED_EMOJI,
            'descriptions': {
                0: 'Pet adopted immediately - exceptional appeal',
                1: 'Fast adoption within first week - strong demand',
                2: 'Good adoption within first month - moderate appeal',
                3: 'Slower adoption within 3 months - needs improvement',
                4: 'No adoption after 100 days - critical intervention needed'
            }
        }


def make_prediction(pet_data: pd.DataFrame) -> dict:
    """
    Convenience function to make predictions.
    
    Args:
        pet_data: DataFrame with pet information
        
    Returns:
        Prediction results dictionary
    """
    predictor = AdoptionPredictor()
    try:
        results = predictor.predict(pet_data)
        return results
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
