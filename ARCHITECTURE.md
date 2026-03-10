# 🏗️ AdoptSense Frontend - Technical Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Streamlit)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Home | Batch Upload | Single Form | About   (4 Tabs)   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATA INPUT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  CSV Upload  │  │  Form Input  │  │   Validation │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 FEATURE ENGINEERING LAYER                        │
│  (frontend/utils/predictions.py → src/features_tabular.py)      │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  • Numeric feature engineering                       │      │
│  │  • Categorical encoding                              │      │
│  │  • Derived feature creation                          │      │
│  │  • Description word count, sentiment (optional)      │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  PREPROCESSING LAYER                             │
│  (frontend/utils/predictions.py)                                │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  • Feature alignment (add missing, drop extra)       │      │
│  │  • StandardScaler (from model pipeline)              │      │
│  │  • Numeric features normalization                    │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MODEL INFERENCE LAYER                         │
│  (frontend/utils/model_loader.py → src/model/)                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  XGBoost Classifier                                  │      │
│  │  • Predict: Adoption Speed (0-4)                    │      │
│  │  • Predict_proba: Probability for each class        │      │
│  │  • 300 estimators, depth=6, learning_rate=0.1       │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  RECOMMENDATION ENGINE                           │
│  (frontend/utils/recommendations.py)                            │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  • Analyze pet characteristics                       │      │
│  │  • Match against 6 recommendation categories         │      │
│  │  • Score by impact (weighted)                        │      │
│  │  • Generate top N suggestions (typically 3)          │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER (Streamlit)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Predictions │  │ Visualizations│  │Recommendations          │
│  │  • Speed     │  │  • Bar chart  │  │  • Ranked   │          │
│  │  • Confidence│  │  • Pie chart  │  │  • Detailed │          │
│  │  • Probs     │  │  • Heatmap    │  │  • Actionable          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Single Pet Prediction Flow

```
User fills form
    ↓
Streamlit collects inputs
    ↓
Create pandas DataFrame (1 row)
    ↓
predictions.py:make_prediction(df)
    ↓
AdoptionPredictor.__init__() [loads model, scaler, features]
    ↓
feature_engineer.feature_engineering_tabular(df)
    ↓
_align_features() [ensure all model features present]
    ↓
scaler.transform() [scale numeric features]
    ↓
model.predict() [get adoption speed class 0-4]
    ↓
model.predict_proba() [get probability for each class]
    ↓
Format results dict
    ↓
RecommendationEngine.generate_recommendations()
    ↓
Return to UI [display prediction + recommendations]
```

### Batch Prediction Flow

```
User uploads CSV
    ↓
Streamlit reads/validates CSV
    ↓
Display preview (first 10 rows)
    ↓
User clicks "Run Predictions"
    ↓
predictions.py:make_prediction(df) [entire df, all rows]
    ↓
[Same as single, but vectorized for all rows]
    ↓
predictions = [results for each row]
    ↓
For each prediction:
    → Generate recommendations
    → Create result card
    → Add to display list
    ↓
Visualize rankings [bar chart by speed]
    ↓
Display all results [expandable sections]
```

---

## Module Interactions

### app.py (Main App)
```
Imports:
  - pandas (data handling)
  - streamlit (UI)
  - plotly (charts)
  - predictions (▼)
  - recommendations (▼)

Functions:
  - main() [entry point]
  - show_home() [tab 1]
  - show_csv_upload() [tab 2]
  - show_manual_form() [tab 3]
  - show_about() [tab 4]

Calls:
  - make_prediction(df)
  - get_recommendations(pet_data, pred, conf)
  - Plotly charts
```

### predictions.py
```
Imports:
  - pandas, numpy
  - sys, Path
  - StandardScaler (sklearn)
  - TabularFeatures (src.features_tabular)
  - model_loader (▼)

Classes:
  - AdoptionPredictor
    └─ __init__()
    └─ predict(df) → Dict
    └─ _align_features(df) → DataFrame

Functions:
  - make_prediction(df) → Dict

Constants:
  - ADOPTION_SPEED_LABELS {0-4: str}
  - ADOPTION_SPEED_EMOJI {0-4: emoji}
```

