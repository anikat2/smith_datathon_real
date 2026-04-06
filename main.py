import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import matplotlib.patheffects as pe
import matplotlib.patches as mpatches

os.makedirs("output", exist_ok=True)

load_dotenv()

df_commute = pd.read_csv(os.getenv("DF_PATH"))
df_ontime = pd.read_csv(os.getenv("DF2_PATH"))
df_road = pd.read_csv(os.getenv("DF3_PATH"))
df_projects = pd.read_csv(os.getenv("DF4_PATH"))
df_tod = pd.read_csv(os.getenv("DF5_PATH"))

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

def projects_by_agency(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    counts = (
        df["Transportation Business Unit"]
        .value_counts()
        .sort_values(ascending=True)
    )

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

    for bar, val in zip(bars, counts.values):
        ax.text(
            bar.get_width() + 8, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", ha="left", color="white", fontsize=10
        )

    ax.set_xlabel("Number of CTP Projects", color="#AAAAAA", fontsize=11)
    ax.set_title(
        "CTP FY2024-FY2029: Projects by Agency (Statewide)",
        fontsize=14, fontweight="bold", color="white", pad=14
    )
    ax.tick_params(colors="#AAAAAA", labelsize=10)
    ax.set_xlim(0, counts.max() * 1.12)
    ax.grid(axis="x", color="#2A2F45", linewidth=0.5, linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    mta_label = "Transit (MTA)"
    if mta_label in counts.index:
        ax.annotate(
            "<- Focus area for\nBaltimore TOD proposal",
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

def county_breakdown_by_agency(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

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
        "CTP FY2024-FY2029: Project Count by County, Stacked by Agency\n(Excludes Areawide/Statewide)",
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

    if "Baltimore City" in pivot.index:
        idx = list(pivot.index).index("Baltimore City")
        ax.get_xticklabels()[idx].set_color("#E63946")
        ax.get_xticklabels()[idx].set_fontweight("bold")

    plt.tight_layout()
    plt.savefig("output/B_county_breakdown_by_agency.png", dpi=200, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()

def statewide_project_map(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    df = df.rename(columns={"Latitude": "lon_raw", "Longitude": "lat_raw"})
    df = df.dropna(subset=["lat_raw", "lon_raw"])

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
        "CTP FY2024-FY2029: All Projects - Maryland Statewide\nby Transportation Agency",
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

def route_ontime():
    citylink_routes = {
        "Citylink BLUE":   69.2,
        "Citylink BROWN":  73.9,
        "Citylink GOLD":   76.7,
        "Citylink GREEN":  75.2,
        "Citylink LIME":   72.7,
        "Citylink NAVY":   68.0,
        "Citylink ORANGE": 70.3,
        "Citylink PINK":   76.3,
        "Citylink PURPLE": 79.5,
        "Citylink RED":    70.0,
        "Citylink SILVER": 70.7,
        "Citylink YELLOW": 73.1,
    }
    citylink_df = pd.DataFrame({
        "Route": list(citylink_routes.keys()),
        "On-Time Performance (%)": list(citylink_routes.values())
    })
    citylink_df = citylink_df.sort_values(by="On-Time Performance (%)", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#0F1117")
    ax.set_facecolor("#141824")

    bars = ax.barh(citylink_df["Route"], citylink_df["On-Time Performance (%)"],
                   color="#E63946", edgecolor="none", height=0.6)

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}%", va="center", ha="left", color="white", fontsize=9)

    ax.set_xlabel("On-Time Performance (%)", color="#AAAAAA", fontsize=11)
    ax.set_title("MTA Citylink Routes: On-Time Performance (2025 YTD)",
                 fontsize=14, fontweight="bold", color="white", pad=14)
    ax.set_xlim(0, 100)
    ax.grid(axis="x", color="#2A2F45", linewidth=0.5, linestyle="--", alpha=0.6)
    ax.tick_params(colors="#AAAAAA", labelsize=10)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    plt.savefig("output/D_citylink_ontime.png", bbox_inches="tight", dpi=300,
                facecolor=fig.get_facecolor())
    plt.close()

def tod_station_analysis(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    marc_penn = df[df["Rail Lines Served"].str.contains("MARC: Penn Line", na=False)].copy()

    score_cols = [
        "Transit Score", "Station Facility Score", "Parking Score",
        "Bike Access Score", "Ped Access Score", "TOD Zoning Score"
    ]
    for col in score_cols:
        marc_penn[col] = pd.to_numeric(marc_penn[col], errors="coerce")

    # Development Market is numeric 1-5: flip so low market = high opportunity
    marc_penn["Development Market"] = pd.to_numeric(marc_penn["Development Market"], errors="coerce")
    marc_penn["Dev Market Score"] = (6 - marc_penn["Development Market"]).fillna(2)

    # Fix ridership — stored as string with commas
    marc_penn["Weekday Ridership: MARC Penn"] = (
        marc_penn["Weekday Ridership: MARC Penn"]
        .astype(str).str.replace(",", "", regex=False)
    )
    marc_penn["Weekday Ridership: MARC Penn"] = pd.to_numeric(
        marc_penn["Weekday Ridership: MARC Penn"], errors="coerce"
    )

    # Opportunity score = high transit score + high dev market gap
    marc_penn["Opportunity Score"] = (
        marc_penn["Transit Score"].fillna(0) +
        marc_penn["Dev Market Score"] * 2
    )

    marc_penn = marc_penn.sort_values("Opportunity Score", ascending=False)

    # --- Plot 1: Scatter (Transit Score vs Dev Market Opportunity) ---
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor("#0F1117")

    ax1 = axes[0]
    ax1.set_facecolor("#141824")

    color_map = {5: "#E63946", 4: "#F4A261", 3: "#4A90D9", 2: "#2A9D8F", 1: "#888888"}
    colors = marc_penn["Dev Market Score"].map(color_map).fillna("#888888")

    ax1.scatter(
        marc_penn["Transit Score"],
        marc_penn["Dev Market Score"],
        c=colors,
        s=(marc_penn["Weekday Ridership: MARC Penn"].fillna(100) / 5).values,
        alpha=0.85,
        edgecolors="none",
        zorder=3
    )

    for _, row in marc_penn.iterrows():
        if pd.notna(row["Transit Score"]) and pd.notna(row["Dev Market Score"]):
            ax1.annotate(
                row["Station Name"],
                xy=(row["Transit Score"], row["Dev Market Score"]),
                xytext=(4, 4), textcoords="offset points",
                color="white", fontsize=7, alpha=0.85
            )

    ax1.set_xlabel("Transit Score", color="#AAAAAA", fontsize=11)
    ax1.set_ylabel("Development Opportunity\n(5=Weak market, 1=Strong market)", color="#AAAAAA", fontsize=10)
    ax1.set_title("MARC Penn: Transit Score vs TOD Opportunity\n(bubble size = weekday ridership)",
                  color="white", fontsize=12, fontweight="bold")
    ax1.tick_params(colors="#AAAAAA")
    ax1.grid(color="#2A2F45", linewidth=0.5, linestyle="--", alpha=0.5)
    for spine in ax1.spines.values():
        spine.set_visible(False)

    legend_items = [
        mpatches.Patch(color="#E63946", label="Weak market (high opportunity)"),
        mpatches.Patch(color="#F4A261", label="Emerging market"),
        mpatches.Patch(color="#4A90D9", label="Moderate market"),
        mpatches.Patch(color="#2A9D8F", label="Strong market"),
        mpatches.Patch(color="#888888", label="Very strong market"),
    ]
    ax1.legend(handles=legend_items, loc="lower right", fontsize=8,
               facecolor="#1A1E2E", edgecolor="#333", labelcolor="white")

    # --- Plot 2: Top stations ranked bar ---
    ax2 = axes[1]
    ax2.set_facecolor("#141824")

    top = marc_penn.head(10)
    bar_colors = [color_map.get(int(s), "#888888") for s in top["Dev Market Score"]]

    bars = ax2.barh(top["Station Name"], top["Opportunity Score"],
                    color=bar_colors, edgecolor="none", height=0.6)

    for bar, val in zip(bars, top["Opportunity Score"]):
        ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                 f"{val:.1f}", va="center", color="white", fontsize=9)

    ax2.set_xlabel("Opportunity Score", color="#AAAAAA", fontsize=10)
    ax2.set_title("Top MARC Penn Stations by TOD Opportunity",
                  color="white", fontsize=12, fontweight="bold")
    ax2.tick_params(colors="#AAAAAA", labelsize=9)
    ax2.grid(axis="x", color="#2A2F45", linewidth=0.5, linestyle="--", alpha=0.5)
    ax2.invert_yaxis()
    for spine in ax2.spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    plt.savefig("output/E_tod_opportunity.png", dpi=200, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()

    # --- Save ranked table ---
    output_cols = [
        "Station Name", "Jurisdiction", "TOD Place Type",
        "Development Market", "Transit Score", "TOD Zoning Score",
        "Opportunity Score", "Weekday Ridership: MARC Penn"
    ]
    export_cols = [c for c in output_cols if c in marc_penn.columns]
    marc_penn[export_cols].to_csv("output/tod_station_rankings.csv", index=False)
    print(marc_penn[export_cols].head(10).to_string(index=False))


commute_data(df_commute)
on_time(df_ontime)
road_closure_data(df_road)
projects_by_agency(df_projects)
county_breakdown_by_agency(df_projects)
statewide_project_map(df_projects)
route_ontime()
tod_station_analysis(df_tod)