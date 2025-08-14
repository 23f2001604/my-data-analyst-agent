from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from utils import encode_plot_to_base64
import pandas as pd
import requests, io, os, re
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

app = FastAPI()

@app.post("/")
async def analyze(
    questions: UploadFile = File(...),
    file1: UploadFile = File(None),
    file2: UploadFile = File(None),
    file3: UploadFile = File(None)
):
    # Read questions
    qtext = (await questions.read()).decode()
    # Parse files
    files = {}
    for i, f in enumerate([file1, file2, file3]):
        if f:
            content = await f.read()
            files[f.filename] = content

    # Select handler based on questions.txt
    # For example, if "highest grossing films" in qtext:
    if 'highest grossing' in qtext.lower():
        answers = answer_highest_grossing_films()
        return JSONResponse(content=answers)
    # (Repeat with if/elif for other datasets and question types...)
    # Fallback:
    return JSONResponse(content=["Unsupported question format"])

def answer_highest_grossing_films():
    # Scrape Wikipedia
    url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find('table', {'class': 'wikitable'})
    df = pd.read_html(str(table))[0]
    df.columns = [c.lower().strip().replace("\n"," ") for c in df.columns]  # Clean

    # Handle dollar values
    df['worldwide gross'] = df['worldwide gross'].astype(str).str.replace(r"[^\d.]", "", regex=True).astype(float)
    df['year'] = df['year'].astype(int)

    # Q1: How many $2 bn movies before 2000?
    q1 = df[(df['worldwide gross'] >= 2_000_000_000) & (df['year'] < 2000)].shape[0]

    # Q2: Earliest film >$1.5bn
    filtered = df[df['worldwide gross'] > 1_500_000_000]
    if not filtered.empty:
        idx = filtered['year'].idxmin()
        q2 = df.loc[idx]["film"]
    else:
        q2 = ""

    # Q3: Correlation (Rank vs Worldwide Gross)
    ranks = np.arange(1, len(df)+1)
    peak = df['worldwide gross']
    corr = np.corrcoef(ranks, peak)[0,1]
    q3 = float(np.round(corr, 6))  # round for scoring

    # Q4: Scatterplot with regression
    plt.figure(figsize=(6,4))
    plt.scatter(ranks, peak, label='Data', alpha=0.7)
    # Regression line
    m, b = np.polyfit(ranks, peak, 1)
    plt.plot(ranks, m*ranks+b, 'r--', label='Red Regression')
    plt.xlabel("Rank")
    plt.ylabel("Peak")
    plt.legend()
    plt.tight_layout()
    img_str = encode_plot_to_base64(plt.gcf())
    plt.close()
    return [q1, q2, q3, img_str]