### model_loader.py
```
Imports:
  - pickle
  - Path

Classes:
  - ModelLoader (Singleton)
    └─ __new__()
    └─ load_model() → Dict
    └─ _find_model_path() → Path
    └─ get_features() → List
    └─ get_scaler() → StandardScaler
    └─ get_xgb_model() → XGBClassifier

Functions:
  - get_model_loader() → ModelLoader
```

### recommendations.py
```
Imports:
  - pandas, numpy
  - typing

Classes:
  - RecommendationEngine
    └─ __init__()
    └─ generate_recommendations() → List[Dict]
    └─ generate_summary() → str

Constants:
  - RECOMMENDATIONS {key: {title, description, tips, impact}}
  - Impact scores (PHOTO=0.95, DESCRIPTION=0.80, etc.)

Functions:
  - get_recommendations() → List[Dict]
  - get_recommendation_summary() → str
```

---

## State Management

### Session State (Streamlit)
```python
st.session_state manages:
  - Current tab/page
  - Uploaded file data
  - Form inputs (various)
  - Prediction results
  - Cached model (implicit)
```

### Model Caching (Singleton)
```python
ModelLoader._model stores:
  - Loaded XGBoost model (pickle)
  - StandardScaler
  - Feature list
  - Pipeline metadata

Loaded once, reused:
  - Faster predictions
  - Single source of truth
```

---

## Error Handling

### File Loading Errors
```
ModelLoader._find_model_path()
  → FileNotFoundError (model not found)
     Try multiple paths
     Return best match or raise

model_loader.load_model()
  → FileNotFoundError (if paths fail)
```

### Data Validation Errors
```
CSV Upload
  → File format errors (csv parsing)
  → Missing columns
  → Invalid data types
  → Display to user

Form Input
  → Streamlit handles validation
  → Type checking on inputs
```

### Prediction Errors
```
predictions.py:make_prediction()
  Try:
    → Feature engineering
    → Scaling
    → Model inference
  Except:
    → Return {'success': False, 'error': str(e)}
    → Display error to user
```

---

## Performance Optimization

### Model Loading
```
Singleton pattern:
  - Model loaded once
  - Reused for all predictions
  - No reload overhead
  - Saves ~2 seconds per prediction
```

### Feature Alignment
```
_align_features():
  - Check once during preprocessing
  - Add missing columns efficiently
  - Drop extra columns
  - Preserve order for model
```

### Visualization
```
Plotly charts:
  - Interactive (client-side rendering)
  - Zoom, pan, hover features
  - Minimal server load
  - Fast redraw
```

---

## Data Structures

### Prediction Result Dict
```python
{
    'success': bool,
    'predictions': [
        {
            'pet_index': int,
            'prediction': int (0-4),
            'prediction_label': str,
            'prediction_emoji': str,
            'confidence': float (0-1),
            'probabilities': {
                0: float,
                1: float,
                2: float,
                3: float,
                4: float
            },
            'original_data': Dict
        },
        ...
    ],
    'count': int,
    'error': str (if success=False)
}
```

### Recommendation Dict
```python
{
    'key': str,
    'title': str,
    'description': str,
    'tips': [str, str, str, ...],
    'impact': str,
    'impact_score': float
}
```

---

## Feature Engineering Pipeline

### Input Features (User provides)
```
Type, Name, Age, Breed1, Breed2, Gender, Color1, Color2, Color3,
MaturitySize, FurLength, Vaccinated, Dewormed, Sterilized, Health,
Quantity, Fee, State, VideoAmt, PhotoAmt, Description, PetID, RescuerID
```

### Processing (TabularFeatures)
```
1. Numeric encoding
2. Age binning
3. Description analysis
   - Word count
   - Character length
   - Sentiment (optional)
4. Categorical encoding
5. Feature combination
6. Missing value handling
```

### Output Features (Model uses)
```
27 engineered features:
  - 23 tabular features (numeric, binned, derived, encoded categoricals)
  - 4 VADER sentiment features (compound, positive, negative, neutral)
  - Text statistics
  - (Model expects specific 27 features: 23 tabular + 4 VADER)
```

---

## Dependencies Graph

