Data_Analysis_Assignment_wk_7
├─ README.md
├─ metadata.csv                
├─ outputs/
│  ├─ metadata_clean_sample.csv
│  ├─ publications_by_year.png
│  └─ ...      # or analysis.ipynb
├─ streamlit_app.py


# COVID-19 Metadata Explorer (Frameworks_Assignment)

This project explores the CORD-19 `metadata.csv` file (sample) and provides a Streamlit app for interactive exploration.

## Structure
- `analysis_notebook.py` : data loading, cleaning, and visualization scripts
- `streamlit_app.py` : interactive app (run `streamlit run streamlit_app.py`)
- `outputs/` : saved plots and cleaned sample CSV

## Setup
1. Create virtual env and install dependencies:
   `pip install -r requirements.txt`
2. Place `metadata.csv` in the project root (or use the provided sample in `outputs/`).
3. Run analysis: `python analysis_notebook.py`
4. Run app: `streamlit run streamlit_app.py`

## Notes
- The original metadata file is large. Used `SAMPLE_ROWS` (in `analysis_notebook.py`) to load a subset for development.
- This assignment includes data cleaning, time-based analysis, journal/source counts, title word frequency, and interactive visualizations.
