# 🐾 AdoptSense Frontend

A beautiful, user-friendly Streamlit application for predicting pet adoption speed and generating personalized improvement recommendations.

## 📋 Overview

**AdoptSense Frontend** is a web-based UI that allows users (shelter employees, rescuers, or pet owners) to:

1. Upload CSV files with multiple pets for batch analysis
2. Fill a form to analyze a single pet manually
3. Get AI-powered adoption speed predictions
4. Receive personalized, actionable recommendations
5. Compare and rank multiple pets side-by-side

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Saved model: `src/model/petadoption_pipeline.pkl`
- Parent project properly configured

### Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

The application will open in your default browser at `http://localhost:8501`

## 📁 Project Structure

```
frontend/
├── app.py                          # Main Streamlit application
├── pages/                          # Page modules (expandable for future features)
│   ├── __init__.py
│   └── (multi-page content in main app.py)
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── model_loader.py            # Load pickled XGBoost pipeline
│   ├── predictions.py             # Make adoption predictions
│   └── recommendations.py         # Generate recommendations
├── assets/                         # Static assets
│   └── sample_pets.csv            # Sample CSV file for batch upload reference
├── run_app.sh                      # Startup script for macOS/Linux
├── run_app.bat                     # Startup script for Windows
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🎯 Features

### 1. Home Tab
- Welcome page with project overview
- Adoption speed categories explained
- Quick links to features
- User guide

### 2. Batch Upload (CSV)
- Upload CSV with multiple pets
- Sample CSV download for reference
- Automatic feature engineering
- Real-time predictions for all pets
- Comparative ranking and visualization
- Individual recommendations for each pet

### 3. Single Pet Form
- Manual input form for one pet at a time
- 20+ fields covering pet characteristics (including breed selection from breed labels)
- Real-time validation
- Visual prediction with emoji indicators
- Detailed probability breakdown
- Description sentiment analysis (VADER-based)
- Top 5 factors helping and hindering adoption
- Interactive probability distribution chart

### 4. About Tab
- Project background
- Technical architecture
- Key insights from model
- Usage instructions
- Future enhancements

## 📊 Prediction Categories

| Speed | Emoji | Label | Timeline | Description |
|-------|-------|-------|----------|-------------|
| 0 | ⭐⭐⭐⭐⭐ | Same Day | Immediate | Exceptional appeal, instant adoption |
| 1 | ⭐⭐⭐⭐ | 1-7 Days | First Week | Strong demand, fast adoption |
| 2 | ⭐⭐⭐ | 8-30 Days | First Month | Moderate appeal, reasonable speed |
| 3 | ⭐⭐ | 31-90 Days | 2-3 Months | Needs improvement, slower adoption |
| 4 | ⭐ | No Adoption | 100+ Days | Critical interventions needed |

## 💡 Factor Analysis & Recommendations

The system evaluates each pet's profile and surfaces the top-5 **positive factors** (helping adoption) and top-5 **negative factors** (hindering adoption), ranked by importance weight. Factors are assessed across these areas:

| Category | Positive Signal | Negative Signal |
|----------|----------------|-----------------|
| **📸 Photos** | 5+ photos | 0-2 photos |
| **💰 Adoption Fee** | Free adoption | High or any fee |
| **🐣 Age** | ≤ 12 months | > 36 months |
| **🏥 Health** | Healthy | Minor/serious injury |
| **💉 Vaccinated** | Yes | No / Unknown |
| **🪱 Dewormed** | Yes | No / Unknown |
| **✂️ Sterilized** | Yes | No / Unknown |
| **✍️ Description** | 80+ words | < 20 words |
| **📐 Size** | Small | Large / Extra-large |
| **🔢 Quantity** | Single pet | Multiple pets |
| **🎥 Video** | Has video(s) | No video |

### Description Sentiment Analysis

Each pet's description is also analyzed using **VADER sentiment analysis** (via NLTK):
- Compound score from -1 (very negative) to +1 (very positive)
- Positive / Neutral / Negative proportion breakdown
- Tone label and actionable writing advice displayed in the UI

## 🔧 Configuration

### Model Loading

The app automatically searches for the model in these locations (in order):
1. `src/model/petadoption_pipeline.pkl`
2. `src/petadoption_pipeline.pkl`
3. Current working directory

### Feature Engineering

The app uses the `TabularFeatures` class from `src/features_tabular.py` to:
- Engineer numeric features
- Encode categorical variables
- Generate derived features
- Handle sentiment analysis (for descriptions)

### Scaling

Features are scaled using `StandardScaler` fitted on training data, stored in the model pipeline.

## 📄 CSV Format

For batch uploads, ensure your CSV includes these columns:

**Required:**
- `Type` (1=Dog, 2=Cat)
- `Age` (months)
- `Breed1`, `Breed2` (breed IDs)
- `Gender` (1=Male, 2=Female, 3=Mixed)
- `Color1`, `Color2`, `Color3` (color IDs)
- `MaturitySize` (0=N/A, 1=Small, 2=Medium, 3=Large, 4=XL)
- `FurLength` (0=N/A, 1=Short, 2=Medium, 3=Long)
- `Vaccinated`, `Dewormed`, `Sterilized` (1=Yes, 2=No, 3=Not Sure)
- `Health` (1=Healthy, 2=Minor Injury, 3=Serious Injury)
- `Quantity` (number of pets)
- `Fee` (adoption fee)
- `State` (Malaysian state ID, e.g. 41326 = Selangor)
- `PhotoAmt` (number of photos)
- `Description` (text)

**Optional:**
- `Name` (pet name)
- `VideoAmt` (number of videos)

## 🎨 UI Components

### Streamlit Features Used
- Multi-tab layout
- File uploader
- Form inputs (text, slider, select)
- Data tables with dataframe display
- Expandable sections
- Container styling
- Custom CSS
- Plotly charts
- Metrics display
- Status messages (success, error, warning, info)

### Visualizations
- Bar charts for prediction rankings
- Probability distribution charts
- Emoji-based status indicators
- Confidence score displays
- Comparative analysis tables

## 🔐 Data Privacy

- No data stored on servers
- All processing is local
- One-time network call on first run to download the NLTK `vader_lexicon` (~1 MB); cached locally afterwards
- Model executes in user's Python environment
- CSV/form data only used for predictions during session

## ⚙️ Performance

- **Cold start:** ~3-5 seconds (model loading)
- **Single prediction:** ~0.5-1 second
- **Batch predictions:** ~0.1 seconds per pet
- **Memory footprint:** ~150-200 MB (model + data)

## 🐛 Troubleshooting

### Model Not Found
```
Error: Model file not found
```
**Solution:** Ensure `src/model/petadoption_pipeline.pkl` exists. Run the training notebook first.

### Import Errors
```
ModuleNotFoundError: No module named 'src'
```
**Solution:** Run from project root directory, or ensure `PYTHONPATH` includes the project root.

### Out of Memory
```
MemoryError
```
**Solution:** Split large CSV files into smaller batches (500-1000 pets per file).

### Streamlit Not Starting
```
StreamlitAPIException
```
**Solution:** 
1. Clear Streamlit cache: `streamlit cache clear`
2. Kill any running Streamlit processes
3. Try again

## 🚀 Running the App

### Option 1: Startup Script (macOS/Linux)
```bash
cd frontend
bash run_app.sh
```
Automatically activates the virtual environment (if present at `../.venv`) and starts the app.

### Option 2: Startup Script (Windows)
```batch
cd frontend
run_app.bat
```
Automatically activates the virtual environment (if present at `..\\.venv`) and starts the app.

### Option 3: From Project Root
```bash
streamlit run frontend/app.py
```

### Option 4: From Frontend Directory
```bash
cd frontend
streamlit run app.py
```

### Option 5: With Custom Port
```bash
streamlit run app.py --server.port 8502
```

### Option 6: With Custom Settings
```bash
streamlit run app.py \
  --server.headless true \
  --browser.gatherUsageStats false \
  --logger.level=error
