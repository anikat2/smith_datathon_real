import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import matplotlib.patheffects as pe
import matplotlib.patches as mpatches

os.makedirs("output", exist_ok=True)

load_dotenv()

df = pd.read_csv(os.getenv("DF_PATH"))
df_ontime = pd.read_csv(os.getenv("DF2_PATH"))
df_abc = pd.read_csv(os.getenv("DF3_PATH"))


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


# ── OPTION A ─────────────────────────────────────────────────────────────────
# Horizontal bar chart: total project count by Transportation Business Unit
# Shows which agency is driving the most CTP investment statewide
# ─────────────────────────────────────────────────────────────────────────────
def projects_by_agency(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    counts = (
        df["Transportation Business Unit"]
        .value_counts()
        .sort_values(ascending=True)
    )

    # Shorten long agency names for readability
    short_names = {
        "Maryland State Highway Administration": "State Highway (SHA)",
        "Maryland Transit Administration":       "Transit (MTA)",
        "Maryland Port Administration":          "Port (MPA)",
        "Maryland Aviation Administration":      "Aviation (MAA)",
        "The Secretary's Office":                "Secretary's Office",
        "Maryland Transportation Authority":     "Transportation Authority",
        "Motor Vehicle Administration":          "Motor Vehicle (MVA)",
    }
    counts.index = [short_names.get(i, i) for i in counts.index]

    colors = [
        "#E63946" if "Transit" in label else "#4A90D9"
        for label in counts.index
    ]

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor("#0F1117")
    ax.set_facecolor("#141824")

    bars = ax.barh(counts.index, counts.values, color=colors, edgecolor="none", height=0.6)

    # Value labels on bars
    for bar, val in zip(bars, counts.values):
        ax.text(
            bar.get_width() + 8, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", ha="left", color="white", fontsize=10
        )

    ax.set_xlabel("Number of CTP Projects", color="#AAAAAA", fontsize=11)
    ax.set_title(
        "CTP FY2024–FY2029: Projects by Agency (Statewide)",
        fontsize=14, fontweight="bold", color="white", pad=14
    )
    ax.tick_params(colors="#AAAAAA", labelsize=10)
    ax.set_xlim(0, counts.max() * 1.12)
    ax.grid(axis="x", color="#2A2F45", linewidth=0.5, linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Highlight MTA bar with annotation
    mta_label = "Transit (MTA)"
    if mta_label in counts.index:
        ax.annotate(
            "← Focus area for\nBaltimore TOD proposal",
            xy=(counts[mta_label], list(counts.index).index(mta_label)),
            xytext=(counts[mta_label] - 180, list(counts.index).index(mta_label) + 0.6),
            color="#E63946", fontsize=8,
            arrowprops=dict(arrowstyle="->", color="#E63946"),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#1A1E2E", edgecolor="#E63946", alpha=0.9)
        )

    plt.tight_layout()
    plt.savefig("output/A_projects_by_agency.png", dpi=200, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()


# ── OPTION B ─────────────────────────────────────────────────────────────────
# Stacked bar chart: top counties by project count, stacked by agency
# Reveals which agencies are driving investment in each county
# Excludes Areawide/Statewide catch-alls to show geographically specific data
# ─────────────────────────────────────────────────────────────────────────────
def county_breakdown_by_agency(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Drop non-geographic catch-alls
    exclude = ["Areawide", "Statewide"]
    df = df[~df["County"].isin(exclude)]

    short_names = {
        "Maryland State Highway Administration": "SHA",
        "Maryland Transit Administration":       "MTA",
        "Maryland Port Administration":          "MPA",
        "Maryland Aviation Administration":      "MAA",
        "The Secretary's Office":                "Sec. Office",
        "Maryland Transportation Authority":     "MdTA",
        "Motor Vehicle Administration":          "MVA",
    }
    df["Agency"] = df["Transportation Business Unit"].map(short_names).fillna("Other")

    # Top 12 counties by project count
    top_counties = df["County"].value_counts().head(12).index.tolist()
    df = df[df["County"].isin(top_counties)]

    pivot = (
        df.groupby(["County", "Agency"])
        .size()
        .unstack(fill_value=0)
    )
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]

    agency_colors = {
        "SHA":        "#4A90D9",
        "MTA":        "#E63946",
        "MPA":        "#2A9D8F",
        "MAA":        "#F4A261",
        "MdTA":       "#A8DADC",
        "MVA":        "#C77DFF",
        "Sec. Office":"#888888",
        "Other":      "#555555",
    }
    colors = [agency_colors.get(col, "#AAAAAA") for col in pivot.columns]

    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor("#0F1117")
    ax.set_facecolor("#141824")

    pivot.plot(
        kind="bar", stacked=True, ax=ax,
        color=colors, edgecolor="none", width=0.7
    )

    ax.set_title(
        "CTP FY2024–FY2029: Project Count by County, Stacked by Agency\n(Excludes Areawide/Statewide)",
        fontsize=13, fontweight="bold", color="white", pad=14
    )
    ax.set_xlabel("")
    ax.set_ylabel("Number of Projects", color="#AAAAAA", fontsize=11)
    ax.tick_params(axis="x", colors="#CCCCCC", labelsize=10, rotation=35)
    ax.tick_params(axis="y", colors="#AAAAAA", labelsize=10)
    ax.grid(axis="y", color="#2A2F45", linewidth=0.5, linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    legend = ax.legend(
        title="Agency", loc="upper right",
        frameon=True, framealpha=0.9,
        facecolor="#1A1E2E", edgecolor="#333",
        fontsize=9, title_fontsize=10
    )
    legend.get_title().set_color("white")
    for text in legend.get_texts():
        text.set_color("#DDDDDD")

    # Highlight Baltimore City bar
    if "Baltimore City" in pivot.index:
        idx = list(pivot.index).index("Baltimore City")
        ax.get_xticklabels()[idx].set_color("#E63946")
        ax.get_xticklabels()[idx].set_fontweight("bold")

    plt.tight_layout()
    plt.savefig("output/B_county_breakdown_by_agency.png", dpi=200, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()


# ── OPTION C ─────────────────────────────────────────────────────────────────
# Geographic scatter plot: all CTP projects plotted by lat/lon
# Colored by Transportation Business Unit
# Shows spatial concentration of investment across Maryland
# ─────────────────────────────────────────────────────────────────────────────
def statewide_project_map(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Columns are swapped in the raw data — fix here
    df = df.rename(columns={"Latitude": "lon_raw", "Longitude": "lat_raw"})
    df = df.dropna(subset=["lat_raw", "lon_raw"])

    # Filter to valid Maryland coordinate range
    df = df[
        (df["lat_raw"].between(37.5, 40.0)) &
        (df["lon_raw"].between(-79.5, -74.5))
    ]

    short_names = {
        "Maryland State Highway Administration": "SHA",
        "Maryland Transit Administration":       "MTA",
        "Maryland Port Administration":          "MPA",
        "Maryland Aviation Administration":      "MAA",
        "The Secretary's Office":                "Sec. Office",
        "Maryland Transportation Authority":     "MdTA",
        "Motor Vehicle Administration":          "MVA",
    }
    df["Agency"] = df["Transportation Business Unit"].map(short_names).fillna("Other")

    agency_style = {
        "SHA":        {"color": "#4A90D9", "size": 30,  "alpha": 0.7, "zorder": 2},
        "MTA":        {"color": "#E63946", "size": 60,  "alpha": 1.0, "zorder": 5},
        "MPA":        {"color": "#2A9D8F", "size": 40,  "alpha": 0.8, "zorder": 3},
        "MAA":        {"color": "#F4A261", "size": 40,  "alpha": 0.8, "zorder": 3},
        "MdTA":       {"color": "#A8DADC", "size": 30,  "alpha": 0.7, "zorder": 2},
        "MVA":        {"color": "#C77DFF", "size": 30,  "alpha": 0.7, "zorder": 2},
        "Sec. Office":{"color": "#888888", "size": 20,  "alpha": 0.5, "zorder": 1},
        "Other":      {"color": "#555555", "size": 15,  "alpha": 0.4, "zorder": 1},
    }

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor("#0F1117")
    ax.set_facecolor("#141824")

    for agency, s in agency_style.items():
        subset = df[df["Agency"] == agency]
        if subset.empty:
            continue
        ax.scatter(
            subset["lon_raw"], subset["lat_raw"],
            c=s["color"], s=s["size"], alpha=s["alpha"],
            zorder=s["zorder"], linewidths=0,
            label=f"{agency}  ({len(subset)})"
        )

    ax.set_title(
        "CTP FY2024–FY2029: All Projects — Maryland Statewide\nby Transportation Agency",
        fontsize=14, fontweight="bold", color="white", pad=14,
        path_effects=[pe.withStroke(linewidth=3, foreground="#0F1117")]
    )
    ax.set_xlabel("Longitude", color="#888", fontsize=9)
    ax.set_ylabel("Latitude", color="#888", fontsize=9)
    ax.tick_params(colors="#666", labelsize=8)
    ax.grid(True, color="#2A2F45", linewidth=0.4, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2A2F45")

    legend = ax.legend(
        loc="lower left", frameon=True, framealpha=0.9,
        facecolor="#1A1E2E", edgecolor="#333",
        fontsize=9, title="Agency", title_fontsize=10
    )
    legend.get_title().set_color("white")
    for text in legend.get_texts():
        text.set_color("#DDDDDD")

    # Annotate Baltimore City cluster
    ax.annotate(
        "Baltimore City\ncluster",
        xy=(-76.62, 39.30),
        xytext=(-75.6, 39.55),
        color="white", fontsize=9,
        arrowprops=dict(arrowstyle="->", color="#AAAAAA", lw=1),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1A1E2E", edgecolor="#555", alpha=0.9)
    )

    plt.tight_layout()
    plt.savefig("output/C_statewide_project_map.png", dpi=200, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()

# projects_by_agency(df_abc)
# county_breakdown_by_agency(df_abc)
# statewide_project_map(df_abc)
