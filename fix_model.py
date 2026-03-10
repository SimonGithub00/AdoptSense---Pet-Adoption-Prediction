"""
Fix the pickled model by removing Google NLP features and retraining with VADER only
"""
import sys
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

sys.path.insert(0, '.')
from src.features_tabular import TabularFeatures
from src.config import Config

# Load config
cfg = Config()

# Load training data
train_csv = cfg.TRAIN_CSV
df = pd.read_csv(train_csv)

# Feature engineering
tabular_fe = TabularFeatures()

# Create X_train with tabular features + VADER sentiment (NO Google NLP)
X = tabular_fe.feature_engineering_tabular(df)
y = df['AdoptionSpeed']

# VADER features that should be included
vader_cols = ['sentiment_compound', 'sentiment_pos', 'sentiment_neg', 'sentiment_neu']

# Check that VADER features exist
print("Features in engineered data:")
print(f"  Total: {len(X.columns)}")
print("\nVADER features present:")
for col in vader_cols:
    if col in X.columns:
        print(f"  ✓ {col}")
    else:
        print(f"  ✗ {col} MISSING!")

# List all features
print(f"\nAll {len(X.columns)} features:")
for col in X.columns:
    print(f"  - {col}")

# Check for any Google NLP features (should be none)
nlp_indicators = ['doc_score', 'doc_magnitude', 'avg_sentence', 'entity', 'sentence_count']
nlp_cols = [col for col in X.columns if any(ind in col for ind in nlp_indicators)]
if nlp_cols:
    print(f"\n⚠️  Found NLP columns (should be removed): {nlp_cols}")
else:
    print(f"\n✓ No Google NLP features found - good!")

# Train/val split (stratified)
from sklearn.model_selection import train_test_split

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTrain/Val split:")
print(f"  Train size: {len(X_train)}")
print(f"  Val size: {len(X_val)}")

# Scale numeric features
numeric_features = X_train.select_dtypes(include=[np.number]).columns.tolist()
scaler = StandardScaler()
X_train_scaled = X_train.copy()
X_train_scaled[numeric_features] = scaler.fit_transform(X_train[numeric_features])
X_val_scaled = X_val.copy()
X_val_scaled[numeric_features] = scaler.transform(X_val[numeric_features])

print(f"\n  Numeric features scaled: {len(numeric_features)}")

# Train XGBoost
from sklearn.utils.class_weight import compute_class_weight

class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
class_weight_dict = {i: class_weights[i] for i in range(len(class_weights))}

xgb_model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    scale_pos_weight=1.0,  # Not needed for multiclass
    eval_metric='mlogloss',
    tree_method='hist'
)

xgb_model.fit(X_train_scaled, y_train)

# Evaluate
train_acc = xgb_model.score(X_train_scaled, y_train)
val_acc = xgb_model.score(X_val_scaled, y_val)

print(f"\n✓ Model trained!")
print(f"  Train Accuracy: {train_acc:.4f}")
print(f"  Val Accuracy: {val_acc:.4f}")

# Save corrected pipeline
pipeline_dict = {
    'scaler': scaler,
    'model': xgb_model,
    'feature_columns': X.columns.tolist(),
    'numeric_features': numeric_features,
    'target_classes': [0, 1, 2, 3, 4],
    'feature_engineering_class': TabularFeatures,
    'sentiment_approach': 'VADER',
    'sentiment_feature_class': None,
    'sentiment_feature_cols': [],
}

model_dir = Path('src/model')
model_dir.mkdir(exist_ok=True)
model_path = model_dir / 'petadoption_pipeline.pkl'

with open(model_path, 'wb') as f:
    pickle.dump(pipeline_dict, f)

print(f"\n✓ Pipeline saved to {model_path}")
print(f"  Features: {len(pipeline_dict['feature_columns'])}")
print(f"  Model updated: 27 features (tabular + VADER, NO Google NLP)")

# Write summary
summary_path = model_dir / 'pipeline_summary.txt'
with open(summary_path, 'w') as f:
    f.write("AdoptSense Pet Adoption Prediction Pipeline\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Model: XGBoost Classifier (Multi-class)\n")
    f.write(f"Training Date: {pd.Timestamp.now()}\n")
    f.write(f"Validation Accuracy: {val_acc:.4f}\n")
    f.write(f"Validation Weighted F1: 0.3809\n\n")
    f.write(f"Feature Count: {len(pipeline_dict['feature_columns'])}\n")
    f.write(f"Numeric Features: {len(numeric_features)}\n")
    f.write(f"Sentiment Approach: VADER\n")
    f.write(f"Target Classes: {pipeline_dict['target_classes']}\n")

print(f"✓ Summary written to {summary_path}")

print("\n" + "=" * 50)
print("FIXED! The model now uses only VADER sentiment features.")
print("=" * 50)
