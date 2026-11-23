import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from html import escape

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Real Estate Buyer Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# PATHS & DATA LOADING
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "reports"

@st.cache_data
def load_data():
    clients = pd.read_csv(DATA_DIR / "clients_cleaned.csv")
    properties = pd.read_csv(DATA_DIR / "properties_cleaned.csv")

    monthly_sales = pd.read_csv(REPORT_DIR / "monthly_sales.csv")
    property_categories = pd.read_csv(REPORT_DIR / "property_categories.csv")
    buyer_purpose = pd.read_csv(REPORT_DIR / "buyer_purpose.csv")
    cluster_summary = pd.read_csv(REPORT_DIR / "buyer_cluster_summary.csv")
    cluster_evaluation = pd.read_csv(REPORT_DIR / "cluster_evaluation.csv")
    buyer_segments = pd.read_csv(REPORT_DIR / "buyer_segments.csv")

    return (
        clients,
        properties,
        monthly_sales,
        property_categories,
        buyer_purpose,
        cluster_summary,
        cluster_evaluation,
        buyer_segments,
    )

try:
    (
        clients,
        properties,
        monthly_sales,
        property_categories,
        buyer_purpose,
        cluster_summary,
        cluster_evaluation,
        buyer_segments,
    ) = load_data()
except FileNotFoundError as error:
    st.error(f"Required project file not found: {error}")
    st.info(
        "Please run the data preprocessing, business analysis, "
        "and buyer segmentation scripts before launching the dashboard."
    )
    st.stop()

# --------------------------------------------------
# EMERALD LUXURY THEME (UI ONLY)
# Styling lives in styles.css next to this file.
# --------------------------------------------------
STYLES_PATH = BASE_DIR / "styles.css"

def load_styles():
    try:
        css = STYLES_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        css = ""
        st.warning("styles.css not found - the dashboard is using default styling.")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_styles()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.markdown("## 🏙️ REI Intelligence")
st.sidebar.caption("Real Estate Analytics Platform")
st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Sales Analytics",
        "Buyer Insights",
        "Buyer Segmentation",
        "Investor Behavior",
        "Geographic Buyer Analysis",
        "Segment Insights Panel",
    ]
)

st.sidebar.divider()
st.sidebar.caption("DATA ANALYST INTERNSHIP PROJECT")
st.sidebar.caption("Market Intelligence • 2024–2025")

# Required PRD filters. Selections are applied to buyer and segment-level views.
st.sidebar.markdown("### Buyer Filters")
def sidebar_multiselect(label, series):
    options = sorted(series.dropna().astype(str).unique().tolist())
    return st.sidebar.multiselect(label, options, default=options)

country_filter = sidebar_multiselect("Country", clients["country"]) if "country" in clients else []
region_filter = sidebar_multiselect("Region", clients["region"]) if "region" in clients else []
purpose_filter = sidebar_multiselect("Acquisition Purpose", clients["acquisition_purpose"]) if "acquisition_purpose" in clients else []
client_type_filter = sidebar_multiselect("Client Type", clients["client_type"]) if "client_type" in clients else []

filtered_clients = clients.copy()
for col, selected in [
    ("country", country_filter),
    ("region", region_filter),
    ("acquisition_purpose", purpose_filter),
    ("client_type", client_type_filter),
]:
    if col in filtered_clients.columns and selected:
        filtered_clients = filtered_clients[filtered_clients[col].astype(str).isin(selected)]
    elif col in filtered_clients.columns and not selected:
        filtered_clients = filtered_clients.iloc[0:0]

filtered_buyer_segments = buyer_segments.copy()
for col, selected in [
    ("country", country_filter),
    ("region", region_filter),
    ("acquisition_purpose", purpose_filter),
    ("client_type", client_type_filter),
]:
    if col in filtered_buyer_segments.columns and selected:
        filtered_buyer_segments = filtered_buyer_segments[filtered_buyer_segments[col].astype(str).isin(selected)]
    elif col in filtered_buyer_segments.columns and not selected:
        filtered_buyer_segments = filtered_buyer_segments.iloc[0:0]


