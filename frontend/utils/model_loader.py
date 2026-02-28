"""
Model loader utility - handles loading the pickled XGBoost pipeline
"""
import pickle
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any

class ModelLoader:
    """Load and manage the pet adoption prediction model pipeline."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def load_model(self) -> Dict[str, Any]:
        """
        Load the model pipeline from disk (singleton pattern).
        
        Returns:
            Dictionary with 'scaler' and 'model' keys
        """
        if self._model is None:
            # Find the model file
            model_path = self._find_model_path()
            
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found at {model_path}")
            
            with open(model_path, 'rb') as f:
                self._model = pickle.load(f)
        
        return self._model
    
    @staticmethod
    def _find_model_path() -> Path:
        """Find the model pickle file."""
        # Search up from current directory
        current = Path(__file__).parent.parent.parent  # Go up to project root
        
        possible_paths = [
            current / "src" / "model" / "petadoption_pipeline.pkl",
            current / "src" / "petadoption_pipeline.pkl",
            Path.cwd() / "src" / "model" / "petadoption_pipeline.pkl",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # If not found, raise error with paths tried
        raise FileNotFoundError(
            f"Model file not found. Tried:\n" + "\n".join(str(p) for p in possible_paths)
        )
    
    def get_features(self) -> list:
        """Get the list of expected feature columns."""
        pipeline = self.load_model()
        return pipeline.get('feature_columns', [])
    
    def get_scaler(self):
        """Get the fitted StandardScaler."""
        pipeline = self.load_model()
        return pipeline.get('scaler')
    
    def get_xgb_model(self):
        """Get the fitted XGBoost model."""
        pipeline = self.load_model()
        return pipeline.get('model')


def get_model_loader() -> ModelLoader:
    """Get singleton instance of model loader."""
    return ModelLoader()