```

## 📊 Model Architecture

```
Raw Pet Data
     ↓
Feature Engineering (TabularFeatures)
     ↓
Preprocessing & Scaling (StandardScaler)
     ↓
XGBoost Classifier (300 estimators)
     ↓
Probability Predictions
     ↓
Recommendations Engine
     ↓
UI Display & Visualization
```

## 🔄 Data Flow

1. **Input** → User uploads CSV or fills form
2. **Parsing** → Data validated and parsed
3. **Engineering** → 37 features extracted/engineered (27 tabular + 10 sentiment features)
4. **Scaling** → Numeric features standardized
5. **Prediction** → XGBoost generates adoption speed + probabilities
6. **Sentiment** → VADER analyzes description tone (compound, pos/neu/neg scores)
7. **Factor Analysis** → Top-5 positive and top-5 negative adoption factors identified
8. **Visualization** → Results displayed with charts and metrics
9. **Export** → Results can be exported as CSV (future feature)

## 📦 Dependencies

Core dependencies:
- `streamlit` - Web app framework
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scikit-learn` - Preprocessing (StandardScaler)
- `xgboost` - Model inference
- `plotly` - Interactive charts
- `nltk` - VADER sentiment analysis for pet descriptions
- `certifi` - SSL certificate bundle for NLTK lexicon download

See `requirements.txt` for exact versions.

## 🎓 Example Usage

### Batch Prediction
```
1. Download sample CSV from "Batch Upload" tab
2. Add your pet data (multiple rows)
3. Upload CSV
4. Click "Run Predictions"
5. View rankings and recommendations
```

### Single Pet Analysis
```
1. Fill form with pet details
2. Click "Get Prediction & Recommendations"
3. View adoption speed prediction
4. Read personalized recommendations
5. Act on top 3 suggestions
```

## 📈 Future Enhancements

- [ ] Image quality analysis (CNN)
- [ ] Export recommendations as PDF
- [ ] Historical comparison tracking
- [ ] Batch optimization suggestions
- [ ] Integration with adoption platforms
- [ ] Real-time model updates
- [ ] A/B testing framework
- [ ] User analytics dashboard
- [ ] Mobile-responsive redesign

## 📝 License

Part of AdoptSense Pet Adoption Prediction project.

## 👥 Contributing

To add features or improvements:
1. Create feature branch
2. Implement changes
3. Test thoroughly
4. Submit pull request

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review model output in browser console
- Check terminal output for Python errors
- Verify data format against CSV schema

---

**Version:** 1.0.0  
**Last Updated:** February 2026  
**Status:** Production Ready ✅
