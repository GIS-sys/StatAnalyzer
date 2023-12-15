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

def drawPandasDataframe(dataframe):
    filename = "data/xicheck"
    styled = dataframe.style.applymap(color_xi)
    dfi.export(styled, f"{filename}.png")
    html = styled.to_html()
    with open(filename, "w") as fout:
        fout.write(f"{filename}.html")
    print(f"Saved analyzis to {filename}.png and {filename}html")

def xiCheck(colA, colB):
    EMPTY_TOKEN = ""
    length = df.shape[0]
    optionsA = list(set(df[colA]))
    optionsB = list(set(df[colB]))
    data = {}
    for A in optionsA:
        data[A] = {}
        for B in optionsB:
            data[A][B] = df[(df[colA] == A) & (df[colB] == B)].shape[0]
        data[A][EMPTY_TOKEN] = sum([data[A][k] for k in data[A]])
    data[EMPTY_TOKEN] = {}
    for B in optionsB + [EMPTY_TOKEN]:
        data[EMPTY_TOKEN][B] = sum([data[k][B] for k in data if k != EMPTY_TOKEN])
    xi = 0
    for A in optionsA:
        for B in optionsB:
            expected = data[A][EMPTY_TOKEN] * data[EMPTY_TOKEN][B] / data[EMPTY_TOKEN][EMPTY_TOKEN]
            xi += (data[A][B] - expected)**2 / expected
    freedom = (len(optionsA) - 1) * (len(optionsB) - 1)
    p = scipy.stats.chi2.cdf(xi, freedom)
    return p


data = []
for colA in tqdm(df_columns):
    row = []
    for colB in df_columns:
        row.append(xiCheck(colA, colB))
    data.append(row)
xiDf = pd.DataFrame(data, columns=df_columns, index=df_columns)
drawPandasDataframe(xiDf)

