# analysis_notebook.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from collections import Counter

# ---------- CONFIG ----------
DATA_PATH = "metadata.csv"   # path to downloaded metadata.csv
SAMPLE_ROWS = None           # seted to  None for full file
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- LOAD ----------
def load_data(path=DATA_PATH, nrows=SAMPLE_ROWS):
    # metadata.csv can be large; use nrows for quick dev
    df = pd.read_csv(path, low_memory=False, nrows=nrows)
    return df

df = load_data()
print("Initial shape:", df.shape)
print(df.columns.tolist())

# ---------- BASIC EXPLORATION ----------
display(df.head())
print(df.info())
print("Missing values (top columns):")
print(df.isnull().sum().sort_values(ascending=False).head(30))

# ---------- CLEANING ----------
# Convert publish_time or publish_time-like column to datetime
# Common columns: 'publish_time' or 'publish_date' - check what exists
date_col = None
for c in ['publish_time', 'publish_time_updated', 'publish_date', 'publish_time_str']:
    if c in df.columns:
        date_col = c
        break

if date_col is None:
    print("No obvious date column found. Columns available:", df.columns.tolist())
else:
    print("Using date column:", date_col)
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df['year'] = df[date_col].dt.year

# Example: create abstract word count
if 'abstract' in df.columns:
    df['abstract_wordcount'] = df['abstract'].fillna("").apply(lambda s: len(str(s).split()))
else:
    df['abstract_wordcount'] = np.nan

# Identify columns with many missing values
missing_pct = df.isnull().mean().sort_values(ascending=False)
print("Columns with >80% missing:")
print(missing_pct[missing_pct > 0.8])

# Drop columns that are nearly empty (example threshold)
drop_cols = missing_pct[missing_pct > 0.98].index.tolist()
print("Dropping columns:", drop_cols)
df_clean = df.drop(columns=drop_cols)

# ---------- ANALYSIS ----------
# Publications by year
if 'year' in df_clean.columns:
    year_counts = df_clean['year'].value_counts().sort_index()
    print("Years range:", year_counts.index.min(), "-", year_counts.index.max())
else:
    year_counts = pd.Series(dtype=int)

# Top journals / sources
# There are columns like 'journal' or 'journal_ref' or 'source_x'
journal_cols = [c for c in df_clean.columns if 'journal' in c or 'source' in c or 'journal_ref' in c]
journal_col = journal_cols[0] if journal_cols else None
print("Journal/source column selected:", journal_col)

if journal_col:
    top_journals = df_clean[journal_col].fillna("Unknown").value_counts().head(20)
else:
    top_journals = pd.Series(dtype=int)

# Frequent words in titles
def clean_text(s):
    s = str(s).lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    return s

if 'title' in df_clean.columns:
    titles = df_clean['title'].dropna().astype(str).apply(clean_text)
    words = " ".join(titles).split()
    stopwords = set([
        'the','and','of','in','to','a','for','on','with','by','from','is','that','as','are','an','be',
        'this','we','s','study','studies','using','use'
    ])
    words = [w for w in words if w not in stopwords and len(w) > 2]
    word_counts = Counter(words)
    top_words = word_counts.most_common(30)
else:
    top_words = []

# ---------- VISUALIZATIONS ----------
plt.figure(figsize=(10,5))
if not year_counts.empty:
    plt.bar(year_counts.index.astype(int), year_counts.values)
    plt.xlabel("Year")
    plt.ylabel("Number of publications")
    plt.title("Publications by Year")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "publications_by_year.png"))
    plt.show()

if not top_journals.empty:
    plt.figure(figsize=(10,6))
    top_journals.plot(kind='bar')
    plt.title("Top publishing journals / sources")
    plt.ylabel("Paper count")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top_journals.png"))
    plt.show()

# Word cloud (titles)
if 'title' in df_clean.columns:
    wc = WordCloud(width=800, height=400, background_color="white").generate(" ".join(words))
    plt.figure(figsize=(12,6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title("Word Cloud of Titles")
    plt.savefig(os.path.join(OUTPUT_DIR, "title_wordcloud.png"))
    plt.show()

# Distribution by 'source_x' or similar
source_col = None
for c in ['source_x', 'source', 'publish_source']:
    if c in df_clean.columns:
        source_col = c
        break

if source_col:
    plt.figure(figsize=(8,6))
    df_clean[source_col].fillna("Unknown").value_counts().head(20).plot(kind='bar')
    plt.title("Top sources")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top_sources.png"))
    plt.show()

# ---------- SAVE A CLEAN SAMPLE ----------
# Save a cleaned CSV sample for the Streamlit app (smaller)
sample_out = os.path.join(OUTPUT_DIR, "metadata_clean_sample.csv")
df_clean.sample(frac=0.2, random_state=1).to_csv(sample_out, index=False)  # save 20% sample for fast load
print("Saved sample to", sample_out)

# ---------- QUICK SUMMARY PRINT ----------
print("Top title words (top 20):", top_words[:20])
print("Top journals (top 10):")
print(top_journals.head(10))
