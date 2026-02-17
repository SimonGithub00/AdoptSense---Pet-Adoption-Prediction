# AdoptSense-Pet-Adoption-Prediction
Full end-to-end ML pipeline (Tabular → +NLP (optional) → +Image/Meta (optional)) for Petfinder Adoption Speed prediction.

---

## Initial setup (everyone)

### 1) Open terminal in VS Code
VS Code → **Terminal → New Terminal**

### 2) Clone the repo

git clone <YOUR_GITHUB_REPO_URL>
cd <REPO_NAME>


### 3) Create a virtual environment (venv) — when and why
**When:** right after cloning (and anytime `requirements.txt` changes).  
**Why:** isolates Python packages per project so everyone avoids global conflicts and keeps installs consistent.

Create venv:

python -m venv .venv


Activate venv:

**macOS / Linux**

source .venv/bin/activate


**Windows (PowerShell)**

.\.venv\Scripts\Activate.ps1


Install dependencies (takes a while the very first time):

python -m pip install --upgrade pip
pip install -r requirements.txt


---

## Daily coding workflow (team rules)

### 1) Always start by syncing with `main`

git checkout main
git pull


### 2) Create a new branch for your work
Use a short descriptive name:

git checkout -b feat/<short-topic>


Examples:

git checkout -b feat/tabular-baseline
git checkout -b feat/text-features
git checkout -b feat/meta-features


### 3) Code + commit often

git status
git add .
git commit -m "Short message describing change"


### 4) Push your branch

git push -u origin feat/<short-topic>


### 5) Open a Pull Request (PR)
On GitHub: create a PR from your branch into `main`.

PR description should include:
- What changed
- How to run/test locally

### 6) Wait for approval, then merge
- At least **1 teammate approval** before merge
- After merge, update your local `main`:

git checkout main
git pull


### 7) If `main` changed while you worked (simple approach)
Merge `main` into your branch before final PR:

git checkout feat/<short-topic>
git merge main
git push


---

## Project structure

### Repo structure

adoptsense/
├─ README.md
├─ .gitignore
├─ requirements.txt
├─ data/                  # ignored (Kaggle files stay local)
└─ src/
   ├─ __init__.py
   ├─ config.py
   ├─ data_loader.py
   ├─ features_tabular.py
   ├─ features_text.py
   ├─ features_image_meta.py
   ├─ model_trainer.py
   ├─ evaluator.py
   └─ run.py


### Kaggle data structure (local only)
Place the Kaggle competition files here (do NOT commit):

data/raw/
├─ train/
│  ├─ train.csv
│  ├─ train_images/
│  ├─ train_metadata/
│  └─ train_sentiment/
├─ test/
│  ├─ test.csv
│  ├─ test_images/
│  ├─ test_metadata/
│  └─ test_sentiment/
├─ sample_submission.csv
├─ breed_labels.csv
├─ color_labels.csv
└─ state_labels.csv


---

## What each file/class is for (minimal)

### `src/config.py`
Holds all paths (train/test CSV, metadata folders, etc.) and key column names.

### `src/data_loader.py`
**DataLoader**: loads `train.csv`/`test.csv`, merges label lookup tables if needed, and creates a stratified train/valid split on `AdoptionSpeed`.

### `src/features_tabular.py`
**TabularFeatures**: selects numeric/categorical columns, handles missing values, encodes categoricals, outputs tabular preprocessing for the model pipeline.

### `src/features_text.py` (optional step 2)
**TextFeatures**: builds NLP features from `Description` (e.g., TF-IDF) and provides a transformer that can be combined with tabular preprocessing.

### `src/features_image_meta.py` (optional step 3)
**ImageMetaFeatures**: reads `train_metadata/*.json` and/or `train_sentiment/*.json` and converts them into numeric features (counts/scores/flags) keyed by `PetID`.

### `src/model_trainer.py`
**ModelTrainer**: creates a single pipeline (preprocess + model), trains it, predicts on validation, and supports stages (tabular / +text / +meta).

### `src/evaluator.py`
**Evaluator**: computes Quadratic Weighted Kappa (main metric) plus a small comparison summary (e.g., confusion matrix / per-class metrics).

### `src/run.py`
Entry point to run:
- Stage 1: tabular baseline
- Stage 2 (optional): tabular + text
- Stage 3 (optional): tabular + text + metadata features  
Prints metrics and can save minimal artifacts (optional: predictions, `metrics.json`).

---

## Notes
- Do not commit anything under `data/`.
- If `requirements.txt` changes, re-run:

pip install -r requirements.txt

