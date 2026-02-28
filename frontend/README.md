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
├── assets/                         # Static assets (images, custom CSS)
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
- 20+ fields covering pet characteristics
- Real-time validation
- Visual prediction with emoji indicators
- Detailed probability breakdown
- Top 3 personalized recommendations
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

## 💡 Recommendations

The system generates personalized recommendations in six categories:

1. **📸 Photography Campaign** (CRITICAL Impact)
   - Minimum 3-5 high-quality photos
   - No photos = 60%+ slow adoption
   - Multiple angles, clear focus

2. **✍️ Description Enhancement** (HIGH Impact)
   - Warm, detailed descriptions
   - Personality-focused content
   - 50+ words recommended
   - Emotional connection

3. **💰 Pricing Strategy** (HIGH Impact)
   - Free/low-cost incentives
   - Fee is a barrier for slow categories
   - Deposit models
   - Value communication

4. **🐣 Age-Targeted Outreach** (MEDIUM Impact)
   - Youth-focused marketing for puppies/kittens
   - Senior pet programs
   - Specific promotional strategies

5. **🏥 Health Transparency** (MEDIUM Impact)
   - Clear health status communication
   - Medical history documentation
   - Recovery care timelines
   - Trust building

6. **🔒 Sterilization Strategy** (LOW-MEDIUM Impact)
   - Benefits communication
   - Part of adoption package
   - Responsible ownership angle

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
- `MaturitySize` (0-4)
- `FurLength` (0-3)
- `Vaccinated`, `Dewormed`, `Sterilized` (1-3)
- `Health` (1-3)
- `Quantity` (number)
- `Fee` (adoption fee)
- `State` (state ID)
- `PhotoAmt` (number of photos)
- `Description` (text)
- `PetID` (unique ID)
- `RescuerID` (rescuer ID)

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
- No external API calls (except Streamlit)
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

### Option 1: From Project Root
```bash
streamlit run frontend/app.py
```

### Option 2: From Frontend Directory
```bash
cd frontend
streamlit run app.py
```

### Option 3: With Custom Port
```bash
streamlit run app.py --server.port 8502
```

### Option 4: With Custom Settings
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
3. **Engineering** → 20+ features extracted/engineered
4. **Scaling** → Numeric features standardized
5. **Prediction** → XGBoost generates adoption speed + probabilities
6. **Recommendations** → Decision rules generate 3-6 suggestions
7. **Visualization** → Results displayed with charts and metrics
8. **Export** → Results can be exported as CSV (future feature)

## 📦 Dependencies

Core dependencies:
- `streamlit` - Web app framework
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scikit-learn` - Preprocessing (StandardScaler)
- `xgboost` - Model inference
- `plotly` - Interactive charts

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
- [ ] Real-time sentiment analysis
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