```
frontend/app.py
  ├─ streamlit (UI)
  ├─ pandas (data)
  ├─ numpy (math)
  ├─ plotly (charts)
  ├─ frontend/utils/predictions.py
  │  ├─ pandas
  │  ├─ numpy
  │  ├─ scikit-learn (StandardScaler)
  │  ├─ src/features_tabular.py
  │  │  ├─ pandas
  │  │  ├─ numpy
  │  │  └─ [NLP libraries if sentiment enabled]
  │  └─ frontend/utils/model_loader.py
  │     ├─ pickle
  │     └─ Path (pathlib)
  └─ frontend/utils/recommendations.py
     ├─ pandas
     └─ numpy
```

---

## Configuration & Constants

### Model Parameters (Fixed)
```python
# XGBoost settings
n_estimators = 300
max_depth = 6
learning_rate = 0.1
subsample = 0.8
colsample_bytree = 0.8
objective = 'multi:softmax'
num_class = 5
random_state = 42
```

### Adoption Speed Classes
```python
{
    0: "Same day",
    1: "1-7 days",
    2: "8-30 days",
    3: "31-90 days",
    4: "No adoption"
}
```

### Recommendation Impact Scores
```python
PHOTO_IMPACT = 0.95       # Strongest
DESCRIPTION_IMPACT = 0.80
AGE_IMPACT = 0.75
FEE_IMPACT = 0.70
HEALTH_IMPACT = 0.65
```

---

## Extension Points

### To Add New Recommendation Category
```python
# In recommendations.py

RECOMMENDATIONS['new_category'] = {
    'title': '🎯 New Category',
    'description': 'What to improve',
    'tips': ['Tip 1', 'Tip 2', ...],
    'impact': 'HIGH/MEDIUM/LOW'
}

# Add check in generate_recommendations()
if pet_data.get('some_condition'):
    prioritized.append(('new_category', impact_score))
```

### To Add New Visualization
```python
# In app.py, show_csv_upload() or show_manual_form()

import plotly.graph_objects as go

fig = go.Figure(data=[...])
fig.update_layout(...)
st.plotly_chart(fig, use_container_width=True)
```

### To Change Model
```python
# Replace petadoption_pipeline.pkl with new model
# Must contain same features and classes
# Update config if feature names change
```

---

## Testing Strategy

### Unit Tests (For Future)
```
tests/
├─ test_model_loader.py
├─ test_predictions.py
├─ test_recommendations.py
└─ test_app.py
```

### Manual Testing (Current)
```
1. Single pet form → Check predictions
2. Batch CSV → Check rankings
3. Edge cases → Missing data, extreme values
4. Performance → Large batches, slow hardware
5. UI/UX → Button clicks, form validation
```

---

## Deployment Considerations

### Local Development
- ✅ No special setup needed
- Run: `streamlit run app.py`
- Single user, local machine

### Local Network Deployment
- Server IP: `streamlit run app.py --server.address 0.0.0.0`
- Access: `http://server-ip:8501`
- Multiple users on network

### Cloud Deployment
- Options: Streamlit Cloud, Docker, AWS, GCP, Azure
- Requires: Model file in accessible location
- Benefits: Scalable, always available

### Docker Containerization (Future)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r frontend/requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "frontend/app.py"]
```

---

## Security & Privacy

### Data Handling
- ✅ CSV data: Processed, not stored
- ✅ Form data: Used for prediction only
- ✅ Model: Loaded from local file
- ✅ No external API calls

### Model Inference
- ✅ Local processing
- ✅ No cloud dependencies
- ✅ No data sent anywhere
- ✅ User fully in control

---

## Future Architecture Enhancements

### Phase 2
- [ ] Database for storing results
- [ ] User authentication & accounts
- [ ] Batch job queuing
- [ ] API endpoint for programmatic access

### Phase 3
- [ ] Image quality analysis (CNN)
- [ ] Advanced NLP sentiment analysis
- [ ] Real-time model updating
- [ ] A/B testing framework

### Phase 4
- [ ] Mobile app
- [ ] Real-time collaboration
- [ ] Integration with adoption platforms
- [ ] Analytics dashboard

---

**Version:** 1.0.0  
**Architecture:** Modular, Scalable  
**Status:** ✅ Production Ready
