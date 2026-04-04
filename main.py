import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("C:\\Users\\anika\\Desktop\\development\\smith_datathon\\datasets\\Choose_Maryland___Compare_Counties_-_Transportation_20260403.csv")
df_ontime = pd.read_csv("C:\\Users\\anika\\Desktop\\development\\smith_datathon\\datasets\\On_Time_Performance_20260403.csv")

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