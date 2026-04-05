import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

os.makedirs("output", exist_ok=True)

load_dotenv()

df = pd.read_csv(os.getenv("DF_PATH"))
df_ontime = pd.read_csv(os.getenv("DF2_PATH"))
df_road = pd.read_csv("datasets/Maryland_Road_Closures_20260403.csv")

def commute_data(df):
    df.columns = df.columns.str.strip()

    df["Net Workers Commuting Into/Out of the County"] = pd.to_numeric(
        df["Net Workers Commuting Into/Out of the County"],
        errors="coerce"
    )

    df = df.sort_values(
        by="Net Workers Commuting Into/Out of the County",
        ascending=False
    )

    fig, ax = plt.subplots()
    ax.axis('off')

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(df.columns))))

    plt.savefig("output/net_commute_table.png", bbox_inches='tight', dpi=300)

def on_time(df):
    df.columns = df.columns.str.strip()
    transit_cols = ["Core Bus", "Metro", "Light Rail", "MARC", "Mobility/Taxi Access"]

    for col in transit_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("%", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Fiscal Year"] = (
        df["Fiscal Year"]
        .astype(str)
        .str.extract(r'(\d+)')
        .astype(float)
    )

    df = df.dropna(subset=["Fiscal Year"])
    grouped = df.groupby("Fiscal Year")[transit_cols].mean().reset_index()

    plt.figure(figsize=(10, 6))

    for col in transit_cols:
        plt.plot(grouped["Fiscal Year"], grouped[col], marker='o', label=col)

    plt.xlabel("Fiscal Year")
    plt.ylabel("On-Time Performance (%)")
    plt.title("On-Time Performance by Transit Type Over Time")
    plt.legend()
    plt.grid(True)

    plt.savefig("output/ontime_performance.png", bbox_inches='tight', dpi=300)

on_time(df_ontime)


def road_closure_data(df):
    df.columns = df.columns.str.strip().str.lower()

    df["county"] = df["county"].astype(str).str.strip()
    df["direction"] = df["direction"].astype(str).str.strip()
    df["lanes"] = df["lanes"].astype(str).str.strip()

    county_counts = df["county"].value_counts().head(10)
    direction_counts = df["direction"].value_counts()
    lane_counts = df["lanes"].value_counts().head(10)
    lane_counts = lane_counts.sort_values()

    fig, axes = plt.subplots(3, 1, figsize=(14, 18))

    county_counts.plot(kind="bar", ax=axes[0])
    axes[0].set_title("Top 10 Counties by Road Closures")
    axes[0].set_xlabel("County")
    axes[0].set_ylabel("Number of Closures")
    axes[0].tick_params(axis="x", rotation=45)

    direction_counts.plot(kind="bar", ax=axes[1])
    axes[1].set_title("Road Closures by Direction")
    axes[1].set_xlabel("Direction")
    axes[1].set_ylabel("Number of Closures")
    axes[1].tick_params(axis="x", rotation=45)

    lane_counts.plot(kind="barh", ax=axes[2])
    axes[2].set_title("Top 10 Lane Closure Types")
    axes[2].set_xlabel("Number of Closures")
    axes[2].set_ylabel("Lane Type")

    for i, v in enumerate(lane_counts.values):
        axes[2].text(v + 0.1, i, str(v), va="center")

    plt.tight_layout()
    plt.savefig("output/road_closure_summary.png", bbox_inches="tight", dpi=300)

road_closure_data(df_road)