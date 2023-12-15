import dataframe_image as dfi
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from pandas.plotting import table
import scipy
from tqdm import tqdm


# SETTINGS
FROM_FILE = False
XI_INTERESTING_THRESHOLD = 0.99


# all global variables
IGNORE_COLUMNS = []
df = None
df_columns = None

# read them
if os.path.exists("config.py"):
    print("Config detected, reading from it")
    with open("config.py", "r") as fin:
        for i, line in enumerate(fin):
            line = line.strip()
            if i == 0:
                CSV_FILE = line
                df = pd.read_csv(CSV_FILE)
            else:
                if line == "":
                    break
                IGNORE_COLUMNS.append(line)
else:
    CSV_FILE = input("Path to .csv file to analzye, for example: data/psy_mark.csv\n")
    df = pd.read_csv(CSV_FILE)
    print("Columns:", df.columns)
    print("Write down all columns you want to ignore, each on new line. Write empty line to exit")
    while (col := input()):
        IGNORE_COLUMNS.append(col)
df_columns = [col for col in df.columns if not (col in IGNORE_COLUMNS)]


def colorFader(c1, c2, mix=0):
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

def color_xi(val):
    COLOR_START = "white"
    COLOR_END = "green"
    return f"background-color: {colorFader(COLOR_START, COLOR_END, val)}"

def drawPandasDataframe(dataframe, style=False, title="dataframe"):
    filename = "data/" + title
    if style:
        styled = dataframe.style.applymap(color_xi)
    else:
        styled = dataframe
    dfi.export(styled, f"{filename}.png")
    with open(f"{filename}.html", "w") as fout:
        fout.write(styled.to_html())
    print(f"Saved analyzis to {filename}.png and {filename}.html")

def xiCheck(colA, colB):
    TOTAL_TOKEN = ""
    length = df.shape[0]
    optionsA = list(set(df[colA]))
    optionsB = list(set(df[colB]))
    data = {}
    for A in optionsA:
        data[A] = {}
        for B in optionsB:
            data[A][B] = df[(df[colA] == A) & (df[colB] == B)].shape[0]
        data[A][TOTAL_TOKEN] = sum([data[A][k] for k in data[A]])
    data[TOTAL_TOKEN] = {}
    for B in optionsB + [TOTAL_TOKEN]:
        data[TOTAL_TOKEN][B] = sum([data[k][B] for k in data if k != TOTAL_TOKEN])
    xi = 0
    for A in optionsA:
        for B in optionsB:
            expected = data[A][TOTAL_TOKEN] * data[TOTAL_TOKEN][B] / data[TOTAL_TOKEN][TOTAL_TOKEN]
            xi += (data[A][B] - expected)**2 / expected
    freedom = (len(optionsA) - 1) * (len(optionsB) - 1)
    p = scipy.stats.chi2.cdf(xi, freedom)
    return p

def analyze(colA, colB):
    TOTAL_TOKEN = "total"
    optionsA = list(set(df[colA]))
    optionsB = list(set(df[colB]))
    abDf = pd.DataFrame([], columns=optionsA+[TOTAL_TOKEN], index=optionsB+[TOTAL_TOKEN])
    for A in optionsA:
        for B in optionsB:
            abDf[A][B] = df[(df[colA] == A) & (df[colB] == B)].shape[0]
    for A in optionsA:
        abDf[A][TOTAL_TOKEN] =df[(df[colA] == A)].shape[0]
    for B in optionsB:
        abDf[TOTAL_TOKEN][B] =df[(df[colB] == B)].shape[0]
    abDf[TOTAL_TOKEN][TOTAL_TOKEN] = len(df)
    drawPandasDataframe(abDf, title=f"{colA}_{colB}")

data = []
for colA in tqdm(df_columns):
    row = []
    for colB in df_columns:
        row.append(xiCheck(colA, colB))
    data.append(row)
xiDf = pd.DataFrame(data, columns=df_columns, index=df_columns)
drawPandasDataframe(xiDf, title="xicheck")

for i, colA in enumerate(df_columns):
    for colB in df_columns[i+1:]:
        if xiDf[colA][colB] > XI_INTERESTING_THRESHOLD:
            analyze(colA, colB)

