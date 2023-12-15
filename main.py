import pandas as pd
import scipy

# Load the CSV file
df = pd.read_csv("psy_mark.csv")

def analyze(colA, colB):
    optionsA = list(set(df[colA]))
    optionsB = list(set(df[colB]))
    for A in optionsA:
        aggr = []
        for B in optionsB:
            count = df[(df[colA] == A) & (df[colB] == B)].shape[0]
            aggr.append(count)
        print(A)
        for B, count in zip(optionsB, aggr):
            print(B, "\t\t", count, "\t\t", count / sum(aggr))

def correlate(colA, colB):
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
    print(p, xi, freedom)

analyze("Ваш пол?", "Играете в компьютерные игры?")
correlate("Ваш пол?", "Играете в компьютерные игры?")

#correlate("Ваш пол?", "Ваш пол?")
#correlate("Играете в компьютерные игры?", "Играете в компьютерные игры?")

analyze("Была ли у вас золотая медаль в школе?", "Вы пьёте алкоголь?")
correlate("Была ли у вас золотая медаль в школе?", "Вы пьёте алкоголь?")

analyze("Ваш курс.", "Ваш пол?")
correlate("Ваш курс.", "Ваш пол?")

analyze("Занимаетесь спортом?", "Часто гуляете на свежем воздухе?")
correlate("Занимаетесь спортом?", "Часто гуляете на свежем воздухе?")

