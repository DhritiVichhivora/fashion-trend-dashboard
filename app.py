"""
Fashion Trend Forecasting & Sales Intelligence Dashboard
=========================================================
ONLINE VERSION: Reads directly from bundled SQLite database.
For Streamlit Cloud deployment (no FastAPI needed).
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import os
from datetime import datetime

st.set_page_config(
    page_title="Fashion Trend Forecasting & Sales Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# THEME — Vogue Editorial
# ═══════════════════════════════════════════════════════════════

VOGUE = {
    "bg":         "#FAF7F2",
    "card":       "#FFFFFF",
    "ink":        "#0A0A0A",
    "ink_soft":   "#3A3A3A",
    "ink_mute":   "#8C8C8C",
    "accent":     "#FF1F6D",
    "accent_dk":  "#C8024B",
    "border":     "#E5E1DA",
}

CHART_COLORS = ["#0A0A0A", "#FF1F6D", "#C8024B", "#8C8C8C",
                "#3A3A3A", "#FF7BA8", "#FFB8CE", "#5A5A5A",
                "#E5E1DA", "#FFD9E5"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Inter:wght@400;500;600;700&display=swap');

.block-container {{ padding: 1.2rem 2rem 3rem; max-width: 1320px; }}
html, body, [class*="css"], p, span, div, label {{ font-family: 'Inter', sans-serif !important; }}
.stApp {{ background: {VOGUE['bg']}; }}

h1 {{
    font-family: 'Playfair Display', serif !important;
    font-size: 2.6rem !important;
    font-weight: 900 !important;
    color: {VOGUE['ink']} !important;
    margin: 0 0 0.2rem 0 !important;
    letter-spacing: -1px;
    line-height: 1.05 !important;
}}

.stCaption, [data-testid="stCaptionContainer"] {{
    color: {VOGUE['ink_mute']} !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 500;
}}

h2, h3, h4 {{ color: {VOGUE['ink']} !important; }}
h3 {{
    font-family: 'Playfair Display', serif !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    margin: 1.5rem 0 0.4rem 0 !important;
    letter-spacing: -0.3px;
}}

[data-testid="stMetric"] {{
    background: {VOGUE['card']};
    border: 1px solid {VOGUE['border']};
    border-radius: 4px;
    padding: 18px 22px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: all 0.2s;
}}
[data-testid="stMetric"]:hover {{
    border-color: {VOGUE['accent']};
    box-shadow: 0 4px 14px rgba(255, 31, 109, 0.12);
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    color: {VOGUE['ink_mute']} !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}}
[data-testid="stMetricValue"] {{
    font-family: 'Playfair Display', serif !important;
    font-size: 2rem !important;
    font-weight: 900 !important;
    color: {VOGUE['ink']} !important;
    letter-spacing: -1px;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 0;
    background: transparent;
    border-bottom: 2px solid {VOGUE['ink']};
    border-radius: 0;
    padding: 0;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 0;
    padding: 12px 22px;
    font-weight: 700;
    font-size: 0.75rem;
    color: {VOGUE['ink_mute']} !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    background: transparent;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
}}
.stTabs [aria-selected="true"] {{
    background: transparent !important;
    color: {VOGUE['ink']} !important;
    border-bottom: 3px solid {VOGUE['accent']} !important;
}}

[data-testid="stSidebar"] {{
    background: {VOGUE['ink']};
}}
[data-testid="stSidebar"] h2 {{
    font-family: 'Playfair Display', serif !important;
    color: {VOGUE['bg']} !important;
    font-size: 1.4rem !important;
    font-weight: 900;
    letter-spacing: -0.5px;
}}
[data-testid="stSidebar"] .stCaption {{
    color: {VOGUE['ink_mute']} !important;
    letter-spacing: 2px;
}}
[data-testid="stSidebar"] label {{
    color: {VOGUE['bg']} !important;
    font-weight: 700 !important;
    font-size: 0.65rem !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {{
    background: #1A1A1A;
    border: 1px solid #3A3A3A;
    color: {VOGUE['bg']};
    border-radius: 2px;
}}

[data-testid="stPlotlyChart"] {{
    background: {VOGUE['card']};
    border: 1px solid {VOGUE['border']};
    border-radius: 4px;
    padding: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}

[data-testid="stDataFrame"] {{
    border-radius: 4px;
    border: 1px solid {VOGUE['border']};
    overflow: hidden;
}}

hr {{ border-color: {VOGUE['ink']} !important; margin: 1.5rem 0 !important; opacity: 0.15; }}

.stButton > button {{
    background: {VOGUE['ink']};
    color: {VOGUE['bg']};
    border: 1px solid {VOGUE['ink']};
    border-radius: 2px;
    font-weight: 700;
    padding: 10px 22px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-size: 0.7rem;
}}
.stButton > button:hover {{
    background: {VOGUE['accent']};
    border-color: {VOGUE['accent']};
    color: white;
}}

.story-card {{
    background: {VOGUE['card']};
    border: 1px solid {VOGUE['border']};
    border-left: 4px solid {VOGUE['accent']};
    border-radius: 2px;
    padding: 18px 22px;
    margin: 8px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}
.story-card .label {{
    color: {VOGUE['accent']};
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0 0 8px 0;
}}
.story-card .body {{
    color: {VOGUE['ink']};
    font-size: 0.95rem;
    line-height: 1.6;
    margin: 0;
}}
.story-card .body strong {{
    color: {VOGUE['accent']};
    font-weight: 700;
}}

.insight-box {{
    background: rgba(255, 31, 109, 0.06);
    border-left: 3px solid {VOGUE['accent']};
    padding: 12px 16px;
    font-size: 0.85rem;
    color: {VOGUE['ink']};
    margin: 10px 0;
}}
.insight-box strong {{ color: {VOGUE['accent']}; font-weight: 700; }}

.chart-subtitle {{
    color: {VOGUE['ink_mute']};
    font-size: 0.78rem;
    margin: -4px 0 12px 0;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-style: italic;
}}

.api-status {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {VOGUE['ink']};
    color: white;
    padding: 4px 12px;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}}
.api-status::before {{
    content: '';
    width: 6px; height: 6px;
    background: {VOGUE['accent']};
    border-radius: 50%;
    box-shadow: 0 0 8px {VOGUE['accent']};
}}

.header-strip {{
    border-top: 4px solid {VOGUE['ink']};
    border-bottom: 1px solid {VOGUE['ink']};
    padding: 1.4rem 0 1rem 0;
    margin-bottom: 1.5rem;
}}
.header-meta {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: {VOGUE['ink_mute']};
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 600;
}}
.header-meta .right {{ color: {VOGUE['accent']}; }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

USD_TO_INR = 83  # Exchange rate for converting USD to Indian Rupees

# Columns that contain money values (will be converted USD -> INR on load)
MONEY_COLS = {"revenue", "total_revenue", "avg_line_value", "lifetime_value",
              "total_value", "cumulative_revenue", "monthly_revenue"}

def to_inr(df):
    """Convert all money columns in a dataframe from USD to INR. Returns a copy."""
    if df is None or df.empty:
        return df
    df = df.copy()
    for col in df.columns:
        if col in MONEY_COLS:
            df[col] = df[col] * USD_TO_INR
    return df

def fmt_money(inr):
    """Format INR value in Indian style (Cr/L/K). Input is already INR."""
    if inr >= 1_00_00_000:  # 1 Crore
        return f"₹{inr/1_00_00_000:.2f}Cr"
    elif inr >= 1_00_000:   # 1 Lakh
        return f"₹{inr/1_00_000:.1f}L"
    elif inr >= 1_000:
        return f"₹{inr/1_000:.1f}K"
    return f"₹{inr:,.0f}"

def insight(text):
    st.markdown(f'<div class="insight-box">◆ {text}</div>', unsafe_allow_html=True)

def story_card(label, body):
    st.markdown(
        f'<div class="story-card"><p class="label">{label}</p><p class="body">{body}</p></div>',
        unsafe_allow_html=True,
    )

def chart_subtitle(text):
    st.markdown(f'<div class="chart-subtitle">{text}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════

DB_PATH = os.path.join(os.path.dirname(__file__), "fashion_trend.db")

def query(sql, params=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ◆ FASHION INTEL")
    st.caption("Trend Forecasting & Sales")
    st.markdown('<span class="api-status">DB Connected</span>', unsafe_allow_html=True)
    st.markdown("---")

    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("##### Filters")

    top_n = st.slider("Top N Items", 5, 20, 10)

    @st.cache_data(ttl=600)
    def get_countries():
        df = query("SELECT DISTINCT country FROM stores ORDER BY country")
        return df["country"].tolist() if not df.empty else []

    countries = get_countries()
    selected_countries = st.multiselect("Countries", countries, default=countries)

    selected_categories = st.multiselect(
        "Category",
        ["Feminine", "Masculine", "Children"],
        default=["Feminine", "Masculine", "Children"],
    )

    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center; color:{VOGUE['ink_mute']}; font-size:0.65rem; "
        f"text-transform:uppercase; letter-spacing:2px;'>"
        "DBMS Project &middot; 2026</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════
# DATA LOADERS (cached SQL queries)
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def load_monthly_sales():
    return query("""
        SELECT strftime('%Y-%m', transaction_date) AS month,
               COUNT(DISTINCT invoice_id) AS total_invoices,
               SUM(quantity) AS units_sold,
               ROUND(SUM(line_total), 2) AS revenue
        FROM transactions WHERE transaction_type = 'Sale'
        GROUP BY month ORDER BY month
    """)

@st.cache_data(ttl=300)
def load_top_products(limit):
    return query("""
        SELECT p.product_id, p.product_name, p.category, p.sub_category,
               SUM(t.quantity) AS units_sold,
               ROUND(SUM(t.line_total), 2) AS total_revenue
        FROM transactions t
        JOIN products p ON t.product_id = p.product_id
        WHERE t.transaction_type = 'Sale'
        GROUP BY p.product_id, p.product_name, p.category, p.sub_category
        ORDER BY total_revenue DESC LIMIT ?
    """, [limit])

@st.cache_data(ttl=300)
def load_country_sales():
    return query("""
        SELECT s.country,
               COUNT(DISTINCT t.invoice_id) AS total_invoices,
               SUM(t.quantity) AS units_sold,
               ROUND(SUM(t.line_total), 2) AS revenue
        FROM transactions t
        JOIN stores s ON t.store_id = s.store_id
        WHERE t.transaction_type = 'Sale'
        GROUP BY s.country ORDER BY revenue DESC
    """)

@st.cache_data(ttl=300)
def load_category_sales():
    return query("""
        SELECT p.category,
               COUNT(t.transaction_id) AS transactions,
               SUM(t.quantity) AS units_sold,
               ROUND(SUM(t.line_total), 2) AS revenue
        FROM transactions t
        JOIN products p ON t.product_id = p.product_id
        WHERE t.transaction_type = 'Sale'
        GROUP BY p.category ORDER BY revenue DESC
    """)

@st.cache_data(ttl=300)
def load_top_stores(limit):
    return query("""
        SELECT s.store_id, s.store_name, s.city, s.country,
               COUNT(DISTINCT t.invoice_id) AS total_invoices,
               ROUND(SUM(t.line_total), 2) AS revenue
        FROM stores s
        JOIN transactions t ON s.store_id = t.store_id
        WHERE t.transaction_type = 'Sale'
        GROUP BY s.store_id, s.store_name, s.city, s.country
        ORDER BY revenue DESC LIMIT ?
    """, [limit])

@st.cache_data(ttl=300)
def load_discount_effectiveness():
    return query("""
        SELECT 
            CASE WHEN discount = 0 THEN 'No Discount'
                 WHEN discount BETWEEN 0.01 AND 0.20 THEN 'Low (1-20%)'
                 WHEN discount BETWEEN 0.21 AND 0.40 THEN 'Medium (21-40%)'
                 ELSE 'High (>40%)'
            END AS discount_bucket,
            COUNT(*) AS transactions,
            ROUND(SUM(line_total), 2) AS revenue
        FROM transactions WHERE transaction_type = 'Sale'
        GROUP BY discount_bucket ORDER BY revenue DESC
    """)

@st.cache_data(ttl=300)
def load_top_customers(limit):
    return query("""
        SELECT c.customer_id, c.name, c.country, c.gender, c.age,
               COUNT(DISTINCT t.invoice_id) AS total_orders,
               ROUND(SUM(t.line_total), 2) AS lifetime_value
        FROM customers c
        JOIN transactions t ON c.customer_id = t.customer_id
        WHERE t.transaction_type = 'Sale'
        GROUP BY c.customer_id, c.name, c.country, c.gender, c.age
        ORDER BY lifetime_value DESC LIMIT ?
    """, [limit])

@st.cache_data(ttl=300)
def load_payment_breakdown():
    return query("""
        SELECT payment_method, COUNT(*) AS transactions,
               ROUND(SUM(line_total), 2) AS revenue,
               ROUND(SUM(line_total) * 100.0 / 
                     (SELECT SUM(line_total) FROM transactions WHERE transaction_type = 'Sale'), 2) AS pct_of_total
        FROM transactions WHERE transaction_type = 'Sale'
        GROUP BY payment_method ORDER BY revenue DESC
    """)

@st.cache_data(ttl=300)
def load_sales_vs_returns():
    return query("""
        SELECT transaction_type, COUNT(*) AS count_transactions,
               ROUND(SUM(line_total), 2) AS total_value
        FROM transactions GROUP BY transaction_type
    """)

@st.cache_data(ttl=300)
def load_sub_category():
    return query("""
        SELECT p.category, p.sub_category,
               ROUND(SUM(t.line_total), 2) AS revenue
        FROM transactions t
        JOIN products p ON t.product_id = p.product_id
        WHERE t.transaction_type = 'Sale'
        GROUP BY p.category, p.sub_category
        ORDER BY p.category, revenue DESC
    """)

@st.cache_data(ttl=300)
def load_demographics():
    return query("""
        SELECT c.gender,
               CASE WHEN c.age < 25 THEN '18-24'
                    WHEN c.age BETWEEN 25 AND 34 THEN '25-34'
                    WHEN c.age BETWEEN 35 AND 44 THEN '35-44'
                    WHEN c.age BETWEEN 45 AND 54 THEN '45-54'
                    ELSE '55+' END AS age_group,
               ROUND(SUM(t.line_total), 2) AS revenue
        FROM customers c
        JOIN transactions t ON c.customer_id = t.customer_id
        WHERE t.transaction_type = 'Sale'
        GROUP BY c.gender, age_group ORDER BY c.gender, age_group
    """)

@st.cache_data(ttl=300)
def load_stores():
    return query("SELECT * FROM stores")

@st.cache_data(ttl=300)
def load_yoy():
    return query("""
        SELECT CAST(strftime('%Y', transaction_date) AS INTEGER) AS year,
               CAST(strftime('%m', transaction_date) AS INTEGER) AS month,
               ROUND(SUM(line_total), 2) AS revenue
        FROM transactions WHERE transaction_type = 'Sale'
        GROUP BY year, month ORDER BY year, month
    """)

@st.cache_data(ttl=300)
def load_dow_heatmap():
    df = query("""
        SELECT strftime('%w', transaction_date) AS day_num,
               CAST(strftime('%H', transaction_date) AS INTEGER) AS hour,
               COUNT(*) AS transaction_count
        FROM transactions WHERE transaction_type = 'Sale'
        GROUP BY day_num, hour ORDER BY day_num, hour
    """)
    if not df.empty:
        day_map = {'0':'Sunday','1':'Monday','2':'Tuesday','3':'Wednesday',
                   '4':'Thursday','5':'Friday','6':'Saturday'}
        df["day_name"] = df["day_num"].map(day_map)
    return df

@st.cache_data(ttl=300)
def load_cumulative():
    df = load_monthly_sales()
    if not df.empty:
        df = df.copy()
        df["cumulative_revenue"] = df["revenue"].cumsum()
    return df


CHART_TEMPLATE = "plotly_white"
CHART_FONT = dict(family="Inter", color=VOGUE['ink'], size=11)
CHART_BG = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")


def style_fig(fig, height=380):
    fig.update_layout(
        template=CHART_TEMPLATE, **CHART_BG,
        height=height, font=CHART_FONT,
        margin=dict(l=15, r=15, t=15, b=15),
        xaxis=dict(gridcolor=VOGUE['border'], linecolor=VOGUE['ink'], linewidth=1, zeroline=False),
        yaxis=dict(gridcolor=VOGUE['border'], linecolor=VOGUE['ink'], linewidth=1, zeroline=False),
    )
    return fig


# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════

st.markdown(
    f'''
    <div class="header-strip">
        <div class="header-meta">
            <span>VOL. 1 &nbsp;&middot;&nbsp; ISSUE 01 &nbsp;&middot;&nbsp; {datetime.now().strftime("%B %Y").upper()}</span>
            <span class="right">◆ FASHION INTELLIGENCE</span>
        </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

st.markdown("# Fashion Trend Forecasting & Sales Intelligence")
st.caption("Real-time analytics dashboard")
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# DATA + KPI + STORY CARDS
# ═══════════════════════════════════════════════════════════════

df_monthly = to_inr(load_monthly_sales())
df_country = to_inr(load_country_sales())
df_category = to_inr(load_category_sales())
df_returns = to_inr(load_sales_vs_returns())

if selected_countries and not df_country.empty:
    df_country_filtered = df_country[df_country["country"].isin(selected_countries)]
else:
    df_country_filtered = df_country

if not df_monthly.empty:
    total_revenue = df_country_filtered["revenue"].sum() if not df_country_filtered.empty else 0
    total_invoices = int(df_country_filtered["total_invoices"].sum()) if not df_country_filtered.empty else 0
    total_units = int(df_country_filtered["units_sold"].sum()) if not df_country_filtered.empty else 0
    avg_invoice = total_revenue / total_invoices if total_invoices > 0 else 0

    return_rate = 0
    if not df_returns.empty:
        sales_cnt = df_returns[df_returns["transaction_type"] == "Sale"]["count_transactions"].sum()
        ret_cnt = df_returns[df_returns["transaction_type"] == "Return"]["count_transactions"].sum()
        if sales_cnt > 0:
            return_rate = (ret_cnt / sales_cnt) * 100

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Revenue", fmt_money(total_revenue))
    k2.metric("Invoices", f"{total_invoices:,}")
    k3.metric("Units Sold", f"{total_units:,}")
    k4.metric("Avg Invoice", fmt_money(avg_invoice))
    k5.metric("Return Rate", f"{return_rate:.1f}%")

if not df_monthly.empty and not df_country.empty and not df_category.empty:
    best_month = df_monthly.loc[df_monthly["revenue"].idxmax()]
    top_country = df_country.iloc[0]
    top_cat = df_category.iloc[0]
    cat_share = (top_cat['revenue'] / df_category['revenue'].sum()) * 100

    st.markdown("###  ")
    c1, c2, c3 = st.columns(3)
    with c1:
        story_card("Top Market",
                   f"<strong>{top_country['country']}</strong> leads with "
                   f"<strong>{fmt_money(top_country['revenue'])}</strong> in revenue from "
                   f"{int(top_country['total_invoices']):,} invoices.")
    with c2:
        story_card("Peak Month",
                   f"<strong>{best_month['month']}</strong> was the highest-grossing month with "
                   f"<strong>{fmt_money(best_month['revenue'])}</strong> in sales.")
    with c3:
        story_card("Bestselling Division",
                   f"<strong>{top_cat['category']}</strong> wear leads with "
                   f"<strong>{fmt_money(top_cat['revenue'])}</strong> "
                   f"({cat_share:.0f}% share).")

st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Trends", "Geography", "Categories", "Payments", "Customers", "Store Map", "Patterns",
])


# ── Tab 1: Trends ──
with tab1:
    if not df_monthly.empty:
        st.markdown("### Monthly Revenue Trend")
        chart_subtitle("Revenue performance month by month")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_monthly["month"], y=df_monthly["revenue"],
            mode="lines+markers",
            line=dict(color=VOGUE['ink'], width=3),
            marker=dict(size=8, color=VOGUE['accent'], line=dict(color=VOGUE['ink'], width=2)),
            fill="tozeroy", fillcolor="rgba(255, 31, 109, 0.06)",
        ))
        fig.update_layout(xaxis_title="", yaxis_title="Revenue (INR)", hovermode="x unified")
        st.plotly_chart(style_fig(fig, 380), use_container_width=True)

        best = df_monthly.loc[df_monthly["revenue"].idxmax()]
        worst = df_monthly.loc[df_monthly["revenue"].idxmin()]
        insight(f"Best month: <strong>{best['month']}</strong> ({fmt_money(best['revenue'])}) &nbsp;|&nbsp; "
                f"Slowest: <strong>{worst['month']}</strong> ({fmt_money(worst['revenue'])})")

        df_cum = to_inr(load_cumulative())
        if not df_cum.empty:
            st.markdown("### Cumulative Revenue Growth")
            chart_subtitle("Total accumulated revenue over the data period")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_cum["month"], y=df_cum["cumulative_revenue"],
                mode="lines",
                line=dict(color=VOGUE['accent'], width=3),
                fill="tozeroy", fillcolor="rgba(255, 31, 109, 0.08)",
            ))
            fig.update_layout(xaxis_title="", yaxis_title="Cumulative Revenue (INR)")
            st.plotly_chart(style_fig(fig, 320), use_container_width=True)

        df_top = to_inr(load_top_products(top_n))
        if not df_top.empty:
            if selected_categories:
                df_top = df_top[df_top["category"].isin(selected_categories)]
            if not df_top.empty:
                st.markdown(f"### Top {top_n} Products by Revenue")
                chart_subtitle("Highest-grossing products. Adjust 'Top N' in sidebar.")
                fig = px.bar(
                    df_top.sort_values("total_revenue"),
                    x="total_revenue", y="product_name", orientation="h",
                    color="category",
                    color_discrete_sequence=[VOGUE['ink'], VOGUE['accent'], "#FFB8CE"],
                    labels={"total_revenue": "Revenue (INR)", "product_name": ""},
                )
                fig.update_layout(legend=dict(orientation="h", y=1.05))
                st.plotly_chart(style_fig(fig, 460), use_container_width=True)


# ── Tab 2: Geography ──
with tab2:
    if not df_country_filtered.empty:
        st.markdown("### Global Revenue by Country")
        chart_subtitle("Choropleth map — darker = more revenue")
        country_iso = {
            "United States": "USA", "China": "CHN", "Germany": "DEU",
            "United Kingdom": "GBR", "France": "FRA", "Spain": "ESP", "Portugal": "PRT",
        }
        df_map = df_country_filtered.copy()
        df_map["iso"] = df_map["country"].map(country_iso)

        fig = px.choropleth(
            df_map, locations="iso", color="revenue",
            hover_name="country",
            hover_data={"iso": False, "revenue": ":,.0f"},
            color_continuous_scale=["#FFFFFF", VOGUE['accent'], VOGUE['ink']],
        )
        fig.update_layout(
            height=420, font=CHART_FONT, **CHART_BG,
            geo=dict(
                bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=True,
                coastlinecolor=VOGUE['border'], landcolor="#FFFFFF",
                showcountries=True, countrycolor=VOGUE['border'],
                projection_type="natural earth",
            ),
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Revenue Ranking")
            chart_subtitle("Countries ranked by total revenue")
            fig = px.bar(
                df_country_filtered.sort_values("revenue"),
                x="revenue", y="country", orientation="h",
                color="revenue", color_continuous_scale=["#FFE5EE", VOGUE['accent']],
                labels={"country": "", "revenue": "Revenue (INR)"},
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(style_fig(fig, 380), use_container_width=True)

        df_stores_perf = to_inr(load_top_stores(top_n))
        if not df_stores_perf.empty:
            with col2:
                st.markdown(f"### Top {top_n} Stores")
                chart_subtitle("Best-performing physical stores worldwide")
                fig = px.bar(
                    df_stores_perf.sort_values("revenue"),
                    x="revenue", y="store_name", orientation="h",
                    color="country", color_discrete_sequence=CHART_COLORS,
                    labels={"revenue": "Revenue (INR)", "store_name": ""},
                )
                fig.update_layout(legend=dict(font=dict(size=9)))
                st.plotly_chart(style_fig(fig, 380), use_container_width=True)


# ── Tab 3: Categories ──
with tab3:
    if not df_category.empty:
        st.markdown("### Category Performance")
        chart_subtitle("Revenue split between Feminine, Masculine, and Children")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                df_category, x="category", y="revenue", color="category",
                labels={"category": "", "revenue": "Revenue (INR)"},
                color_discrete_sequence=[VOGUE['accent'], VOGUE['ink'], "#FFB8CE"],
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(style_fig(fig, 380), use_container_width=True)
        with col2:
            fig = px.pie(
                df_category, values="revenue", names="category", hole=0.5,
                color_discrete_sequence=[VOGUE['accent'], VOGUE['ink'], "#FFB8CE"],
            )
            fig.update_layout(font=CHART_FONT, **CHART_BG, height=380, margin=dict(l=15, r=15, t=15, b=15))
            st.plotly_chart(fig, use_container_width=True)

        df_sub = to_inr(load_sub_category())
        if not df_sub.empty:
            if selected_categories:
                df_sub = df_sub[df_sub["category"].isin(selected_categories)]
            if not df_sub.empty:
                st.markdown("### Sub-Category Treemap")
                chart_subtitle("Each rectangle's size shows its revenue contribution")
                fig = px.treemap(
                    df_sub, path=["category", "sub_category"], values="revenue",
                    color="revenue",
                    color_continuous_scale=["#FFFFFF", VOGUE['accent'], VOGUE['ink']],
                )
                fig.update_layout(height=460, font=CHART_FONT, **CHART_BG, margin=dict(l=15, r=15, t=15, b=15))
                st.plotly_chart(fig, use_container_width=True)


# ── Tab 4: Payments ──
with tab4:
    df_pay = to_inr(load_payment_breakdown())
    df_disc = to_inr(load_discount_effectiveness())

    col1, col2 = st.columns(2)
    if not df_pay.empty:
        with col1:
            st.markdown("### Payment Methods")
            chart_subtitle("How customers choose to pay")
            fig = px.pie(
                df_pay, values="revenue", names="payment_method", hole=0.5,
                color_discrete_sequence=[VOGUE['ink'], VOGUE['accent']],
            )
            fig.update_layout(height=380, font=CHART_FONT, **CHART_BG, margin=dict(l=15, r=15, t=15, b=15))
            st.plotly_chart(fig, use_container_width=True)
            top_pay = df_pay.iloc[0]
            insight(f"<strong>{top_pay['payment_method']}</strong> dominates with "
                    f"<strong>{top_pay['pct_of_total']}%</strong> of total revenue")

    if not df_disc.empty:
        with col2:
            st.markdown("### Discount Effectiveness")
            chart_subtitle("Revenue distribution across discount levels")
            fig = px.bar(
                df_disc, x="discount_bucket", y="revenue", color="discount_bucket",
                labels={"discount_bucket": "", "revenue": "Revenue (INR)"},
                color_discrete_sequence=CHART_COLORS,
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(style_fig(fig, 380), use_container_width=True)

    if not df_returns.empty:
        st.markdown("### Sales vs Returns")
        chart_subtitle("Compare total sales value with returns")
        fig = px.bar(
            df_returns, x="transaction_type", y="total_value", color="transaction_type",
            labels={"transaction_type": "", "total_value": "Value (INR)"},
            color_discrete_sequence=[VOGUE['ink'], VOGUE['accent']],
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig, 320), use_container_width=True)


# ── Tab 5: Customers ──
with tab5:
    df_top_cust = to_inr(load_top_customers(top_n))
    if not df_top_cust.empty:
        st.markdown(f"### Top {top_n} Customers by Lifetime Value")
        chart_subtitle("Highest-spending customers with their purchase history")
        st.dataframe(
            df_top_cust.rename(columns={
                "customer_id": "ID", "name": "Name", "country": "Country",
                "gender": "Gender", "age": "Age", "total_orders": "Orders",
                "lifetime_value": "Lifetime Value (INR)",
            }),
            use_container_width=True, hide_index=True,
        )

    df_demo = to_inr(load_demographics())
    if not df_demo.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Revenue by Gender")
            chart_subtitle("Revenue split across customer gender")
            df_g = df_demo.groupby("gender")["revenue"].sum().reset_index()
            fig = px.bar(
                df_g, x="gender", y="revenue", color="gender",
                labels={"gender": "", "revenue": "Revenue (INR)"},
                color_discrete_sequence=[VOGUE['accent'], VOGUE['ink'], "#FFB8CE"],
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(style_fig(fig, 350), use_container_width=True)
        with col2:
            st.markdown("### Revenue by Age Group")
            chart_subtitle("Which age groups drive the most sales")
            df_a = df_demo.groupby("age_group")["revenue"].sum().reset_index()
            fig = px.bar(
                df_a, x="age_group", y="revenue",
                color="revenue", color_continuous_scale=["#FFE5EE", VOGUE['accent']],
                labels={"age_group": "", "revenue": "Revenue (INR)"},
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(style_fig(fig, 350), use_container_width=True)


# ── Tab 6: Store Map ──
with tab6:
    df_stores = load_stores()
    if not df_stores.empty:
        st.markdown("### Global Store Network")
        chart_subtitle(f"All {len(df_stores)} stores worldwide. Bubble size = number of employees.")
        fig = px.scatter_geo(
            df_stores, lat="latitude", lon="longitude",
            hover_name="store_name",
            hover_data={"city": True, "country": True, "num_employees": True,
                        "latitude": False, "longitude": False},
            color="country", size="num_employees",
            projection="natural earth",
            color_discrete_sequence=CHART_COLORS,
        )
        fig.update_layout(
            height=550, font=CHART_FONT, **CHART_BG,
            geo=dict(
                bgcolor="rgba(0,0,0,0)", landcolor="#FFFFFF",
                showcountries=True, countrycolor=VOGUE['border'],
                coastlinecolor=VOGUE['border'],
            ),
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(font=dict(size=10)),
        )
        st.plotly_chart(fig, use_container_width=True)


# ── Tab 7: Patterns ──
with tab7:
    df_yoy = to_inr(load_yoy())
    if not df_yoy.empty:
        st.markdown("### Year-over-Year Comparison")
        chart_subtitle("Compare monthly revenue across years to spot trends and seasonality")
        month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                       7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        df_yoy["month_name"] = df_yoy["month"].map(month_names)

        fig = go.Figure()
        year_colors = {2023: VOGUE['ink'], 2024: VOGUE['accent'], 2025: "#FFB8CE"}
        for year in sorted(df_yoy["year"].unique()):
            year_data = df_yoy[df_yoy["year"] == year]
            fig.add_trace(go.Scatter(
                x=year_data["month_name"], y=year_data["revenue"],
                mode="lines+markers", name=str(year),
                line=dict(width=3, color=year_colors.get(year, VOGUE['accent_dk'])),
                marker=dict(size=8),
            ))
        fig.update_layout(xaxis_title="", yaxis_title="Revenue (INR)", hovermode="x unified")
        st.plotly_chart(style_fig(fig, 400), use_container_width=True)

    df_dow = load_dow_heatmap()
    if not df_dow.empty:
        st.markdown("### Shopping Patterns Heatmap")
        chart_subtitle("Brighter cells = more transactions at that day/hour combination")
        day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        pivot = df_dow.pivot_table(index="day_name", columns="hour", values="transaction_count", fill_value=0)
        pivot = pivot.reindex([d for d in day_order if d in pivot.index])

        fig = px.imshow(
            pivot, color_continuous_scale=["#FFFFFF", VOGUE['accent'], VOGUE['ink']], aspect="auto",
            labels=dict(x="Hour of Day", y="", color="Transactions"),
        )
        fig.update_layout(height=380, font=CHART_FONT, **CHART_BG, margin=dict(l=15, r=15, t=15, b=15))
        st.plotly_chart(fig, use_container_width=True)

        max_idx = df_dow["transaction_count"].idxmax()
        peak = df_dow.loc[max_idx]
        insight(f"Peak shopping time: <strong>{peak['day_name']} at {int(peak['hour'])}:00</strong> "
                f"with {int(peak['transaction_count'])} transactions")


# ── Footer ──
st.markdown("---")
st.markdown(
    f"<div style='text-align:center; color:{VOGUE['ink_mute']}; font-size:0.7rem; "
    f"text-transform:uppercase; letter-spacing:2px; padding-top:0.5rem;'>"
    "◆ Fashion Trend Forecasting & Sales Intelligence &middot; DBMS Project 2026"
    "</div>",
    unsafe_allow_html=True,
)
