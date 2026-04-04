import pandas as pd

df = pd.read_csv("C:\\Users\\anika\\Desktop\\development\\smith_datathon\\datasets\\Choose_Maryland___Compare_Counties_-_Transportation_20260403.csv")

net_commute = dict(zip(
    df["County"],
    df["Net Workers Commuting Into/Out of the County"]
))

print(net_commute)