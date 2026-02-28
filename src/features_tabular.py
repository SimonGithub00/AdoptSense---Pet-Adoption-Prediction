import pandas as pd
import numpy as np
from pathlib import Path

# We use VADER sentiment analyzer for informal/social-media-style text
try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    import nltk
    # We ensure VADER lexicon is available
    try:
        nltk.data.find('sentiment/vader_lexicon')
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False

class TabularFeatures:
    """We engineer tabular features for pet adoption prediction."""
    
    def __init__(self):
        """Initialize with label mappings and sentiment analyzer."""
        # We use these mappings to add readable labels alongside numeric codes
        self.speed_labels = {0: "Same day", 1: "1-7d", 2: "8-30d", 3: "31-90d", 4: "No adoption"}
        # We initialize VADER sentiment analyzer if available
        self.sia = SentimentIntensityAnalyzer() if SENTIMENT_AVAILABLE else None
        
    def feature_engineering_tabular(self, df, label_dicts=None):
        """
        We transform raw tabular data into engineered features for XGBoost.
        
        Args:
            df: Raw DataFrame with columns from train.csv
            label_dicts: Dict with 'color_map', 'state_map' for label lookups.
                         If None, we skip label encoding.
        
        Returns:
            DataFrame with engineered features ready for XGBoost.
        """
        df = df.copy()
        
        # --- 1. We handle missing numeric values ---
        numeric_cols = ['Age', 'PhotoAmt', 'Fee', 'VideoAmt', 'Quantity']
        for col in numeric_cols:
            if col in df.columns:
                df[col].fillna(df[col].median(), inplace=True)
        
        # --- 2. We create binary flags from numeric features ---
        df['has_photo'] = (df['PhotoAmt'] > 0).astype(int)
        df['has_video'] = (df['VideoAmt'] > 0).astype(int)
        df['is_free'] = (df['Fee'] == 0).astype(int)
        df['has_name'] = df['Name'].notna().astype(int)
        
        # --- 3. We bin Age into age groups ---
        df['age_bin'] = pd.cut(df['Age'], 
                                bins=[-1, 1, 3, 12, 24, 300],
                                labels=['<1mo', '1-3mo', '3-12mo', '1-2yr', '2yr+'])
        # Convert to ordinal for XGBoost (0=<1mo, 1=1-3mo, etc.)
        df['age_bin'] = df['age_bin'].cat.codes
        
        # --- 4. We handle Description: length, word count & sentiment ---
        df['desc_word_count'] = df['Description'].fillna('').str.split().str.len()
        # We drop desc_len to avoid perfect correlation with word_count
        
        # We extract sentiment features from description if available
        if self.sia is not None:
            sentiments = df['Description'].fillna('').apply(
                lambda x: self.sia.polarity_scores(x) if x else {'compound': 0, 'pos': 0, 'neu': 0, 'neg': 0}
            )
            df['sentiment_compound'] = sentiments.apply(lambda x: x['compound'])
            df['sentiment_pos'] = sentiments.apply(lambda x: x['pos'])
            df['sentiment_neg'] = sentiments.apply(lambda x: x['neg'])
            df['sentiment_neu'] = sentiments.apply(lambda x: x['neu'])
        else:
            # We fallback to zeros if VADER is not available
            df['sentiment_compound'] = 0.0
            df['sentiment_pos'] = 0.0
            df['sentiment_neg'] = 0.0
            df['sentiment_neu'] = 0.0
        
        # --- 5. We bin PhotoAmt and Description length ---
        df['photo_bin'] = pd.cut(df['PhotoAmt'], 
                                  bins=[-1, 0, 2, 5, 10, 100],
                                  labels=['0', '1-2', '3-5', '6-10', '10+'])
        df['photo_bin'] = df['photo_bin'].cat.codes
        
        df['desc_bin'] = pd.cut(df['desc_word_count'],
                                 bins=[-1, 0, 25, 75, 150, 1000],
                                 labels=['None', 'Short', 'Medium', 'Long', 'Very Long'])
        df['desc_bin'] = df['desc_bin'].cat.codes
        
        # --- 6. We keep categorical features as-is (XGBoost handles them) ---
        # We fill missing categoricals with a sentinel value
        categorical_cols = ['Type', 'Gender', 'MaturitySize', 'FurLength',
                           'Vaccinated', 'Dewormed', 'Sterilized', 'Health',
                           'Color1', 'State']
        for col in categorical_cols:
            if col in df.columns:
                df[col].fillna(-1, inplace=True)
        
        # --- 8. We select features for final output ---
        feature_cols = (
            numeric_cols +  # Original numerics (already filled)
            ['has_photo', 'has_video', 'is_free', 'has_name'] +  # Binary flags
            ['age_bin', 'photo_bin', 'desc_bin', 'desc_word_count'] +  # Binned/derived
            ['sentiment_compound', 'sentiment_pos', 'sentiment_neg', 'sentiment_neu'] +  # Sentiment features
            categorical_cols  # Categorical features
        )
        
        # We keep only columns that exist in the dataframe
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        return df[feature_cols]
