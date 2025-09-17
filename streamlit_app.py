# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np

st.set_page_config(page_title="CORD-19 Data Explorer", layout="wide")
st.title("CORD-19 Data Explorer")
st.write("Interactive explorer for the CORD-19 metadata (sample).")

# Path to cleaned sample created in analysis script
SAMPLE_PATH = "outputs/metadata_clean_sample.csv"

@st.cache_data
def load_data(path=SAMPLE_PATH):
    df = pd.read_csv(path, low_memory=False)
    # Ensure date and year columns exist
    if 'publish_time' in df.columns:
        df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
        df['year'] = df['publish_time'].dt.year
    if 'year' not in df.columns and 'publish_time' in df.columns:
        df['year'] = df['publish_time'].dt.year
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
years = df['year'].dropna().astype(int)
min_year = int(years.min()) if not years.empty else 2019
max_year = int(years.max()) if not years.empty else 2022
year_range = st.sidebar.slider("Select year range", min_year, max_year, (min_year, max_year))

journal_col = None
for c in df.columns:
    if 'journal' in c or 'source' in c:
        journal_col = c
        break

if journal_col:
    journals = df[journal_col].fillna("Unknown").unique().tolist()
    selected_journal = st.sidebar.selectbox("Journal / Source (All for none)", ["All"] + sorted(journals))
else:
    selected_journal = "All"

# Apply filters
filtered = df.copy()
if 'year' in df.columns:
    filtered = filtered[filtered['year'].between(year_range[0], year_range[1], inclusive="both")]
if selected_journal != "All" and journal_col:
    filtered = filtered[filtered[journal_col] == selected_journal]

st.markdown(f"### Showing {len(filtered):,} records for years {year_range[0]}—{year_range[1]}")

# Plot: publications by year
if 'year' in filtered.columns:
    year_counts = filtered['year'].value_counts().sort_index()
    fig, ax = plt.subplots()
    ax.bar(year_counts.index.astype(int), year_counts.values)
    ax.set_title("Publications by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    st.pyplot(fig)

# Top journals
if journal_col:
    st.markdown("#### Top journals / sources (in filtered data)")
    top_j = filtered[journal_col].fillna("Unknown").value_counts().head(10)
    st.bar_chart(top_j)

# Word cloud of titles
if 'title' in filtered.columns:
    st.markdown("#### Word cloud from titles")
    titles_text = " ".join(filtered['title'].dropna().astype(str).tolist())
    if len(titles_text.strip()) > 0:
        wc = WordCloud(width=800, height=400, background_color="white").generate(titles_text)
        fig_wc, ax_wc = plt.subplots(figsize=(12,6))
        ax_wc.imshow(wc, interpolation='bilinear')
        ax_wc.axis('off')
        st.pyplot(fig_wc)
    else:
        st.write("No title text available for word cloud.")

# Data sample table
st.markdown("### Data sample")
st.dataframe(filtered.sample(min(50, len(filtered))).reset_index(drop=True))

#Run the app with:
# streamlit run streamlit_app.py