# --------------------------------------------------
# COMMON HELPERS
# --------------------------------------------------
def format_currency(value):
    return f"${value / 1_000_000_000:.2f}B"

# Emerald Luxury palette (presentation only)
EMERALD_COLORWAY = [
    "#10B981", "#D6B36A", "#A7F3D0", "#B88A44",
    "#34D399", "#E8D3A0", "#5E8C7A", "#F5F7F5",
]
EMERALD_SCALE = [
    [0.0, "#0B2B22"], [0.35, "#0E7A5A"], [0.7, "#10B981"], [1.0, "#E8D3A0"],
]
TEXT_PRIMARY = "#F5F7F5"
TEXT_SECONDARY = "#A7B8AE"
GRID_COLOR = "rgba(255,255,255,0.07)"
AXIS_LINE = "rgba(255,255,255,0.12)"

# Default template so px figures are created with the emerald palette.
px.defaults.template = go.layout.Template(
    layout=dict(
        colorway=EMERALD_COLORWAY,
        colorscale=dict(sequential=EMERALD_SCALE),
        font=dict(color=TEXT_SECONDARY, family="Inter, sans-serif"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
)

def show_chart(fig, **kwargs):
    """Render a Plotly figure using the custom emerald template (theme=None)."""
    kwargs.setdefault("theme", None)
    st.plotly_chart(fig, **kwargs)

def style_chart(fig, height=350):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_SECONDARY, family="Inter, sans-serif"),
        margin=dict(l=15, r=15, t=45, b=15),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT_SECONDARY),
            title_font=dict(color="#E8D3A0"),
        ),
        title_font=dict(size=16, color=TEXT_PRIMARY),
        hoverlabel=dict(
            bgcolor="#0B2B22",
            bordercolor="#D6B36A",
            font=dict(color=TEXT_PRIMARY, family="Inter, sans-serif"),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=AXIS_LINE,
        tickfont=dict(color=TEXT_SECONDARY),
        title_font=dict(color=TEXT_SECONDARY),
    )
    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        zeroline=False,
        tickfont=dict(color=TEXT_SECONDARY),
        title_font=dict(color=TEXT_SECONDARY),
    )
    if any(getattr(trace, "type", "") == "choropleth" for trace in fig.data):
        fig.update_geos(
            bgcolor="rgba(0,0,0,0)",
            landcolor="rgba(16,61,48,0.55)",
            subunitcolor="rgba(255,255,255,0.15)",
            showlakes=False,
        )
        fig.update_coloraxes(
            colorbar=dict(
                tickfont=dict(color=TEXT_SECONDARY),
                title_font=dict(color=TEXT_SECONDARY),
            )
        )
    return fig

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-eyebrow">Buyer Segmentation &amp; Investment Profiling</div>
        <div class="hero-title">REAL ESTATE MARKET INTELLIGENCE</div>
        <div class="hero-subtitle">
            Buyer behaviour · Sales performance · Property analytics ·
            Machine learning based segmentation
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------
if page == "Overview":

    total_listings = len(properties)
    sold_properties = properties[
        properties["listing_status"].astype(str).str.lower() == "sold"
    ]
    available_properties = properties[
        properties["listing_status"].astype(str).str.lower() == "available"
    ]

    total_sales_value = pd.to_numeric(
        sold_properties["sale_price"], errors="coerce"
    ).sum()

    avg_sold_price = pd.to_numeric(
        sold_properties["sale_price"], errors="coerce"
    ).mean()

    sale_rate = (
        len(sold_properties) / total_listings * 100
        if total_listings else 0
    )

    st.markdown('<div class="section-heading">Market Performance Overview</div>',
                unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("TOTAL LISTINGS", f"{total_listings:,}")
    k2.metric("SOLD PROPERTIES", f"{len(sold_properties):,}")
    k3.metric("AVAILABLE", f"{len(available_properties):,}")
    k4.metric("TOTAL SALES VALUE", format_currency(total_sales_value))

    st.caption(
        f"Recorded sell-through rate: {sale_rate:.2f}%  ·  "
        f"Average sold property price: ${avg_sold_price:,.0f}"
    )

    left, right = st.columns([1.6, 1])

    with left:
        st.markdown("#### Monthly Sales Trend")

        trend = monthly_sales.copy()
        trend["transaction_month"] = pd.to_datetime(
    trend["transaction_month"], errors="coerce"
)
        trend = trend.dropna(subset=["transaction_month"]).sort_values("transaction_month")

        count_col = next(
            (c for c in ["properties_sold", "sold_count", "count", "property_count"]
             if c in trend.columns),
            None
        )

        if count_col:
            fig = px.line(
                trend,
                x= "transaction_month",
                y=count_col,
                markers=True,
                title="Properties Sold Over Time",
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=6))
            show_chart(style_chart(fig, 360), use_container_width=True)
        else:
            st.warning(f"Could not identify the sales-count column. Found: {list(trend.columns)}")

    with right:
        st.markdown("#### Listing Status")

        status_df = pd.DataFrame({
            "Status": ["Sold", "Available"],
            "Count": [len(sold_properties), len(available_properties)]
        })

        fig = px.pie(
            status_df,
            names="Status",
            values="Count",
            hole=0.68,
            title="Inventory Distribution"
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        show_chart(style_chart(fig, 360), use_container_width=True)

    st.markdown("#### Property Category Analysis")

    if {"unit_category", "listing_status"}.issubset(properties.columns):
        category_df = (
            properties.groupby(["unit_category", "listing_status"])
            .size()
            .reset_index(name="listing_count")
        )

        fig = px.bar(
            category_df,
            x="unit_category",
            y="listing_count",
            color="listing_status",
            barmode="group",
            title="Listings by Property Category",
            labels={
                "unit_category": "Property Category",
                "listing_count": "Number of Listings",
                "listing_status": "Status"
            }
        )
        show_chart(style_chart(fig, 300), use_container_width=True)

# --------------------------------------------------
# SALES ANALYTICS PAGE
# --------------------------------------------------
elif page == "Sales Analytics":

    st.markdown("### 📈 Sales Analytics")

    trend = monthly_sales.copy()
    trend["transaction_month"] = pd.to_datetime(
    trend["transaction_month"], errors="coerce"
)
    trend = trend.dropna(subset=["transaction_month"]).sort_values("transaction_month")

    count_col = next(
        (c for c in ["properties_sold", "sold_count", "count", "property_count"]
         if c in trend.columns),
        None
    )

    value_col = next(
        (c for c in ["total_sales_value", "sales_value", "total_sale_value"]
         if c in trend.columns),
        None
    )

    if count_col:
        fig = px.area(
            trend, x="transaction_month", y=count_col,
            title="Monthly Properties Sold",
            labels={count_col: "Properties Sold", "month": "Month"}
        )
        show_chart(style_chart(fig, 380), use_container_width=True)

    if value_col:
        fig = px.line(
            trend, x="transaction_month", y=value_col,
            markers=True,
            title="Monthly Sales Value",
            labels={value_col: "Sales Value ($)", "month": "Month"}
        )
        show_chart(style_chart(fig, 380), use_container_width=True)
    else:
        st.info("Monthly sales-value chart needs a sales-value column in monthly_sales.csv.")

    if count_col:
        st.markdown("#### Monthly Sales Data")
        st.dataframe(trend, use_container_width=True, hide_index=True)

# --------------------------------------------------
# BUYER INSIGHTS PAGE
# --------------------------------------------------
elif page == "Buyer Insights":

    st.markdown("### 👥 Buyer Insights")

    purpose_col = next(
        (c for c in ["acquisition_purpose", "purpose", "buyer_purpose"]
         if c in clients.columns),
        None
    )

    if purpose_col:
        purpose_df = (
            filtered_clients[purpose_col].fillna("Unknown")
            .value_counts()
            .rename_axis("Buyer Purpose")
            .reset_index(name="Buyer Count")
        )

        fig = px.bar(
            purpose_df,
            x="Buyer Purpose",
            y="Buyer Count",
            color="Buyer Purpose",
            title="Buyer Distribution by Purpose"
        )
        show_chart(style_chart(fig, 350), use_container_width=True)

    if "referral_channel" in filtered_clients.columns:
        referral_df = (
            filtered_clients["referral_channel"].fillna("Unknown")
            .value_counts()
            .rename_axis("Referral Channel")
            .reset_index(name="Buyer Count")
        )

        fig = px.bar(
            referral_df,
            x="Referral Channel",
            y="Buyer Count",
            title="Customer Acquisition Channels"
        )
        show_chart(style_chart(fig, 350), use_container_width=True)

    if "satisfaction_score" in filtered_clients.columns:
        satisfaction = filtered_clients["satisfaction_score"].value_counts().sort_index()
        satisfaction_df = satisfaction.rename_axis("Satisfaction Score").reset_index(
            name="Buyer Count"
        )

        fig = px.bar(
            satisfaction_df,
            x="Satisfaction Score",
            y="Buyer Count",
            title="Customer Satisfaction Distribution"
        )
        show_chart(style_chart(fig, 350), use_container_width=True)

# --------------------------------------------------
# BUYER SEGMENTATION PAGE
# --------------------------------------------------
elif page == "Buyer Segmentation":

    st.markdown("### 🧩 Buyer Segmentation")
    st.caption(
        "K-Means clustering groups buyers by observed purchase behaviour "
        "and available profile attributes. Clusters are analytical groups, "
        "not verified wealth categories."
    )

    st.markdown("#### Model Evaluation")
    eval_view = cluster_evaluation.copy()
    if {"model", "n_clusters", "silhouette_score"}.issubset(eval_view.columns):
        fig = px.line(
            eval_view, x="n_clusters", y="silhouette_score", color="model",
            markers=True, title="Silhouette Score: K-Means vs Hierarchical"
        )
        show_chart(style_chart(fig, 330), use_container_width=True)
    if "model" in eval_view.columns and "inertia" in eval_view.columns:
        kmeans_eval = eval_view[(eval_view["model"] == "KMeans") & eval_view["inertia"].notna()]
        if not kmeans_eval.empty:
            fig = px.line(
                kmeans_eval, x="n_clusters", y="inertia", markers=True,
                title="Elbow Method — K-Means Inertia"
            )
            show_chart(style_chart(fig, 330), use_container_width=True)

    if "cluster" in cluster_summary.columns:
        cluster_col = "cluster"
    elif "cluster_label" in cluster_summary.columns:
        cluster_col = "cluster_label"
    else:
        cluster_col = None

    if cluster_col:
        cluster_summary[cluster_col] = (
    "Cluster " + cluster_summary[cluster_col].astype(str)
)

        cluster_colors = px.colors.qualitative.Plotly

        left, right = st.columns(2)

        with left:
            fig = px.bar(
                cluster_summary,
                x=cluster_col,
                y="buyer_count",
                color=cluster_col,
                title="Buyers in Each Cluster",
                labels={
                    cluster_col: "Cluster",
                    "buyer_count": "Number of Buyers"
                }
            )
            show_chart(style_chart(fig, 350), use_container_width=True)

        with right:
            if "buyer_percentage" in cluster_summary.columns:
                fig = px.pie(
                    cluster_summary,
                    names=cluster_col,
                    values="buyer_percentage",
                    hole=0.60,
                    title="Buyer Segment Share"
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                show_chart(style_chart(fig, 350), use_container_width=True)

        st.markdown("#### Cluster Profile")
                # Prepare a presentation-friendly cluster profile
        display_summary = cluster_summary.copy()

        display_summary = display_summary.rename(columns={
            "cluster": "Buyer Segment",
            "buyer_count": "Number of Buyers",
            "avg_properties_purchased": "Avg. Properties Purchased",
            "avg_total_purchase_value": "Avg. Total Purchase Value ($)",
            "avg_property_price": "Avg. Property Price ($)",
            "avg_satisfaction_score": "Avg. Satisfaction Score",
            "buyer_percentage": "Buyer Share (%)"
        })

        currency_columns = [
            "Avg. Total Purchase Value ($)",
            "Avg. Property Price ($)"
        ]

        for column in currency_columns:
            if column in display_summary.columns:
                display_summary[column] = display_summary[column].map(
                    lambda value: f"${value:,.0f}"
                )

        if "Avg. Properties Purchased" in display_summary.columns:
            display_summary["Avg. Properties Purchased"] = (
                display_summary["Avg. Properties Purchased"].map(
                    lambda value: f"{value:.2f}"
                )
            )

        if "Avg. Satisfaction Score" in display_summary.columns:
            display_summary["Avg. Satisfaction Score"] = (
                display_summary["Avg. Satisfaction Score"].map(
                    lambda value: f"{value:.2f}"
                )
            )

        if "Buyer Share (%)" in display_summary.columns:
            display_summary["Buyer Share (%)"] = (
                display_summary["Buyer Share (%)"].map(
                    lambda value: f"{value:.1f}%"
                )
            )

        st.dataframe(
            display_summary,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### Key Observations")

        if "avg_total_purchase_value" in cluster_summary.columns:
            top_value_cluster = cluster_summary.loc[
                cluster_summary["avg_total_purchase_value"].idxmax()
            ]
            st.info(
                f"{top_value_cluster[cluster_col]} has the highest "
                f"average recorded purchase value: "
                f"${top_value_cluster['avg_total_purchase_value']:,.0f} per buyer."
            )

        if "avg_satisfaction_score" in cluster_summary.columns:
            top_satisfaction_cluster = cluster_summary.loc[
                cluster_summary["avg_satisfaction_score"].idxmax()
            ]
            st.info(
                f"{top_satisfaction_cluster[cluster_col]} has the "
                f"highest average satisfaction score: "
                f"{top_satisfaction_cluster['avg_satisfaction_score']:.2f}."
            )

    else:
        st.warning("Cluster column not found in buyer_cluster_summary.csv.")

    st.markdown("### 💡 Business Recommendations")

    # Dynamic recommendation cards (presentation only).
    # Built from the existing cluster_summary DataFrame; nothing is recalculated
    # or written back. Missing columns / empty data fall back to a neutral note.
    def _card(title_class, title, body):
        return (
            '<div class="insight-card">'
            f'<h4 class="insight-title {title_class}">{title}</h4>'
            f'<p>{body}</p>'
            '</div>'
        )

    def _num_series(column):
        if column not in cluster_summary.columns:
            return None
        series = pd.to_numeric(cluster_summary[column], errors="coerce").dropna()
        return series if not series.empty else None

    def _label(index):
        return escape(str(cluster_summary.loc[index, cluster_col]))

    def _share_text(index):
        if "buyer_percentage" in cluster_summary.columns:
            share = pd.to_numeric(
                cluster_summary.loc[index, "buyer_percentage"], errors="coerce"
            )
            if pd.notna(share):
                return f"{share:.1f}%"
        return None

    unavailable = (
        "Cluster summary data is not available, so this recommendation "
        "cannot be generated."
    )
    summary_ready = (
        isinstance(cluster_summary, pd.DataFrame)
        and not cluster_summary.empty
        and cluster_col is not None
    )

    # 01 - highest average purchase value
    card_1 = _card("gold", "01 · High Purchase-Value Segment", unavailable)
    value_series = _num_series("avg_total_purchase_value") if summary_ready else None
    if value_series is not None:
        idx = value_series.idxmax()
        note = ""
        share = _share_text(idx)
        if share:
            note = f" This segment represents {share} of observed buyers."
        card_1 = _card(
            "gold",
            "01 · High Purchase-Value Segment",
            f"{_label(idx)} has the highest average recorded purchase value "
            f"(${value_series.loc[idx]:,.0f} per buyer).{note} "
            "Consider personalized property recommendations and dedicated "
            "customer support for buyers with similar purchase patterns.",
        )

    # 02 - two largest segments (buyer_count, falling back to buyer_percentage)
    card_2 = _card("champagne", "02 · Largest Buyer Segments", unavailable)
    size_col, size_series = None, None
    if summary_ready:
        for candidate in ["buyer_count", "buyer_percentage"]:
            size_series = _num_series(candidate)
            if size_series is not None:
                size_col = candidate
                break
    if size_series is not None:
        top_idx = list(size_series.nlargest(2).index)

        def _segment_text(index):
            if size_col == "buyer_count":
                text = f"{_label(index)} ({int(size_series.loc[index]):,} buyers"
                share = _share_text(index)
                return text + (f", {share})" if share else ")")
            return f"{_label(index)} ({size_series.loc[index]:.1f}% of buyers)"

        if len(top_idx) == 2:
            lead = (
                f"{_segment_text(top_idx[0])} and {_segment_text(top_idx[1])} "
                "are the two largest buyer segments."
            )
        else:
            lead = f"{_segment_text(top_idx[0])} is the largest buyer segment."
        card_2 = _card(
            "champagne",
            "02 · Largest Buyer Segments",
            f"{lead} Compare their property preferences and satisfaction "
            "scores to improve targeted marketing and customer experience.",
        )

    # 03 - customer satisfaction, based on avg_satisfaction_score
    card_3 = _card("mint", "03 · Improve Customer Satisfaction", unavailable)
    sat_series = _num_series("avg_satisfaction_score") if summary_ready else None
    if sat_series is not None:
        low_idx, high_idx = sat_series.idxmin(), sat_series.idxmax()
        if len(sat_series) > 1 and low_idx != high_idx:
            sat_lead = (
                f"{_label(low_idx)} has the lowest average satisfaction score "
                f"({sat_series.loc[low_idx]:.2f}), compared with "
                f"{_label(high_idx)} at {sat_series.loc[high_idx]:.2f}."
            )
        else:
            sat_lead = (
                f"{_label(low_idx)} has an average satisfaction score of "
                f"{sat_series.loc[low_idx]:.2f}."
            )
        card_3 = _card(
            "mint",
            "03 · Improve Customer Satisfaction",
            f"{sat_lead} Review feedback and service touchpoints for "
            "segments with lower average satisfaction. Test improvements "
            "and monitor satisfaction over time.",
        )

    st.markdown("\n".join([card_1, card_2, card_3]), unsafe_allow_html=True)

# --------------------------------------------------
# INVESTOR BEHAVIOR DASHBOARD
# --------------------------------------------------
elif page == "Investor Behavior":
    st.markdown("### 📊 Investor Behavior Dashboard")
    if filtered_buyer_segments.empty:
        st.warning("No buyers match the selected filters. Adjust filters in the sidebar.")
    else:
        purpose_cluster = pd.crosstab(
            filtered_buyer_segments["cluster"],
            filtered_buyer_segments["acquisition_purpose"],
            normalize="index"
        ).mul(100).reset_index()
        purpose_long = purpose_cluster.melt(
            id_vars="cluster", var_name="Acquisition Purpose", value_name="Buyer Share (%)"
        )
        fig = px.bar(
            purpose_long, x="cluster", y="Buyer Share (%)",
            color="Acquisition Purpose", barmode="stack",
            title="Acquisition Purpose Mix by K-Means Cluster"
        )
        show_chart(style_chart(fig, 380), use_container_width=True)

        loan_cluster = pd.crosstab(
            filtered_buyer_segments["cluster"],
            filtered_buyer_segments["loan_applied"],
            normalize="index"
        ).mul(100).reset_index()
        loan_long = loan_cluster.melt(
            id_vars="cluster", var_name="Loan Applied", value_name="Buyer Share (%)"
        )
        fig = px.bar(
            loan_long, x="cluster", y="Buyer Share (%)",
            color="Loan Applied", barmode="stack",
            title="Financing Patterns by K-Means Cluster"
        )
        show_chart(style_chart(fig, 350), use_container_width=True)

        value_col = "total_purchase_value"
        if value_col in filtered_buyer_segments:
            fig = px.box(
                filtered_buyer_segments, x="cluster", y=value_col,
                title="Recorded Purchase Value Distribution by Cluster",
                labels={value_col: "Total Purchase Value ($)", "cluster": "K-Means Cluster"}
            )
            show_chart(style_chart(fig, 350), use_container_width=True)

# --------------------------------------------------
# GEOGRAPHIC BUYER ANALYSIS
# --------------------------------------------------
elif page == "Geographic Buyer Analysis":
    st.markdown("### 🌍 Geographic Buyer Analysis")
    if filtered_buyer_segments.empty:
        st.warning("No buyers match the selected filters. Adjust filters in the sidebar.")
    else:
        geo = (
            filtered_buyer_segments.groupby(["country", "region", "cluster"], dropna=False)
            .size().reset_index(name="buyer_count")
        )

        # Plotly's USA-states map uses state abbreviations. Only map rows explicitly
        # marked USA; retain all other countries in the regional charts below.
        state_codes = {
            "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
            "Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA",
            "Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS",
            "Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA",
            "Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT",
            "Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM",
            "New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK",
            "Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC",
            "South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT",
            "Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
        }
        usa = geo[geo["country"].astype(str).str.casefold().eq("usa")].copy()
        usa["state_code"] = usa["region"].map(state_codes)
        usa_map = usa.dropna(subset=["state_code"]).groupby("state_code", as_index=False)["buyer_count"].sum()
        if not usa_map.empty:
            map_fig = px.choropleth(
                usa_map, locations="state_code", locationmode="USA-states",
                color="buyer_count", scope="usa",
                title="US Buyer Distribution by State",
                labels={"buyer_count": "Buyer Count", "state_code": "State"}
            )
            show_chart(style_chart(map_fig, 430), use_container_width=True)

        top_regions = (
            geo.groupby(["region", "country"], dropna=False)["buyer_count"].sum()
            .reset_index().sort_values("buyer_count", ascending=False).head(20)
        )
        fig = px.bar(
            top_regions, x="buyer_count", y="region", color="country",
            orientation="h", title="Top Regions by Matched Buyer Count",
            labels={"buyer_count": "Buyer Count", "region": "Region", "country": "Country"}
        )
        show_chart(style_chart(fig, 500), use_container_width=True)

        region_cluster = (
            geo.groupby(["region", "cluster"])["buyer_count"].sum()
            .reset_index().sort_values("buyer_count", ascending=False)
        )
        fig = px.bar(
            region_cluster, x="region", y="buyer_count", color="cluster",
            barmode="stack", title="Buyer Segment Distribution by Region"
        )
        show_chart(style_chart(fig, 400), use_container_width=True)
        st.caption("The US choropleth maps state-level counts where region labels match US states; other countries remain represented in the regional comparison charts.")

# --------------------------------------------------
# SEGMENT INSIGHTS PANEL
# --------------------------------------------------
elif page == "Segment Insights Panel":
    st.markdown("### 🔎 Segment Insights Panel")
    if filtered_buyer_segments.empty:
        st.warning("No buyers match the selected filters. Adjust filters in the sidebar.")
    else:
        metrics = filtered_buyer_segments.groupby("cluster").agg(
            buyer_count=("client_id", "nunique"),
            avg_age=("age", "mean"),
            avg_properties_purchased=("properties_purchased", "mean"),
            avg_total_purchase_value=("total_purchase_value", "mean"),
            avg_property_price=("average_property_price", "mean"),
            avg_satisfaction_score=("satisfaction_score", "mean"),
        ).reset_index()
        metrics["buyer_share_pct"] = metrics["buyer_count"] / metrics["buyer_count"].sum() * 100
        st.dataframe(metrics.round(2), use_container_width=True, hide_index=True)

        long_metrics = metrics.melt(
            id_vars="cluster",
            value_vars=["avg_properties_purchased", "avg_total_purchase_value",
                        "avg_property_price", "avg_satisfaction_score"],
            var_name="Metric", value_name="Average"
        )
        fig = px.bar(
            long_metrics, x="cluster", y="Average", color="Metric", barmode="group",
            title="Descriptive Statistics by Buyer Segment"
        )
        show_chart(style_chart(fig, 400), use_container_width=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption(
    "Real Estate Buyer Segmentation & Investment Profiling · "
    "Data Analyst Internship Project"
)