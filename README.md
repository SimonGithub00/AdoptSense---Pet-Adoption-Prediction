# AdoptSense — Pet Adoption Speed Prediction

End-to-end machine learning pipeline predicting how quickly a pet listed on PetFinder will be adopted (same day to never), built on the Kaggle PetFinder.my dataset. The trained pipeline powers a Streamlit frontend for live predictions.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Findings](#key-findings)
- [Model](#model)
- [Feature Engineering](#feature-engineering)
- [Sentiment Analysis](#sentiment-analysis)
- [Notebook Structure](#notebook-structure)
- [Source Modules](#source-modules)
- [Pipeline Artifact](#pipeline-artifact)
- [Project Structure](#project-structure)
- [Data Setup](#data-setup)
- [Setup and Installation](#setup-and-installation)
- [Running the Notebook](#running-the-notebook)

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

**Evaluation metrics:** Accuracy, Macro F1, Weighted F1, Macro Precision, Macro Recall, per-class F1, ROC curves (one-vs-rest), Precision-Recall curves, confusion matrices.

Macro F1 is used as the primary selection metric because it weights all five classes equally, penalising poor performance on minority classes (especially Speed 0, which represents only 2.7% of the data). Class weights are applied during training to partially counteract the imbalance.

**Validation:** Stratified train/validation split (80/20). Stratification preserves the class distribution in both sets, giving a reliable generalisation estimate without access to labelled test data.

---

## Feature Engineering

`TabularFeatures` (`src/features_tabular.py`) produces 27 features from the raw listing DataFrame. All features are integer-encoded; the StandardScaler is applied to all 27 for consistency with the inference path (scaling has no effect on XGBoost predictions since tree-based models are scale-invariant).

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

Section 3.4 of the notebook uses these features for an ablation test (Google NLP JSON vs no sentiment baseline), confirming they add signal. Section 3.5 runs a head-to-head comparison against VADER.

### VADER (deployed pipeline)

Despite Google NLP JSON features reaching a higher Macro F1 on validation data, VADER was selected for the deployed pipeline for a concrete engineering reason: the Google NLP JSON files exist only for the training corpus. For any new pet listing submitted through the frontend, no pre-computed JSON exists. The only alternatives would be calling the Google Cloud NLP API at inference time (latency, cost, external dependency) or zero-filling the 10 features (removing exactly the signal that gave Google NLP its advantage). VADER is computed directly from the description string — offline, instantaneous, and free — producing identical behaviour in training and in production.

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
| **3.4 JSON Sentiment Feature Impact** | Ablation: 27-feature baseline vs 37-feature (+ Google NLP JSON) model |
| **3.5 Performance Test: Sentiment Approaches** | Head-to-head: VADER vs Google NLP JSON; deployment decision (VADER) with rationale |
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
| `scaler` | `StandardScaler` | Fitted on 27 training features |
| `model` | `XGBClassifier` | Trained XGBoost (300 estimators) |
| `feature_columns` | `list[str]` | Ordered list of 27 expected feature names |
| `numeric_features` | `list[str]` | Same 27 columns (all integer-encoded) |
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
├── README.md
├── requirements.txt
├── LICENSE
├── data/                            # gitignored — Kaggle files stay local
│   ├── train/
│   │   ├── train.csv                # 14,993 labelled pet listings
│   │   ├── train_images/
│   │   ├── train_metadata/
│   │   └── train_sentiment/         # Google NLP JSON files (one per PetID)
│   ├── test/                        # no AdoptionSpeed labels — not used for eval
│   ├── breed_labels.csv
│   ├── color_labels.csv
│   └── state_labels.csv
├── src/
│   ├── config.py                    # Central config (paths, constants)
│   ├── features_tabular.py          # TabularFeatures + VADER sentiment
│   ├── features_sentiment.py        # SentimentFeatures (Google NLP JSON)
│   ├── features_text.py             # Stub for future text features
│   ├── features_image_meta.py       # Stub for future image/metadata features
│   ├── petadoption_run.ipynb        # Full analytical and training notebook
│   └── model/
│       ├── petadoption_pipeline.pkl # Saved pipeline (scaler + XGBoost)
│       └── pipeline_summary.txt     # Human-readable pipeline metadata
└── frontend/
    ├── app.py                       # Streamlit application
    ├── requirements.txt
    └── utils/
        ├── predictions.py           # AdoptionPredictor, feature alignment
        ├── model_loader.py          # Singleton pipeline loader
        └── recommendations.py       # Rule-based adoption factor analysis
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
git clone <repo-url>
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

**3. Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Run the notebook**

```bash
jupyter notebook src/petadoption_run.ipynb
```

Run all cells top to bottom. The pipeline pickle is written to `src/model/` at Section 4.

**5. Launch the frontend** (optional)

```bash
streamlit run frontend/app.py
```


> Do not commit anything under `data/`. If `requirements.txt` changes, re-run `pip install -r requirements.txt`.
