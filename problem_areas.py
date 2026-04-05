import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt


os.makedirs("output", exist_ok=True)
load_dotenv()

def recommend(row):
    if row["transit_need"] < df["transit_need"].median():
        return "No Major Action"
    elif row["train_score"] > row["bus_score"]:
        return "Rail Investment"
    else:
        return "Bus Optimization"


df = pd.read_csv(os.getenv("DF_PATH"))

df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("(", "").str.replace(")", "").str.replace("%", "Pct")

df = df.rename(columns={
    "Workers_Commuting_Into_the_County": "inflow",
    "Workers_Commuting_Out_of_the_County": "outflow",
    "Residents_Who_Work_in_Own_County": "residents_working",
    "Percentage_of_Employed_Residents_Who_Work_in_Own_County_Pct": "retention_rate",
    "Average_Travel_Time_to_Work_Minutes": "travel_time"
})

numeric_cols = [
    "inflow",
    "outflow",
    "residents_working",
    "travel_time",
    "retention_rate"
]

for col in numeric_cols:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["retention_rate"] = df["retention_rate"] / 100

df["commuter_intensity"] = (df["inflow"] + df["outflow"]) / df["residents_working"]
df["net_flow_ratio"] = (df["inflow"] - df["outflow"]) / (df["inflow"] + df["outflow"])

baseline = df["travel_time"].mean()
df["travel_pressure"] = df["travel_time"] / baseline

df["transit_need"] = df["commuter_intensity"] + df["travel_pressure"] + (1 - df["retention_rate"])
df["train_score"] = df["commuter_intensity"] * df["net_flow_ratio"].abs()
df["bus_score"] = (1 - df["retention_rate"]) * df["travel_pressure"]

df["population_affected"] = df["inflow"] + df["outflow"] + df["residents_working"]

df["absolute_impact"] = df["transit_need"] * df["population_affected"]
df["weighted_score"] = df["absolute_impact"]  
df["absolute_impact_minutes"] = df["travel_pressure"] * df["population_affected"] * baseline

def recommend(row):
    if row["transit_need"] < df["transit_need"].median():
        return "No Major Action"
    elif row["train_score"] > row["bus_score"]:
        return "Rail Investment"
    else:
        return "Bus Optimization"

df["recommendation"] = df.apply(recommend, axis=1)

top_relative = df.sort_values("transit_need", ascending=False).head(10)
top_absolute = df.sort_values("absolute_impact", ascending=False).head(10)

print("Top 10 by Relative Inefficiency:")
print(top_relative[["County", "transit_need", "train_score", "bus_score", "recommendation"]])

print("\nTop 10 by Absolute Impact:")
print(top_absolute[["County", "absolute_impact", "population_affected", "travel_pressure", "recommendation"]])

plt.figure(figsize=(10,6))
plt.scatter(
    df["commuter_intensity"],
    df["travel_pressure"],
    s=df["population_affected"] / 1000,  
    c=df["transit_need"],                
    cmap="Reds",
    alpha=0.6
)

plt.xlabel("Commuter Intensity")
plt.ylabel("Travel Pressure")
plt.title("Transportation Inefficiency Analysis (Absolute Impact Scaled)")
plt.colorbar(label="Transit Need (normalized)")

for i, txt in enumerate(df["County"]):
    plt.annotate(txt, (df["commuter_intensity"][i], df["travel_pressure"][i]), fontsize=8)

plt.savefig("output/problem_areas_absolute.png", bbox_inches='tight', dpi=300)
plt.show()