import sys
import pickle
from pathlib import Path
sys.path.insert(0, '.')

# Load the existing pipeline 
model_path = Path('src/model/petadoption_pipeline.pkl')
with open(model_path, 'rb') as f:
    pipeline = pickle.load(f)

# Get the feature columns from the existing model
feature_cols = pipeline.get('feature_columns', [])
print(f"Current feature columns ({len(feature_cols)} total):")

# Identify which are Google NLP sentiment features
nlp_cols = [c for c in feature_cols if c.startswith('sentiment_') and c not in 
            ['sentiment_compound', 'sentiment_pos', 'sentiment_neg', 'sentiment_neu']]
             
print(f"\nGoogle NLP features found ({len(nlp_cols)}):")
for col in nlp_cols:
    print(f"  - {col}")
    
print(f"\nVADER+Tabular features ({len(feature_cols) - len(nlp_cols)}):")
vader_and_tabular = [c for c in feature_cols if c not in nlp_cols]
for col in vader_and_tabular:
    print(f"  - {col}")
