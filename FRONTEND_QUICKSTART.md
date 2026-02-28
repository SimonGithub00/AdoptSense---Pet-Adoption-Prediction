# 🚀 AdoptSense Frontend - Quick Start Guide

## 30-Second Setup

### Windows Users

1. **Open PowerShell** in the project root folder
2. **Run this command:**
   ```powershell
   cd frontend
   python -m streamlit run app.py
   ```
3. **Wait 3-5 seconds** - The app will open in your browser automatically

### Mac/Linux Users

1. **Open Terminal** in the project root folder
2. **Run these commands:**
   ```bash
   cd frontend
   python -m streamlit run app.py
   ```
3. **Wait 3-5 seconds** - The app will open in your browser automatically

---

## Alternative: Use Startup Scripts

### Windows
- Double-click: `frontend\run_app.bat`
- Or run: `.\frontend\run_app.bat` in PowerShell

### Mac/Linux
- Run: `bash frontend/run_app.sh`

---

## What to Expect

✅ A Streamlit web interface opens at `http://localhost:8501`  
✅ Four tabs: Home, Batch Upload, Single Pet Form, About  
✅ No external internet needed (runs locally)  
✅ Model predictions in real-time  

---

## Common Issues & Solutions

### "Module not found" Error
**Problem:** Python can't find the model or src files  
**Solution:** Make sure you're in the project root directory before running the command

### "Port 8501 is already in use"
**Problem:** Another app is using port 8501  
**Solution:** Run with a different port:
```bash
streamlit run app.py --server.port 8502
```

### Streamlit not installed
**Problem:** `ModuleNotFoundError: No module named 'streamlit'`  
**Solution:** Install the frontend dependencies:
```bash
cd frontend
pip install -r requirements.txt
```

### Model file not found
**Problem:** `FileNotFoundError: Model not found`  
**Solution:** Make sure you've run the training notebook first:
1. Open `src/petadoption_run.ipynb`
2. Run all cells
3. This will create `src/model/petadoption_pipeline.pkl`

---

## First Time Using the App?

### 1. **Start with Home Tab** 📊
- Learn about adoption speed categories
- Understand the prediction system
- See example workflows

### 2. **Try Batch Upload** 📁
- Download sample CSV from the app
- Or use the one in `frontend/assets/sample_pets.csv`
- Upload and get predictions for multiple pets
- See comparative rankings

### 3. **Try Single Pet Form** 📝
- Fill in details for one pet
- Get instant prediction
- Read personalized recommendations
- Understand what affects adoption speed

### 4. **Explore Recommendations** 💡
- Focus on top 3 suggestions
- Implement changes to improve adoption speed
- Photography is critical! 📸

---

## File Locations

```
AdoptSense-Pet-Adoption-Prediction/
├── frontend/                      ← You are here
│   ├── app.py                    (Main Streamlit app)
│   ├── run_app.bat               (Windows startup)
│   ├── run_app.sh                (Mac/Linux startup)
│   ├── requirements.txt           (Dependencies)
│   ├── utils/                    (Helper modules)
│   ├── assets/                   (Sample data)
│   └── README.md                 (Full documentation)
├── src/                          (Model code)
│   ├── config.py
│   ├── features_tabular.py
│   ├── features_text.py
│   ├── features_image_meta.py
│   ├── model/
│   │   └── petadoption_pipeline.pkl  (The trained model)
│   └── petadoption_run.ipynb     (Training notebook)
└── data/                         (Datasets)
    ├── train/
    ├── test/
    ├── train_metadata/
    └── ...
```

---

## Tips for Best Results

### 🎯 Photography
- **Critical:** Upload 3-5 photos minimum
- Each photo should be clear and well-lit
- Show the pet's personality
- Include close-ups and full-body shots

### ✍️ Description
- Write at least 50 words
- Tell the pet's story
- Use warm, emotional language
- Mention personality traits and hobbies

### 💰 Pricing
- Free adoptions adopt faster
- Consider waiving fees for older animals
- Use deposit model if fees are required

### 🐣 Age
- Young pets naturally adopt faster
- Older pets need special marketing
- Emphasize benefits of mature animals

### 🏥 Health
- Be transparent about health issues
- Document all medical care
- Highlight completed treatments

---

## Performance Tips

### Slow Performance?
1. Close unnecessary browser tabs
2. Restart the Streamlit app
3. Clear browser cache

### Large Batch Upload?
- Split CSV into files of 500-1000 pets
- Upload them one at a time
- Combine results manually if needed

### Memory Issues?
- Process smaller batches
- Restart the app
- Close other applications

---

## Common Workflows

### Workflow 1: Quick Prediction
```
1. Open app
2. Go to "Single Pet Form"
3. Fill in pet details
4. Click "Get Prediction"
5. Read top 3 recommendations
6. Implement changes
```

### Workflow 2: Batch Analysis
```
1. Prepare CSV with multiple pets
2. Go to "Batch Upload"
3. Download sample CSV for reference
4. Fill in your data
5. Upload CSV
6. View rankings
7. Review recommendations for each pet
8. Focus on "slow adopter" category
```

### Workflow 3: Listing Optimization
```
1. Use single pet form for current listing
2. Note the prediction and recommendations
3. Take more/better photos
4. Enhance description
5. Consider price adjustment
6. Re-run prediction
7. Check improvement
8. List with optimized profile
```

---

## Need More Help?

### Check the Full README
```bash
cat frontend/README.md
```

### View Model Details
Open the training notebook: `src/petadoption_run.ipynb`

### Check Configuration
Edit or view: `src/config.py`

### Review Sample Data
Open: `frontend/assets/sample_pets.csv`

---

## Features at a Glance

| Feature | Location | Use Case |
|---------|----------|----------|
| Home | Tab 1 | Learn about the system |
| Batch Predictions | Tab 2 | Compare multiple pets |
| Single Predictions | Tab 3 | Analyze one pet |
| CSV Download | Tab 2 | Get sample format |
| Visualizations | Tabs 2-3 | See rankings & charts |
| Recommendations | Tabs 2-3 | Get improvement ideas |
| About | Tab 4 | Project background |

---

## Keyboard Shortcuts

- `Ctrl+C` - Stop the app
- `R` - Rerun the app (in browser)
- `S` - Clear state
- `Q` - Quit

---

## URL Navigation

Once the app is running:

- **Home:** `http://localhost:8501/`
- **CSV Upload:** `http://localhost:8501/?tab=upload`
- **Single Form:** `http://localhost:8501/?tab=form`
- **About:** `http://localhost:8501/?tab=about`

*(Note: URLs may vary depending on Streamlit version)*

---

## You're Ready! 🎉

**Next Steps:**
1. Run the app
2. Explore the interface
3. Upload test data
4. Get predictions
5. Implement recommendations
6. See adoption improvements!

---

**Questions?** Check `frontend/README.md` for detailed documentation.

**Happy adopting! 🐾**
