import os
import pandas as pd
import scipy
from tqdm import tqdm


# all global variables
FROM_FILE = False
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



#def analyze(colA, colB):
#    optionsA = list(set(df[colA]))
#    optionsB = list(set(df[colB]))
#    for A in optionsA:
#        aggr = []
#        for B in optionsB:
#            count = df[(df[colA] == A) & (df[colB] == B)].shape[0]
#            aggr.append(count)
#        print(A)
#        for B, count in zip(optionsB, aggr):
#            print(B, "\t\t", count, "\t\t", count / sum(aggr))

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
    # print(p, xi, freedom)
    return p

data = []
for colA in tqdm(df_columns):
    row = []
    for colB in df_columns:
        row.append(xiCheck(colA, colB))
    data.append(row)
print(data)
df = pd.DataFrame(data, columns=df_columns, index=df_columns)
print(df)
