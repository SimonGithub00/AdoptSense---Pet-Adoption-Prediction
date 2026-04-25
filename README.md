# AdoptSense — Pet Adoption Speed Prediction & Marketplace

End-to-end machine learning platform combining XGBoost adoption speed prediction with a two-sided pet adoption marketplace. Built on the Kaggle PetFinder.my dataset, it powers a Streamlit frontend featuring prediction analytics, KPI tracking, and role-based marketplace for shelters, private owners, and adopters.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Findings](#key-findings)
- [Model](#model)
- [Feature Engineering](#feature-engineering)
- [Sentiment Analysis](#sentiment-analysis)
- [Marketplace Platform](#marketplace-platform)
- [KPI System](#kpi-system)
- [Notebook Structure](#notebook-structure)
- [Source Modules](#source-modules)
- [Frontend Features](#frontend-features)
- [Pipeline Artifact](#pipeline-artifact)
- [Project Structure](#project-structure)
- [Data Setup](#data-setup)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)

---

## Project Overview

AdoptSense trains an XGBoost multi-class classifier on ~15,000 labelled pet listings to predict one of five adoption speed classes:

| Class | Label | Meaning |
|---|---|---|
| 0 | Same day | Adopted on the day of listing |
| 1 | 1-7 days | Adopted within the first week |
| 2 | 8-30 days | Adopted within the first month |
| 3 | 31-90 days | Adopted within three months |
| 4 | No adoption | Not adopted after 100 days |

The notebook (`src/petadoption_run.ipynb`) covers the full analytical pipeline from EDA through to a saved, production-ready pickle. The test set from Kaggle contains no labels and is not used for evaluation; all validation is done on a stratified hold-out split of the labelled training data.

---

## Key Findings

From the EDA and model feature importance:

- **Photos are the single strongest factor.** Listings with no photos have a 60%+ probability of Speed 4 (no adoption). The effect plateaus after 3 to 5 photos.
- **Age drives adoption speed more than any other numeric feature.** Puppies and kittens (1 to 3 months) adopt fastest; pets over two years adopt significantly slower.
- **Fee is a barrier.** Free adoptions skew strongly toward faster speeds.
- **All linear correlations with AdoptionSpeed are below 0.10**, confirming that a non-linear tree-based model is the right choice.
- **Description sentiment matters.** Listings with a more positive tone tend toward faster adoption, even after controlling for other features.
- **Health and sterilisation** show counterintuitive patterns: listings marked as healthy dominate the dataset (low discriminative power), and non-sterilised pets show faster adoption in the data.
- **Geography:** Selangor and Kuala Lumpur account for ~85% of listings; Pahang and Johor adopt faster than average.

---

## Model

**Algorithm:** XGBoost multi-class classifier (`multi:softmax`, 5 classes)

**Hyperparameters:**

| Parameter | Value |
|---|---|
| `n_estimators` | 300 |
| `max_depth` | 6 |
| `learning_rate` | 0.1 |
| `subsample` | 0.8 |
| `colsample_bytree` | 0.8 |
| `random_state` | 42 |

**Validation metrics (Section 3.1 output):**

| Metric | Value |
|---|---|
| Accuracy | 0.3991 |
| Macro F1 | 0.3461 |
| Weighted F1 | 0.3877 |
| Macro Precision | 0.4738 |
| Macro Recall | 0.3362 |

**Evaluation metrics:** Accuracy, Macro F1, Weighted F1, Macro Precision, Macro Recall, per-class F1, ROC curves (one-vs-rest), Precision-Recall curves, confusion matrices.

Macro F1 is used as the primary selection metric because it weights all five classes equally, penalising poor performance on minority classes (especially Speed 0, which represents only 2.7% of the data). Class weights are applied during training to partially counteract the imbalance.

**Validation:** Stratified train/validation split (80/20). Stratification preserves the class distribution in both sets, giving a reliable generalisation estimate without access to labelled test data.

---

## Feature Engineering

`TabularFeatures` (`src/features_tabular.py`) produces 27 features from the raw listing DataFrame. In the notebook run captured in `src/petadoption_run.ipynb`, an additional 10 Google NLP JSON sentiment features are appended during modeling, producing a 37-column analytical matrix. All features are integer-encoded; the StandardScaler is applied to numeric columns selected from that matrix (scaling has no effect on XGBoost predictions since tree-based models are scale-invariant).

**Structural features (23):**

| Group | Features |
|---|---|
| Raw numerics | `Age`, `PhotoAmt`, `Fee`, `VideoAmt`, `Quantity` |
| Binary flags | `has_photo`, `has_video`, `is_free`, `has_name` |
| Ordinal bins | `age_bin`, `photo_bin`, `desc_bin` |
| Description | `desc_word_count` |
| Categoricals | `Type`, `Gender`, `MaturitySize`, `FurLength`, `Vaccinated`, `Dewormed`, `Sterilized`, `Health`, `Color1`, `State` |

**VADER sentiment features (4):**

Computed inline from the `Description` string by `TabularFeatures` using the NLTK VADER lexicon — offline, instant, no API required:

| Feature | Description |
|---|---|
| `sentiment_compound` | Overall polarity score (-1 to +1) |
| `sentiment_pos` | Fraction of text with positive tone |
| `sentiment_neg` | Fraction of text with negative tone |
| `sentiment_neu` | Fraction of text with neutral tone |

---

## Sentiment Analysis

Two sentiment approaches were evaluated in the notebook. The final pipeline uses VADER.

### Google NLP JSON (analytical only)

The Kaggle dataset includes pre-computed Google Cloud Natural Language API JSON files for 96.3% of training pets (14,442 out of 14,993). These provide 10 richer features: document score, document magnitude, sentence-level ratios, entity count, and entity salience.

Section 3.4 of the notebook uses these features for an ablation test (27-feature baseline vs 37-feature enhanced), confirming they add signal:

| Metric | Baseline (27) | Enhanced (+JSON, 37) | Delta |
|---|---:|---:|---:|
| Accuracy | 0.3931 | 0.3991 | +0.0060 |
| Macro F1 | 0.3314 | 0.3461 | +0.0147 |
| Weighted F1 | 0.3809 | 0.3877 | +0.0068 |
| Macro Precision | 0.4115 | 0.4738 | +0.0623 |
| Macro Recall | 0.3263 | 0.3362 | +0.0099 |

Section 3.5 then runs a direct head-to-head comparison against VADER-only features.

### VADER (deployed pipeline)

In the head-to-head test (Section 3.5 output), VADER and Google NLP JSON trade off metrics:

| Approach | Feature Count | Accuracy | Macro F1 | Weighted F1 | Macro Precision | Macro Recall |
|---|---:|---:|---:|---:|---:|---:|
| VADER-only | 27 | 0.3931 | 0.3314 | 0.3809 | 0.4115 | 0.3263 |
| Google NLP JSON-only | 33 | 0.3995 | 0.3304 | 0.3879 | 0.4005 | 0.3278 |

VADER was selected by Macro F1 in that comparison and for the deployment practicality reason: Google NLP JSON files exist only for the training corpus. For new frontend listings, no pre-computed JSON exists. The alternatives are calling Google Cloud NLP at inference time (latency, cost, external dependency) or zero-filling JSON features (discarding the intended signal). VADER is computed directly from the description string - offline, fast, and reproducible in production.

---

## Marketplace Platform

### Overview

AdoptSense now includes a **complete two-sided pet adoption marketplace** with role-based interfaces for three user types:

| User Type | Role | Key Features |
|-----------|------|--------------|
| **Adopters** 🐕 | Pet seekers | Browse, filter, save to watchlist, message sellers |
| **Shelters** 🏥 | Organizations | Manage inventory, create listings, view KPIs & analytics |
| **Private Owners** 👨‍👩‍👧 | Individuals | List personal pets, track adoption, get recommendations |

### Architecture

```
AdoptSense Platform (Unified)
    ├─ Prediction Engine
    │   └─ XGBoost + Feature Engineering + VADER Sentiment
    │
    ├─ Marketplace Tab (5 tabs total)
    │   ├─ For Adopters:
    │   │   ├─ Browse Pets (with filters)
    │   │   ├─ Watchlist (favorites)
    │   │   ├─ Messages (interface placeholder)
    │   │   └─ Dashboard (adoption tracking)
    │   │
    │   ├─ For Shelters:
    │   │   ├─ My Listings (inventory management)
    │   │   ├─ Create Listing (with AI prediction preview)
    │   │   ├─ KPIs (adoption trends, rates, metrics)
    │   │   └─ Messages (bulk inquiries)
    │   │
    │   └─ For Private Owners:
    │       ├─ My Listings (personal pets)
    │       ├─ Create Listing (simplified form)
    │       ├─ Analytics (performance tracking)
    │       └─ Watchlist (monitor adoption trends)
    │
    └─ KPI Tracking System
        ├─ Listing-level metrics
        ├─ Organization-level aggregation
        └─ Real-time calculation & dashboards
```

### Marketplace Features

#### 🔍 Pet Discovery
- **Browse Interface**: Filterable, sortable pet listings
- **Smart Filters**: Pet type, adoption speed, location
- **Listing Cards**: Visual adoption speed badges with confidence scores
- **AI Recommendations**: Suggests high-likelihood matches

#### ➕ Listing Creation
- **Smart Forms**: Separate forms for shelters vs. private owners
- **AI Preview**: Get adoption speed prediction before publishing
- **Recommendations**: AI-driven suggestions to improve adoption (photos, fee, description, etc.)
- **Photo Support**: Upload multiple pet photos for better visibility

#### 📊 Performance Dashboards
- **Real-time Metrics**: Views, contacts, matches, adoption time
- **KPI Charts**: Adoption trends, speed distribution, historical data
- **Status Tracking**: Monitor listing progress through adoption funnel
- **Performance Analytics**: Length-of-stay, adoption rates, contact rates

#### ❤️ Watchlist & Favorites
- **Save Pets**: Add interesting listings to personal watchlist
- **Quick Actions**: Message sellers, view details, track progress
- **Status Updates**: Notified when saved pets are adopted

#### 💬 Messaging (Framework Ready)
- **Direct Communication**: Message interface for adopter-seller interaction
- **Shelter Bulk Messaging**: Future support for high-volume inquiries
- **Message History**: Track all communications

### Data Models

Three new utility modules power the marketplace:

**`frontend/utils/matching_platform.py`** - Core Engine
- `UserProfile`: Manages shelters, owners, adopters with verification
- `PetListing`: Complete listing with AI predictions & confidence scores
- `PetMatch`: Compatibility matching between pets and adopters
- `ListingKPI` & `ShelterKPI`: Performance tracking at listing & org levels
- `MatchingPlatformDataStore`: In-memory data management (ready for PostgreSQL)
- `RecommendationEngine`: AI-powered improvement suggestions

**`frontend/utils/matching_platform_ui.py`** - Streamlit Interface
- `MatchingPlatformUI`: Main class with all UI components
- Role-based navigation (3 distinct user experiences)
- Browse, create, manage, and track adoptions
- Interactive dashboards with Plotly charts
- Sample data included for testing

### Integration with Prediction Model

The marketplace seamlessly integrates your XGBoost model:

```
User Creates Listing
    ↓
Form Data → TabularFeatures (27 structural + 4 sentiment)
    ↓
Sentiment Analysis (VADER)
    ↓
XGBoost Prediction (0-4 speed scale)
    ↓
Display Adoption Speed + Confidence
    ↓
Generate AI Recommendations
```

**No changes to existing prediction pipeline!** The model is fully compatible.

### Quick Start: Testing the Marketplace

1. **Launch the app:**
   ```bash
   streamlit run frontend/app.py
   ```

2. **Click the "🤝 Marketplace" tab** (it's the 4th tab)

3. **Select your role** (Sidebar):
   - Adopter: Browse pets
   - Shelter Manager: Manage inventory
   - Private Owner: List personal pets

4. **Explore features:**
   - **Adopter**: Browse 3 sample listings, filter by speed, add to watchlist
   - **Shelter**: See listing management, create new with AI preview, view KPIs
   - **Owner**: Same as shelter but optimized for individuals

### Future Marketplace Features (Roadmap)

**Phase 3: Production Infrastructure**
- [ ] Database persistence (PostgreSQL)
- [ ] User authentication & registration
- [ ] Geographic features (maps, location-based discovery)
- [ ] Photo upload & storage (AWS S3)

**Phase 4: Advanced Features**
- [ ] Real messaging system
- [ ] Photo enhancement AI (professional backgrounds, filters)
- [ ] Digital stickers (shareable pet avatars)
- [ ] Weekly shelter reports (email summaries)

**Phase 5: Revenue Streams**
- [ ] Listing prioritization (paid feature)
- [ ] Featured listings (premium placement)
- [ ] Partner advertising network
- [ ] Premium analytics reports

---

## KPI System

### Overview

The matching platform tracks comprehensive business metrics at both listing and organizational levels to measure adoption sustainability and platform success.

### Main KPIs Implemented

✅ **Listing-Level Metrics**
- **Views**: Number of times a listing was viewed
- **Contacts**: How many interested adopters reached out
- **Matches**: AI-generated compatibility scores
- **Adoption Time**: Days from listing creation to adoption
- **Contact Rate**: (Contacts / Views) × 100%

✅ **Organization-Level Metrics**
- **Total Listings**: All pets ever listed by organization
- **Active Listings**: Currently available for adoption
- **Adopted Count**: Successfully adopted pets
- **Adoption Rate**: (Adopted / Total) × 100%
- **Average Adoption Speed**: Mean adoption speed (0-4 scale)
- **Average Length-of-Stay**: Average days in shelter before adoption
- **Average Views Per Listing**: Total engagement metric
- **Contact Rate**: Organization-wide interest metric
- **Reinsertion Rate**: % of pets re-entering after adoption (framework)
- **User Satisfaction**: Average Likert scale feedback 1-5 (framework)

### KPI Calculation Logic

#### When a Listing is Created
```python
PetListing created with:
  - adoption_speed_pred: AI prediction (0-4)
  - adoption_speed_confidence: Model confidence (0-1)
  - created_at: timestamp

ListingKPI initialized:
  - views: 0
  - contacts: 0
  - adoption_time_days: None (null until adopted)
```

#### During Listing Lifecycle
```python
# Each view increments counter
listing_kpi.views += 1
listing_kpi.last_view_at = now

# Each contact increments counter
listing_kpi.contacts += 1

# AI can generate matches
listing_kpi.matches += 1
```

#### When Pet is Adopted
```python
# Record adoption with actual speed
datastore.record_adoption(
    listing_id="unique_id",
    adoption_speed_actual=1  # How fast it actually adopted
)

# Automatic calculations:
adoption_days = (adopted_date - created_date).days
listing_kpi.adoption_time_days = adoption_days

# Organization KPIs auto-updated:
shelter_kpi.adopted_count += 1
shelter_kpi.active_listings -= 1

# Recalculate all averages:
avg_los = sum(adoption_days) / count(adoptions)
avg_speed = sum(adoption_speeds) / count(adoptions)
adoption_rate = adopted_count / total_listings
```

### Example: End-to-End KPI Tracking

```
Day 0: Shelter lists "Max" (dog, 12mo, $50, 4 photos)
  ├─ Prediction: Speed 0 (same day), confidence 85%
  └─ KPI: total_listings=1, active_listings=1

Days 1-5: Adopters browse marketplace
  ├─ Day 1: 5 views → listing_kpi.views=5
  ├─ Day 2: 2 views, 1 contact → views=7, contacts=1
  ├─ Day 3: 3 views, 2 contacts → views=10, contacts=3
  └─ Day 5: 1 view, 1 match → views=11, matches=1

Day 6: Pet is adopted
  ├─ Status: ADOPTED
  ├─ Adoption time: 6 days
  ├─ Actual speed: 0 (matched prediction!) ✓
  │
  └─ Final KPIs:
      ├─ Listing: views=11, contacts=3 (27% contact rate), adoption_time=6
      ├─ Shelter: adopted=1, adoption_rate=100%, avg_los=6 days
      └─ Prediction Accuracy: Predicted=0, Actual=0 → Perfect!
```

### Dashboard Display

The KPI dashboard shows:
- **Summary Cards**: Key metrics at a glance (total, adopted, adoption rate, avg LOS)
- **Adoption Timeline**: 30-day trend chart showing daily adoption rate
- **Speed Distribution**: Histogram of adoption speeds across all listings
- **Detailed Stats Table**: Breakdowns of each metric
- **Expandable Details**: Click to drill into specific metrics

### Integration with Business Logic

**Metrics Inform Pricing:**
- Organizations with low contact rates → Recommend paid photo enhancement
- Organizations with high adoption rates → Unlock premium features or discounts
- Long average LOS → Recommend paid listing prioritization
- High adoption success → Performance bonus on next listing

### Future Enhancements

**Reinsertion Rate Tracking** (Phase 2)
```python
Track when pets re-enter system after adoption:
- Track reason: returned, lost, owner change, etc.
- Days in household before reinsertion
- Correlation with adoption speed
```

**User Satisfaction** (Phase 2)
```python
Post-adoption feedback (Likert 1-5):
- Adopter satisfaction with pet match
- Pet health/happiness after adoption
- Would recommend platform? Yes/No
- Calculate avg_satisfaction and recommendation_rate
```

### Database Schema (Ready to Implement)

```sql
CREATE TABLE listings (
    listing_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    pet_name TEXT NOT NULL,
    adoption_speed_pred INT,
    adoption_speed_confidence FLOAT,
    status VARCHAR(20),
    created_at TIMESTAMP,
    adopted_at TIMESTAMP,
    adoption_speed_actual INT
);

CREATE TABLE listing_kpis (
    listing_id TEXT PRIMARY KEY,
    views INT DEFAULT 0,
    contacts INT DEFAULT 0,
    matches INT DEFAULT 0,
    adoption_time_days INT,
    last_view_at TIMESTAMP
);

CREATE TABLE shelter_kpis (
    user_id TEXT PRIMARY KEY,
    total_listings INT,
    adopted_count INT,
    avg_adoption_speed FLOAT,
    avg_length_of_stay_days FLOAT,
    adoption_rate FLOAT,
    contact_rate FLOAT,
    updated_at TIMESTAMP
);
```

---

## Notebook Structure

`src/petadoption_run.ipynb`

| Section | Content |
|---|---|
| **0. Setup and Data Loading** | Config, CSV loading, label maps, Google NLP JSON merge |
| **1. EDA** | General overview, target distribution, pet characteristics, health, listing quality, geography, correlation summary, sentiment EDA (JSON), key takeaways |
| **2. Predictive Modeling** | Feature engineering (VADER + tabular), JSON feature append, train/validation split, StandardScaler, XGBoost training |
| **3.1 Metric Choice** | Justification for Macro F1 as primary metric |
| **3.2 Model Comparison** | Metrics table, bar plot, confusion matrices, ROC curves, Precision-Recall curves |
| **3.3 Feature Importance** | Top 20 XGBoost feature importances |
| **3.4 JSON Sentiment Feature Impact** | Ablation output: enhanced model improves all tracked metrics vs baseline (Macro F1 +0.0147) |
| **3.5 Performance Test: Sentiment Approaches** | Head-to-head output: VADER wins Macro F1 (0.3314 vs 0.3304), JSON wins Accuracy (0.3995 vs 0.3931), deployment decision remains VADER |
| **4. Save Model Pipeline** | Pipeline dict creation, pickle export, summary text file |
| **5. Drivers and Recommendations** | Top feature drivers, strategic actions for adoption centers |

---

## Source Modules

### `src/config.py`

Frozen dataclass holding all filesystem paths and training constants. Import once and pass `cfg` through the notebook:

```python
from src.config import Config
cfg = Config()
```

Key constants: `RANDOM_STATE = 42`, `TEST_SIZE = 0.2`, `TARGET_COL = "AdoptionSpeed"`.

### `src/features_tabular.py`

`TabularFeatures` — stateless feature transformer. Handles missing value imputation, binary flag creation, ordinal binning, and VADER sentiment scoring. No fit step; safe to reuse across train, validation, and inference.

```python
from src.features_tabular import TabularFeatures
fe = TabularFeatures()
X = fe.feature_engineering_tabular(df)   # returns 27-column DataFrame
```

### `src/features_sentiment.py`

`SentimentFeatures` — loads Google NLP JSON files for the training corpus. Used analytically in the notebook (Sections 3.4 and 3.5) but not included in the deployed pipeline.

```python
from src.features_sentiment import SentimentFeatures, SENTIMENT_FEATURE_COLS
sf = SentimentFeatures(cfg.TRAIN_SENTIMENT_DIR)
sent_df = sf.load_for_ids(df["PetID"])
df = df.merge(sent_df, on="PetID", how="left")
```

### `src/features_text.py`

Stub module reserved for future transformer-based or TF-IDF text features. Current description sentiment is handled by VADER inside `TabularFeatures`.

### `src/features_image_meta.py`

Stub module reserved for image quality or metadata features (CNNs, image scoring). Not used in the current pipeline.

### `frontend/utils/matching_platform.py`

Core marketplace engine with data models:
- `UserProfile`: User account management
- `PetListing`: Pet listings with predictions
- `ListingKPI` & `ShelterKPI`: KPI tracking
- `MatchingPlatformDataStore`: Data management
- `RecommendationEngine`: AI suggestions

### `frontend/utils/matching_platform_ui.py`

Streamlit UI components:
- `MatchingPlatformUI`: Main UI class
- Browse interface with filters
- Listing creation forms
- KPI dashboards
- Watchlist management
- Role-based navigation

---

## Frontend Features

The Streamlit application now includes 5 tabs:

| Tab | Purpose | Audience |
|-----|---------|----------|
| 📊 Home | Landing page & feature overview | All users |
| 📁 Batch Upload | Predict speeds for multiple pets via CSV | Shelters, analysts |
| 📝 Single Pet Form | Single pet prediction & recommendations | Individuals |
| 🤝 **Marketplace** | Two-sided marketplace for adoption | All users |
| ℹ️ About | Project documentation & methodology | All users |

### Tab: 🤝 Marketplace

**For Adopters:**
- Browse available pets with smart filters
- Filter by pet type (dogs/cats) and adoption speed
- Save favorites to watchlist
- Send messages to sellers
- Track adoption progress

**For Shelters:**
- View and manage pet inventory
- Create new listings with AI prediction preview
- See actionable recommendations to improve adoption
- Monitor KPI dashboard (adoption trends, rates, metrics)
- Respond to adoption inquiries

**For Private Owners:**
- List personal pets with same AI analysis
- Get recommendations to improve adoption chances
- Track individual listing performance
- Monitor adoption progress

---

## Pipeline Artifact

Saved to `src/model/petadoption_pipeline.pkl` after running the notebook. Load with:

```python
import pickle, sys
sys.path.insert(0, ".")   # project root on path
pipeline = pickle.load(open("src/model/petadoption_pipeline.pkl", "rb"))
```

Contents:

| Key | Type | Description |
|---|---|---|
| `scaler` | `StandardScaler` | Fitted from the selected feature matrix used in the notebook run |
| `model` | `XGBClassifier` | Trained XGBoost (300 estimators) |
| `feature_columns` | `list[str]` | Ordered feature-name schema stored by the notebook output (37 in current run) |
| `numeric_features` | `list[str]` | Numeric columns persisted alongside the model (37 in current run output) |
| `target_classes` | `list[int]` | `[0, 1, 2, 3, 4]` |
| `feature_engineering_class` | `type` | `TabularFeatures` |
| `sentiment_approach` | `str` | `"VADER"` |
| `sentiment_feature_class` | `None` | VADER is inline; no separate class needed |
| `sentiment_feature_cols` | `list` | `[]` (no Google NLP JSON in pipeline) |

A human-readable summary is also written to `src/model/pipeline_summary.txt`.

---

## Project Structure

```
AdoptSense-Pet-Adoption-Prediction/
├── README.md                        # This file - comprehensive documentation
├── requirements.txt
├── LICENSE
├── data/                            # gitignored — Kaggle files stay local
│   ├── train/
│   │   ├── train.csv                # 14,993 labelled pet listings
│   │   ├── train_images/
│   │   ├── train_metadata/
│   │   └── train_sentiment/         # Google NLP JSON files
│   ├── test/                        # no AdoptionSpeed labels — not used for eval
│   ├── breed_labels.csv
│   ├── color_labels.csv
│   └── state_labels.csv
├── src/
│   ├── config.py                    # Central config (paths, constants)
│   ├── features_tabular.py          # TabularFeatures + VADER sentiment
│   ├── features_sentiment.py        # SentimentFeatures (Google NLP JSON)
│   ├── features_text.py             # Stub for future text features
│   ├── features_image_meta.py       # Stub for future image features
│   ├── petadoption_run.ipynb        # Full analytical and training notebook
│   └── model/
│       ├── petadoption_pipeline.pkl # Saved pipeline (scaler + XGBoost)
│       └── pipeline_summary.txt     # Human-readable pipeline metadata
└── frontend/
    ├── app.py                       # Streamlit application (5 tabs)
    ├── requirements.txt
    ├── run_app.bat
    ├── run_app.sh
    ├── assets/                      # Static assets
    └── utils/
        ├── model_loader.py          # Singleton pipeline loader
        ├── predictions.py           # AdoptionPredictor, feature alignment
        ├── recommendations.py       # Rule-based adoption factor analysis
        ├── matching_platform.py     # Marketplace core engine ← NEW
        └── matching_platform_ui.py  # Marketplace Streamlit UI ← NEW
```

---

## Data Setup

Download the dataset from the [PetFinder.my Kaggle competition](https://www.kaggle.com/c/petfinder-adoption-prediction) and place the files as shown below. Do not commit anything under `data/`.

```
data/
├── train/
│   ├── train.csv
│   ├── train_images/
│   ├── train_metadata/
│   └── train_sentiment/      # required for Sections 3.4 and 3.5 of the notebook
├── test/
│   ├── test.csv
│   └── ...
├── breed_labels.csv
├── color_labels.csv
└── state_labels.csv
```

The `train_sentiment/` directory is needed for the Google NLP JSON analytical sections. Without it, those sections are skipped gracefully and the VADER-based pipeline (Sections 2 onwards) runs without issue.

---

## Setup and Installation

**1. Clone and open**

```bash
git clone https://github.com/<your-username>/AdoptSense-Pet-Adoption-Prediction.git
cd AdoptSense-Pet-Adoption-Prediction
code .
```

**2. Create a virtual environment**

```bash
python -m venv .venv
```

Activate:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

**3. Install dependencies (both backend and frontend)**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Run the notebook (optional as model will be retrained)**

```bash
jupyter notebook src/petadoption_run.ipynb
```

Run all cells top to bottom. The pipeline pickle is written to `src/model/` at Section 4.

**5. Launch the Streamlit application**

```bash
streamlit run frontend/app.py
```

The application opens in your default browser with 5 tabs:
- **📊 Home**: Feature overview and adoption speed categories
- **📁 Batch Upload**: CSV prediction for multiple pets
- **📝 Single Pet Form**: Individual pet prediction & recommendations
- **🤝 Marketplace**: Two-sided adoption platform
- **ℹ️ About**: Project documentation

---

## Using the Marketplace

### Getting Started

1. Click the **"🤝 Marketplace"** tab in the Streamlit app
2. Select your role in the sidebar (Adopter, Shelter Manager, or Private Owner)
3. Choose the corresponding tab to explore features for your role

### For Adopters 🐕

1. Go to **"🔍 Browse Pets"**
2. Filter by pet type (dogs/cats) and adoption speed
3. Sort results by preference
4. Click **"❤️ Save"** to add to watchlist
5. Click **"💬 Message"** to contact the seller
6. Visit **"❤️ Watchlist"** to manage saved pets

### For Shelters 🏥

1. Go to **"📋 My Listings"** to see your inventory
2. Go to **"➕ Create Listing"** to add new pets:
   - Fill in pet details (name, age, health status, etc.)
   - Upload photos
   - Get AI adoption speed prediction before publishing
   - Read recommendations to optimize listing
3. Go to **"📊 KPIs"** to view analytics:
   - Adoption trends (30-day chart)
   - Speed distribution (histogram)
   - Key metrics (adoption rate, length-of-stay, etc.)
   - Mark pets as adopted to update metrics

### For Private Owners 👨‍👩‍👧

Same features as shelters but optimized for individual pet listings:
- Simplified form for 1-few pets
- Personal adoption story emphasis
- Individual listing performance tracking

### Sample Data

The marketplace includes 3 demo listings:
- **Max** (Dog) - Speed 0 (⭐⭐⭐⭐⭐ Same day)
- **Whiskers** (Cat) - Speed 1 (⭐⭐⭐⭐ 1-7 days)
- **Luna** (Cat) - Speed 3 (⭐⭐ 31-90 days)

Test different filters to see how the search and discovery works!

---

## Technical Architecture

### Current Implementation

- **Backend**: XGBoost model with feature engineering
- **Database**: In-memory Python dicts (demo)
- **Frontend**: Streamlit with 5 tabs
- **AI Integration**: Real-time predictions on listing creation
- **KPI Tracking**: Session-based calculation ready for persistence

### Production Ready for:

- **Testing**: MVP with complete feature set
- **User feedback**: All core functionality works
- **Scaling**: Architecture supports PostgreSQL migration
- **Feature expansion**: Clear extension points for advanced features

### Next Steps for Production

1. **Database**: Implement PostgreSQL persistence (schema provided in README)
2. **Auth**: Add user registration and authentication
3. **Storage**: Connect AWS S3 for photo uploads
4. **Messaging**: Implement real message queue system
5. **Deployment**: Host on cloud platform (AWS, GCP, Azure)
6. **Monitoring**: Add analytics and error tracking

---

## Notes

> - Do not commit anything under `data/`. 
> - If `requirements.txt` changes, re-run `pip install -r requirements.txt`.
> - All marketplace features are integrated into the single Streamlit app (no external services required).
> - Sample data resets on app refresh (no persistence until database is added).
> - The marketplace is fully functional but designed for MVP testing before production deployment.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## References

- **Dataset:** [PetFinder.my Kaggle Competition](https://www.kaggle.com/c/petfinder-adoption-prediction)
- **ML Framework:** XGBoost, scikit-learn
- **Sentiment Analysis:** NLTK VADER + Google Cloud NLP (analytical only)
- **Frontend:** Streamlit, Plotly
- **Deployment:** Python pickle serialization (production ready)

---

## Public Repository Checklist

Before publishing, verify the following:

- No personal identifiers are present in documentation, notebook outputs, or logs.
- No secrets are present in tracked files (`.env`, API keys, tokens, credentials).
- Large local artifacts are excluded from git (`data/`, `.venv/`, caches, temporary files).
- Notebook outputs are cleared if they include local absolute paths or machine-specific details.
- The project README and license are generic and portfolio-ready.
