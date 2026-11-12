
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



st.set_page_config(
    page_title="Indian Startups Analysis",
    # page_icon="📊",
    layout="wide"
)


# 2. LOAD DATA


@st.cache_data
def load_data():
    data = pd.read_csv(
        "startup_funding.csv",
        encoding="utf-8"
    )

    data.columns = data.columns.str.strip()

    # Remove Remarks if available
    if "Remarks" in data.columns:
        data.drop(columns=["Remarks"], inplace=True)

    # Rename columns
    data.rename(
        columns={
            "Date dd/mm/yyyy": "Date",
            "Industry Vertical": "Vertical",
            "SubVertical": "Sub Vertical",
            "City  Location": "Location",
            "Amount in USD": "Amount",
            "InvestmentnType": "Round"
        },
        inplace=True
    )

    # Clean funding amount
    data["Amount"] = (
        data["Amount"]
        .fillna("0")
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("+", "", regex=False)
        .str.strip()
    )

    data["Amount"] = data["Amount"].replace(
        to_replace=r"^(undisclosed|unknown|n/a|nan|)$",
        value="0",
        regex=True
    )

    data["Amount"] = pd.to_numeric(
        data["Amount"],
        errors="coerce"
    ).fillna(0)

    # Convert USD amount to INR crore
    data["Amount"] = (
        data["Amount"] * 96.25
    ) / 10000000

    # Clean date strings
    data["Date"] = (
        data["Date"]
        .astype(str)
        .str.strip()
        .str.replace(".", "/", regex=False)
        .str.replace("//", "/", regex=False)
        .replace({
            "05/072018": "05/07/2018",
            "01/07/015": "01/07/2015"
        })
    )

    data["Date"] = pd.to_datetime(
        data["Date"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    # Clean text columns
    text_columns = [
        "Startup Name",
        "Investors Name",
        "Vertical",
        "Sub Vertical",
        "Location",
        "Round"
    ]

    for column in text_columns:
        if column in data.columns:
            data[column] = (
                data[column]
                .astype("string")
                .str.strip()
            )

    # Fill missing investor names
    data["Investors Name"] = (
        data["Investors Name"]
        .fillna("Undisclosed")
    )

    # Clean startup names
    data["Startup Name"] = (
        data["Startup Name"]
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.title()
    )

    data["Startup Name"] = (
        data["Startup Name"]
        .str.replace(".Com", "", regex=False)
    )

    data["Startup Name"] = (
        data["Startup Name"]
        .replace({
            "Ola Cabs": "Ola",
            "Ola Cab": "Ola",
            "Rapido Bike Taxi": "Rapido",
            'Byju\\\\xe2\\\\x80\\\\x99s':"Byju’S",
            'Byju\\\\xe2\\\\x80\\\\x99s':"Byju’S",
            'Byju\\\\Xe2\\\\x80\\\\x99s':"Byju’S",
            'Byju\\\\Xe2\\\\X80\\\\X99S':"Byju’S"
        })
    )

    # Remove rows without a startup name
    data = data.dropna(
        subset=["Startup Name"]
    ).copy()

    data = data.drop(data.index[67])
    
    # Clean funding rounds
    data["Round"] = (
        data["Round"]
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.title()
    )

    round_mapping = {
        "Seed Funding": "Seed",
        "Seed Round": "Seed",
        "Seed Funding Round": "Seed",
        "Seed / Angel Funding": "Seed/Angel",
        "Seed/ Angel Funding": "Seed/Angel",
        "Seed/Angel Funding": "Seed/Angel",
        "Seed / Angle Funding": "Seed/Angel",
        "Angel / Seed Funding": "Seed/Angel",
        "Private Equity Round": "Private Equity",
        "Privateequity": "Private Equity",
        "Venture Round": "Venture",
        "Single Venture": "Venture",
        "Venture - Series Unknown": "Venture",
        "Debt Funding": "Debt",
        "Debt-Funding": "Debt",
        "Structured Debt": "Debt",
        "Debt And Preference Capital": "Debt",
        "Term Loan": "Debt",
        "Pre Series A": "Pre-Series A",
        "Equity Based Funding": "Equity",
        "Series B (Extension)": "Series B"
    }

    data["Round"] = data["Round"].replace(
        round_mapping
    )

    # Create year column
    data["Year"] = data["Date"].dt.year

    # Clean investor names for analysis
    data["Investors Name"] = (
        data["Investors Name"]
        .str.replace("\u00a0", " ", regex=False)
        .str.strip()
    )

    return data


df = load_data()


# 3. GENERAL SETTINGS


COLORS = [
    "#6C4DD8",
    "#2A9D8F",
    "#F4A261",
    "#E76F51",
    "#457B9D",
    "#8AB17D",
    "#E9C46A",
    "#B56576",
    "#9A8C98",
    "#4D908E"
]


def short(label, n=25):
    """Shorten long labels for readable charts."""
    label = str(label)

    if len(label) <= n:
        return label

    return label[:n - 1] + "…"


def clean_axes(ax):
    """Improve chart appearance."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.25
    )
    ax.set_axisbelow(True)


def money_format(value):
    return f"₹ {value:,.2f} Cr"



# 4. PIE CHART FUNCTION


def nice_pie(series, top_n=6, title=None):
    """
    Display top categories and combine remaining
    categories into Others.
    """

    series = series.dropna()
    series = series[series > 0]
    series = series.sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))

    if series.empty:
        ax.text(
            0.5, 0.5,
            "No data available",
            ha="center",
            va="center"
        )
        ax.axis("off")
        return fig

    if len(series) > top_n:
        others_value = series.iloc[top_n:].sum()

        series = pd.concat([
            series.iloc[:top_n],
            pd.Series({"Others": others_value})
        ])

    total = series.sum()

    colors = [
        COLORS[i % len(COLORS)]
        for i in range(len(series))
    ]

    if "Others" in series.index:
        colors[list(series.index).index("Others")] = "#BBBBBB"

    wedges, _, autotexts = ax.pie(
        series.values,
        startangle=90,
        counterclock=False,
        colors=colors,
        autopct=lambda p: f"{p:.1f}%" if p >= 5 else "",
        pctdistance=0.70,
        wedgeprops={
            "edgecolor": "white",
            "linewidth": 1.5
        }
    )

    for text in autotexts:
        text.set_color("white")
        text.set_fontsize(9)
        text.set_fontweight("bold")

    legend_labels = [
        f"{short(label, 25)} ({value / total:.1%})"
        for label, value in series.items()
    ]

    ax.legend(
        wedges,
        legend_labels,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        frameon=False,
        fontsize=9
    )

    if title:
        ax.set_title(title)

    ax.axis("equal")
    fig.tight_layout()

    return fig



# 5. YEAR CHART FUNCTION


def year_chart(series, ylabel, kind="line", title=None):
    series = series.dropna().sort_index()

    fig, ax = plt.subplots(figsize=(9, 4.5))

    if series.empty:
        ax.text(
            0.5, 0.5,
            "No data available",
            ha="center",
            va="center"
        )
        ax.axis("off")
        return fig

    x = series.index.astype(int)
    values = series.values

    if kind == "line":
        ax.plot(
            x,
            values,
            marker="o",
            linewidth=2,
            color=COLORS[0]
        )

        for xi, yi in zip(x, values):
            ax.annotate(
                f"{yi:,.0f}",
                (xi, yi),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=8
            )

    else:
        bars = ax.bar(
            x,
            values,
            color=COLORS[0],
            width=0.6
        )

        ax.bar_label(
            bars,
            labels=[f"{v:,.0f}" for v in values],
            padding=3,
            fontsize=8
        )

    ax.set_xticks(x)
    ax.set_xticklabels([str(year) for year in x])

    if len(values) and max(values) > 0:
        ax.set_ylim(0, max(values) * 1.20)

    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)

    if title:
        ax.set_title(title)

    clean_axes(ax)
    fig.tight_layout()

    return fig



# 6. HORIZONTAL BAR CHART


def horizontal_bar(
    series,
    title,
    xlabel,
    top_n=10
):
    series = series.dropna()
    series = series.sort_values(
        ascending=False
    ).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 5))

    if series.empty:
        ax.text(
            0.5, 0.5,
            "No data available",
            ha="center",
            va="center"
        )
        ax.axis("off")
        return fig

    series = series.sort_values(ascending=True)

    bars = ax.barh(
        [short(label, 32) for label in series.index],
        series.values,
        color=COLORS[1]
    )

    ax.bar_label(
        bars,
        labels=[f"{value:,.1f}" for value in series.values],
        padding=3,
        fontsize=8
    )

    ax.set_title(title)
    ax.set_xlabel(xlabel)

    if series.max() > 0:
        ax.set_xlim(0, series.max() * 1.20)

    clean_axes(ax)
    fig.tight_layout()

    return fig



# 7. INVESTOR DATA PREPARATION


investor_df = df[
    ["Startup Name", "Investors Name", "Amount",
     "Date", "Vertical", "Round", "Location", "Year"]
].copy()

investor_df["Investor"] = (
    investor_df["Investors Name"]
    .fillna("Undisclosed")
    .astype(str)
    .str.split(",")
)

# investor_df['Investors Name'] = 
investor_df = investor_df.explode("Investor")

investor_df["Investor"] = (
    investor_df["Investor"]
    .astype(str)
    .str.strip()
)

investor_df = investor_df[
    investor_df["Investor"].ne("")
].copy()

unique_investors = sorted(
    investor_df["Investor"].dropna().unique().tolist()
)



# 8. STARTUP ANALYSIS


def load_startup(company):

    st.title(company)

    # Exact match avoids mixing similarly named startups
    company_df = df[
        df["Startup Name"].eq(company)
    ].copy()

    company_df["Year"] = pd.to_numeric(
        company_df["Year"],
        errors="coerce"
    )

    company_df["Amount"] = pd.to_numeric(
        company_df["Amount"],
        errors="coerce"
    )

    years = sorted(
        company_df["Year"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    if not years:
        st.warning(
            "No year data available for this startup."
        )
        return

    # IMPORTANT: year selection triggers Streamlit rerun.
    # Every selected-year section below uses current_df.
    year = st.selectbox(
        "Choose Year:",
        years,
        index=len(years) - 1,
        key=f"startup_year_{company}"
    )

    current_df = company_df[
        company_df["Year"] == year
    ].copy()

    previous_df = company_df[
        company_df["Year"] == year - 1
    ].copy()

    if current_df.empty:
        st.warning(
            f"No funding data available for {year}."
        )
        return

    st.caption(
        f"Showing {len(current_df)} funding record(s) "
        f"for {company} in {year}."
    )

    # A. FUNDING OVERVIEW
   

    st.subheader(f"Funding Overview — {year}")

    metrics = {
        "Total Investment": "sum",
        "Mean Investment": "mean",
        "Maximum Investment": "max",
        "Minimum Investment": "min"
    }

    cols = st.columns(4)

    for col, (label, operation) in zip(
        cols,
        metrics.items()
    ):

        current_amount = current_df["Amount"].dropna()
        previous_amount = previous_df["Amount"].dropna()

        current_value = (
            getattr(current_amount, operation)()
            if not current_amount.empty
            else np.nan
        )

        previous_value = (
            getattr(previous_amount, operation)()
            if not previous_amount.empty
            else np.nan
        )

        delta = None

        if (
            not pd.isna(current_value)
            and not pd.isna(previous_value)
            and previous_value != 0
        ):
            change = (
                (current_value - previous_value)
                / abs(previous_value)
            ) * 100

            delta = f"{change:+.2f}%"

        with col:
            if pd.isna(current_value):
                st.metric(label, "N/A")
            else:
                st.metric(
                    label,
                    money_format(current_value),
                    delta=delta,
                    help=(
                        f"Percentage change compared "
                        f"with {year - 1}"
                    )
                )

    st.caption(
        f"Year-over-year comparison: {year} vs {year - 1}. "
        "Delta is hidden when previous-year data is missing "
        "or zero."
    )

    # -----------------------------------------------------
    # B. INVESTING PARTNERS — SELECTED YEAR
    # -----------------------------------------------------

    st.markdown(f"### Investing Partners — {year}")

    selected_investors = (
        current_df["Investors Name"]
        .dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
    )

    selected_investors = (
        selected_investors[
            selected_investors.ne("")
        ]
        .drop_duplicates()
        .sort_values()
    )

    if not selected_investors.empty:
        st.dataframe(
            pd.DataFrame({
                "Investors Name": selected_investors
            }),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info(
            f"No investor names available for {year}."
        )

    # -----------------------------------------------------
    # C. YEARLY FUNDING TREND — ALL YEARS
    # -----------------------------------------------------

    st.markdown("### Yearly Funding Trend — All Years")

    yearly_funding = (
        company_df.dropna(subset=["Year"])
        .groupby("Year")["Amount"]
        .sum()
        .sort_index()
    )

    if not yearly_funding.empty:

        fig = year_chart(
            yearly_funding,
            "Funding (₹ Cr)",
            kind="line",
            title=f"{company}: Yearly Funding Trend"
        )

        st.pyplot(fig)
        plt.close(fig)

    # D. FUNDING BY ROUND — SELECTED YEAR

    st.markdown(f"### Funding By Rounds — {year}")

    round_funding = (
        current_df.dropna(subset=["Round"])
        .groupby("Round")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    if not round_funding.empty:

        col1, col2 = st.columns([1, 1])

        with col1:
            fig = nice_pie(
                round_funding,
                top_n=6,
                title=f"Funding Share by Round — {year}"
            )

            st.pyplot(fig)
            plt.close(fig)

        with col2:
            fig = horizontal_bar(
                round_funding,
                title=f"Funding by Round — {year}",
                xlabel="Funding (₹ Cr)",
                top_n=10
            )

            st.pyplot(fig)
            plt.close(fig)

        st.dataframe(
            round_funding.reset_index(name="Amount"),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Amount": st.column_config.NumberColumn(
                    "Funding (₹ Cr)",
                    format="₹ %.2f Cr"
                )
            }
        )

    else:
        st.info(
            f"No funding-round information for {year}."
        )

    # -----------------------------------------------------
    # E. FUNDING FREQUENCY — SELECTED YEAR
    # -----------------------------------------------------

    st.markdown(
        f"### Funding Frequency by Round — {year}"
    )

    frequency = (
        current_df.dropna(subset=["Round"])
        .groupby("Round")
        .size()
        .reset_index(name="Funding Rounds")
        .sort_values(
            "Funding Rounds",
            ascending=False
        )
    )

    if not frequency.empty:

        st.dataframe(
            frequency,
            hide_index=True,
            use_container_width=True
        )

        frequency_plot = (
            frequency
            .set_index("Round")["Funding Rounds"]
        )

        fig = horizontal_bar(
            frequency_plot,
            title=f"Number of Funding Rounds — {year}",
            xlabel="Number of Rounds",
            top_n=10
        )

        st.pyplot(fig)
        plt.close(fig)

    else:
        st.info(
            f"No funding frequency data available for {year}."
        )

    
    # F. FUNDING DETAILS — SELECTED YEAR
   

    st.markdown(f"### Funding Details — {year}")

    latest_columns = [
        "Date",
        "Startup Name",
        "Vertical",
        "Investors Name",
        "Location",
        "Round",
        "Amount"
    ]

    latest = current_df[
        latest_columns
    ].sort_values(
        by="Date",
        ascending=False
    )

    st.dataframe(
        latest,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Date": st.column_config.DateColumn(
                "Date",
                format="DD-MM-YYYY"
            ),
            "Amount": st.column_config.NumberColumn(
                "Amount (₹ Cr)",
                format="₹ %.2f Cr"
            )
        }
    )

    # -----------------------------------------------------
    # G. FUNDING BY CITY — SELECTED YEAR
    # -----------------------------------------------------

    st.markdown(f"### Total Funding By City — {year}")

    city_funding = (
        current_df.dropna(subset=["Location"])
        .groupby("Location")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    if not city_funding.empty:

        st.dataframe(
            city_funding.reset_index(),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Amount": st.column_config.NumberColumn(
                    "Amount (₹ Cr)",
                    format="₹ %.2f Cr"
                )
            }
        )

        fig = horizontal_bar(
            city_funding,
            title=f"Top Cities by Funding — {year}",
            xlabel="Funding (₹ Cr)",
            top_n=10
        )

        st.pyplot(fig)
        plt.close(fig)

    else:
        st.info(
            f"No city-wise funding data available for {year}."
        )



# 9. INVESTOR ANALYSIS


def load_investor(investor):

    st.title(investor)

    # Exact investor match
    selected_df = investor_df[
        investor_df["Investor"].str.casefold()
        == investor.casefold()
    ].copy()

    if selected_df.empty:
        st.warning(
            "No investment records found for this investor."
        )
        return

    # A. INVESTOR OVERVIEW


    st.subheader("Investor Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Investment",
            money_format(selected_df["Amount"].sum())
        )

    with col2:
        st.metric(
            "Startups Funded",
            selected_df["Startup Name"].nunique()
        )

    with col3:
        st.metric(
            "Investment Records",
            len(selected_df)
        )

    # -----------------------------------------------------
    # B. RECENT INVESTMENTS
    # -----------------------------------------------------

    st.markdown("### Recent Investments")

    details = (
        selected_df[
            [
                "Date",
                "Startup Name",
                "Vertical",
                "Round",
                "Amount"
            ]
        ]
        .sort_values("Date", ascending=False)
        .head(10)
    )

    st.dataframe(
        details,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Date": st.column_config.DateColumn(
                "Date",
                format="DD-MM-YYYY"
            ),
            "Amount": st.column_config.NumberColumn(
                "Funding (₹ Cr)",
                format="₹ %.2f Cr"
            )
        }
    )

    # -----------------------------------------------------
    # C. BIGGEST STARTUP INVESTMENTS
    # -----------------------------------------------------

    biggest = (
        selected_df.groupby("Startup Name")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Biggest Investments")

        fig = horizontal_bar(
            biggest,
            title="Top Startups by Investment",
            xlabel="Investment (₹ Cr)",
            top_n=10
        )

        st.pyplot(fig)
        plt.close(fig)

        # D. SECTORS OF INVESTMENT

    sector_funding = (
        selected_df.dropna(subset=["Vertical"])
        .groupby("Vertical")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    with col2:
        st.markdown("### Sectors of Investment")

        fig = nice_pie(
            sector_funding,
            top_n=6,
            title="Sector Funding Share"
        )

        st.pyplot(fig)
        plt.close(fig)

    
    # E. FUNDING ROUND BREAKDOWN
    
    col3, col4 = st.columns(2)

    stages = (
        selected_df.dropna(subset=["Round"])
        .groupby("Round")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    with col3:
        st.markdown("### Funding Stage Breakdown")

        fig = nice_pie(
            stages,
            top_n=6,
            title="Investment by Round"
        )

        st.pyplot(fig)
        plt.close(fig)

    # -----------------------------------------------------
    # F. CITY BREAKDOWN
    # -----------------------------------------------------

    cities = (
        selected_df.dropna(subset=["Location"])
        .groupby("Location")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    with col4:
        st.markdown("### Investment by City")

        fig = horizontal_bar(
            cities,
            title="Top Cities",
            xlabel="Investment (₹ Cr)",
            top_n=10
        )

        st.pyplot(fig)
        plt.close(fig)

    # -----------------------------------------------------
    # G. YEAR-ON-YEAR INVESTMENT
    # -----------------------------------------------------

    st.markdown("### Year-on-Year Investment")

    yearly_investment = (
        selected_df.dropna(subset=["Year"])
        .groupby("Year")["Amount"]
        .sum()
        .sort_index()
    )

    if not yearly_investment.empty:

        fig = year_chart(
            yearly_investment,
            "Investment (₹ Cr)",
            kind="line",
            title="Year-on-Year Investment Trend"
        )

        st.pyplot(fig)
        plt.close(fig)

    # -----------------------------------------------------
    # H. INVESTMENT DETAILS BY STARTUP
    # -----------------------------------------------------

    st.markdown("### Startup Investment Details")

    startup_details = (
        selected_df.groupby("Startup Name")
        .agg(
            Total_Investment=("Amount", "sum"),
            Funding_Records=("Amount", "count"),
            Latest_Investment=("Date", "max")
        )
        .sort_values(
            "Total_Investment",
            ascending=False
        )
        .reset_index()
    )

    st.dataframe(
        startup_details,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Total_Investment": st.column_config.NumberColumn(
                "Total Investment (₹ Cr)",
                format="₹ %.2f Cr"
            ),
            "Latest_Investment": st.column_config.DateColumn(
                "Latest Investment",
                format="DD-MM-YYYY"
            )
        }
    )


# =========================================================
# 10. OVERALL ANALYSIS
# =========================================================

def load_overall():

    st.title("Overall Analysis")

    # -----------------------------------------------------
    # A. KEY METRICS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Startups",
            f"{df['Startup Name'].nunique():,}"
        )

    with col2:
        st.metric(
            "Total Investors",
            f"{len(unique_investors):,}"
        )

    with col3:
        st.metric(
            "Total Funding",
            money_format(df["Amount"].sum())
        )

    with col4:
        st.metric(
            "Maximum Funding Record",
            money_format(df["Amount"].max())
        )

    # -----------------------------------------------------
    # B. YEAR-WISE FUNDING TREND
    # -----------------------------------------------------

    st.markdown("### Year-wise Funding Trend")

    yearly_funding = (
        df.dropna(subset=["Year"])
        .groupby("Year")["Amount"]
        .sum()
        .sort_index()
    )

    fig = year_chart(
        yearly_funding,
        "Funding (₹ Cr)",
        kind="line",
        title="Total Startup Funding by Year"
    )

    st.pyplot(fig)
    plt.close(fig)

    # -----------------------------------------------------
    # C. YEAR-WISE FUNDING ROUNDS
    # -----------------------------------------------------

    st.markdown("### Year-wise Number of Funding Records")

    yearly_rounds = (
        df.dropna(subset=["Year"])
        .groupby("Year")
        .size()
    )

    fig = year_chart(
        yearly_rounds,
        "Funding Records",
        kind="bar",
        title="Funding Records by Year"
    )

    st.pyplot(fig)
    plt.close(fig)

    # -----------------------------------------------------
    # D. TOP STARTUPS BY FUNDING
    # -----------------------------------------------------

    st.markdown("### Top 10 Startups by Total Funding")

    top_startups = (
        df.groupby("Startup Name")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig = horizontal_bar(
        top_startups,
        title="Top Funded Startups",
        xlabel="Total Funding (₹ Cr)",
        top_n=10
    )

    st.pyplot(fig)
    plt.close(fig)

    # -----------------------------------------------------
    # E. TOP INDUSTRIES BY FUNDING
    # -----------------------------------------------------

    st.markdown("### Top Industries by Funding")

    industry_funding = (
        df.dropna(subset=["Vertical"])
        .groupby("Vertical")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    col1, col2 = st.columns([1.3, 1])

    with col1:
        fig = horizontal_bar(
            industry_funding,
            title="Top 10 Industries by Funding",
            xlabel="Funding (₹ Cr)",
            top_n=10
        )

        st.pyplot(fig)
        plt.close(fig)

    # -----------------------------------------------------
    # F. TOP INDUSTRIES BY NUMBER OF RECORDS
    # -----------------------------------------------------

    industry_records = (
        df.dropna(subset=["Vertical"])
        .groupby("Vertical")
        .size()
        .sort_values(ascending=False)
    )

    with col2:
        fig = horizontal_bar(
            industry_records,
            title="Top Industries by Funding Records",
            xlabel="Number of Records",
            top_n=10
        )

        st.pyplot(fig)
        plt.close(fig)

    # -----------------------------------------------------
    # G. FUNDING ROUND DISTRIBUTION
    # -----------------------------------------------------

    st.markdown("### Funding Round Distribution")

    round_distribution = (
        df.dropna(subset=["Round"])
        .groupby("Round")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        fig = nice_pie(
            round_distribution,
            top_n=7,
            title="Funding Share by Round"
        )

        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig = horizontal_bar(
            round_distribution,
            title="Funding by Round",
            xlabel="Funding (₹ Cr)",
            top_n=10
        )

        st.pyplot(fig)
        plt.close(fig)

    
    # H. TOP CITIES BY FUNDING
    

    st.markdown("### Top Cities by Funding")

    city_funding = (
        df.dropna(subset=["Location"])
        .groupby("Location")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    fig = horizontal_bar(
        city_funding,
        title="Top 10 Cities by Funding",
        xlabel="Funding (₹ Cr)",
        top_n=10
    )

    st.pyplot(fig)
    plt.close(fig)

    
    # I. LATEST FUNDING RECORDS
   

    st.markdown("### Latest Funding Records")

    latest_columns = [
        "Date",
        "Startup Name",
        "Vertical",
        "Investors Name",
        "Location",
        "Round",
        "Amount"
    ]

    latest = (
        df[latest_columns]
        .sort_values("Date", ascending=False)
        .head(20)
    )

    st.dataframe(
        latest,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Date": st.column_config.DateColumn(
                "Date",
                format="DD-MM-YYYY"
            ),
            "Amount": st.column_config.NumberColumn(
                "Funding (₹ Cr)",
                format="₹ %.2f Cr"
            )
        }
    )


# 11. SIDEBAR NAVIGATION


st.sidebar.title("Indian Startups Analysis")

choice = st.sidebar.selectbox(
    "Choose Your Analysis Type:",
    [
        "Overall Analysis",
        "Startup Analysis",
        "Investor Analysis"
    ],
    index=None,
    placeholder="Select Analysis:"
)



# 12. RUN SELECTED ANALYSIS


if choice is None:

    st.title("Welcome to Indian Startups Analysis")

    st.write(
        "Select an analysis type from the sidebar "
        "to explore Indian startup funding data."
    )

    st.info(
        "Choose Overall Analysis, Startup Analysis "
        "or Investor Analysis from the sidebar."
    )


elif choice == "Overall Analysis":

    load_overall()


elif choice == "Startup Analysis":

    startup_names = sorted(
        df["Startup Name"]
        .dropna()
        .unique()
        .tolist()
    )

    startup = st.sidebar.selectbox(
        "Choose Startup:",
        startup_names,
        index=None,
        placeholder="Select a startup:"
    )

    # No Search button condition here.
    # Selecting a year reruns load_startup automatically.
    if startup:
        load_startup(startup)


elif choice == "Investor Analysis":

    selected = st.sidebar.selectbox(
        "Choose Investor:",
        unique_investors,
        index=None,
        placeholder="Select an investor:"
    )

    if selected:
        load_investor(selected)
