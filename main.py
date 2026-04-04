import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("C:\\Users\\anika\\Desktop\\development\\smith_datathon\\datasets\\Choose_Maryland___Compare_Counties_-_Transportation_20260403.csv")

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

commute_data(df)