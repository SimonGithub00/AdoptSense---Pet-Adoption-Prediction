# AdoptSense-Pet-Adoption-Prediction
Full end-to-end ML pipeline (Tabular → +NLP (optional) → +Image/Meta (optional)) for Petfinder Adoption Speed prediction.

---

## Initial setup (everyone)

### 1) Open terminal in VS Code
VS Code → **Terminal → New Terminal**

### 2) Clone the repo
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd <REPO_NAME>
code .
```

### 3) Create a virtual environment (venv) — when and why
**When:** right after cloning (and anytime `requirements.txt` changes).  
**Why:** isolates Python packages per project so everyone avoids global conflicts and keeps installs consistent.

Create venv:
```bash
python -m venv .venv
```

Activate venv:

**macOS / Linux**
```bash
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Daily coding workflow (team rules)

### 1) Always start by syncing with `main`
```bash
git checkout main
git pull
```

### 2) Create a new branch for your work
Use a short descriptive name:
```bash
git checkout -b feat/<short-topic>
```

Examples:
```bash
git checkout -b feat/tabular-baseline
git checkout -b feat/text-features
git checkout -b feat/meta-features
```

### 3) Code + commit often
```bash
git status
git add .
git commit -m "Short message describing change"
```

### 4) Push your branch
```bash
git push -u origin feat/<short-topic>
```

### 5) Open a Pull Request (PR)
On GitHub: create a PR from your branch into `main`.

PR description should include:
- What changed
- How to run/test locally

### 6) Wait for approval, then merge
- At least **1 teammate approval** before merge
- After merge, update your local `main`:
```bash
git checkout main
git pull
```

### 7) If `main` changed while you worked (simple approach)
Merge `main` into your branch before final PR:
```bash
git checkout feat/<short-topic>
git merge main
git push
```

---

## Project structure

### Repo structure
```text
AdoptSense-Pet-Adoption-Prediction/
├─ README.md
├─ .gitignore
├─ requirements.txt
├─ LICENSE
├─ petadoption_run.ipynb
├─ data/                         # ignored (Kaggle files stay local)
│  ├─ train/
│  │  └─ train.csv
│  ├─ test/
│  │  └─ test.csv
│  ├─ train_images/
│  ├─ test_images/
│  ├─ train_metadata/
│  ├─ test_metadata/
│  ├─ train_sentiment/
│  ├─ test_sentiment/
│  ├─ sample_submission.csv
│  ├─ breed_labels.csv
│  ├─ BreedLabels.csv
│  ├─ PetFinder-BreedLabels.csv
│  ├─ color_labels.csv
│  ├─ ColorLabels.csv
│  ├─ PetFinder-ColorLabels.csv
│  ├─ state_labels.csv
│  ├─ StateLabels.csv
│  └─ PetFinder-StateLabels.csv
└─ src/
   ├─ config.py
   ├─ features_tabular.py
   ├─ features_text.py
   ├─ features_image_meta.py
   └─ model/                     # saved model artifacts
```

### Kaggle data structure (local only)
Place the Kaggle competition files here (do NOT commit):
```text
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
```

---

## What each file/class is for 

### `src/features_tabular.py`
**TabularFeatures**: selects numeric/categorical columns, handles missing values, encodes categoricals, outputs tabular preprocessing for the model pipeline.

### `src/features_text.py` (optional step 2)
**TextFeatures**: builds NLP features from `Description` (e.g., TF-IDF) and provides a transformer that can be combined with tabular preprocessing.

### `src/features_image_meta.py` (optional step 3)
**ImageMetaFeatures**: reads `train_metadata/*.json` and/or `train_sentiment/*.json` and converts them into numeric features (counts/scores/flags) keyed by `PetID`.

### `src/pedadoption_run.ipynb`
Class that combines EDA, calls feature engineering functions, creates pipeline (preprocess + model), trains and evaluates it, predicts on validation and safes model's trained parameters in model folder. 
Entry point to run:
- Stage 1: tabular baseline
- Stage 2 (optional): tabular + text
- Stage 3 (optional): tabular + text + metadata features  

---

## Notes
- Do not commit anything under `data/`.
- If `requirements.txt` changes, re-run:
```bash
pip install -r requirements.txt
```
