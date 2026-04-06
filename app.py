"""
Fashion Trend Forecasting & Sales Intelligence Dashboard
=========================================================
Standalone version — reads directly from SQLite database.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import os
from datetime import datetime, date

# ── Page config ──
st.set_page_config(
    page_title="Fashion Trend Intelligence",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium CSS ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    /* Global */
    .block-container { padding: 1.5rem 2rem; max-width: 1200px; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    /* Header styling */
    h1 { 
        font-size: 1.8rem !important; 
        font-weight: 700 !important; 
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0 !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8f9fc 0%, #eef1f8 100%);
        border: 1px solid #e2e6f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 4px; 
        background: #f1f5f9;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label {
        color: #64748b !important;
        font-weight: 500;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Dividers */
    hr { border-color: #e2e6f0 !important; margin: 1rem 0 !important; }

    /* Plotly chart containers */
    [data-testid="stPlotlyChart"] {
        border: 1px solid #e2e6f0;
        border-radius: 12px;
        padding: 8px;
        background: white;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# DATABASE CONNECTION
# ═══════════════════════════════════════════════════════════════

DB_PATH = os.path.join(os.path.dirname(__file__), "fashion_trend.db")

def get_data(query, params=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 👗 Fashion Intelligence")
    st.caption("Trend Forecasting & Sales Analytics")
    st.divider()

    if st.button("🔄  Refresh Data", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.markdown("##### Filters")

    # Date range filter
    date_range = st.date_input(
        "📅 Date Range",
        value=(date(2023, 1, 1), date(2025, 12, 31)),
        min_value=date(2023, 1, 1),
        max_value=date(2025, 12, 31),
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = date(2023, 1, 1), date(2025, 12, 31)

    # Attribute type filter
    attr_type = st.selectbox(
        "🏷️ Attribute Type",
        ["Color", "Style", "Material", "Season", "Fit"],
    )

    # Top N slider
    top_n = st.slider("🏆 Top N Products", 5, 20, 10)

    # Channel filter
    channel_filter = st.multiselect(
        "📱 Sales Channel",
        ["Online", "Store", "App"],
        default=["Online", "Store", "App"],
    )

    # Category filter
    categories = get_data("SELECT category_name FROM categories ORDER BY category_name")
    if not categories.empty:
        cat_list = categories["category_name"].tolist()
        selected_cats = st.multiselect(
            "📂 Categories",
            cat_list,
            default=cat_list,
        )
    else:
        selected_cats = []

    st.divider()
    st.markdown(
        "<div style='text-align:center; opacity:0.5; font-size:0.7rem;'>"
        "DBMS Course Project 2026</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def load_monthly_sales(channels, start, end):
    channels = list(channels)
    if not channels:
        return pd.DataFrame()
    placeholders = ",".join(["?" for _ in channels])
    params = channels + [str(start), str(end)]
    return get_data(f"""
        SELECT strftime('%Y-%m', sale_date) AS month,
               COUNT(*) AS total_orders,
               SUM(quantity) AS units_sold,
               ROUND(SUM(total_amount), 2) AS revenue
        FROM sales
        WHERE channel IN ({placeholders})
          AND sale_date >= ? AND sale_date <= ?
        GROUP BY month ORDER BY month
    """, params)

@st.cache_data(ttl=300)
def load_top_products(n, start, end, cats):
    if not cats:
        return pd.DataFrame()
    cat_ph = ",".join(["?" for _ in cats])
    params = [str(start), str(end)] + list(cats) + [n]
    return get_data(f"""
        SELECT p.product_id, p.product_name, c.category_name,
               ROUND(SUM(s.total_amount), 2) AS total_revenue,
               SUM(s.quantity) AS total_units
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        WHERE s.sale_date >= ? AND s.sale_date <= ?
          AND c.category_name IN ({cat_ph})
        GROUP BY p.product_id, p.product_name, c.category_name
        ORDER BY total_revenue DESC LIMIT ?
    """, params)

@st.cache_data(ttl=300)
def load_trend_correlation():
    return get_data("""
        SELECT t.keyword,
               ROUND(AVG(t.trend_score), 2) AS avg_trend_score,
               COUNT(DISTINCT s.sale_id) AS linked_sales,
               ROUND(SUM(s.total_amount), 2) AS linked_revenue
        FROM trends t
        JOIN product_trend_map ptm ON t.trend_id = ptm.trend_id
        JOIN sales s ON ptm.product_id = s.product_id
        GROUP BY t.keyword ORDER BY avg_trend_score DESC LIMIT 15
    """)

@st.cache_data(ttl=300)
def load_region_demand(start, end):
    return get_data("""
        SELECT cu.region,
               COUNT(s.sale_id) AS total_orders,
               SUM(s.quantity) AS units_sold,
               ROUND(SUM(s.total_amount), 2) AS revenue
        FROM sales s
        JOIN customers cu ON s.customer_id = cu.customer_id
        WHERE s.sale_date >= ? AND s.sale_date <= ?
        GROUP BY cu.region ORDER BY revenue DESC
    """, [str(start), str(end)])

@st.cache_data(ttl=300)
def load_inventory_risk():
    return get_data("""
        SELECT p.product_id, p.product_name, p.brand,
               i.stock_quantity, i.reorder_level,
               i.warehouse_location,
               (i.reorder_level - i.stock_quantity) AS deficit
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        WHERE i.stock_quantity < i.reorder_level
        ORDER BY deficit DESC
    """)

@st.cache_data(ttl=300)
def load_dead_stock():
    return get_data("""
        SELECT p.product_id, p.product_name, p.brand,
               i.stock_quantity, i.warehouse_location
        FROM products p
        JOIN inventory i ON p.product_id = i.product_id
        LEFT JOIN sales s ON p.product_id = s.product_id
            AND s.sale_date >= date('now', '-90 days')
        WHERE i.stock_quantity > 0
        GROUP BY p.product_id, p.product_name, p.brand,
                 i.stock_quantity, i.warehouse_location
        HAVING COUNT(s.sale_id) = 0
        ORDER BY i.stock_quantity DESC
    """)

@st.cache_data(ttl=300)
def load_attribute_trends(atype, start, end):
    return get_data("""
        SELECT a.attribute_type, a.attribute_value,
               SUM(s.quantity) AS units_sold,
               ROUND(SUM(s.total_amount), 2) AS revenue
        FROM sales s
        JOIN product_attributes pa ON s.product_id = pa.product_id
        JOIN attributes a ON pa.attribute_id = a.attribute_id
        WHERE a.attribute_type = ?
          AND s.sale_date >= ? AND s.sale_date <= ?
        GROUP BY a.attribute_type, a.attribute_value
        ORDER BY units_sold DESC
    """, [atype, str(start), str(end)])

@st.cache_data(ttl=300)
def load_segment_data(start, end):
    return get_data("""
        SELECT cu.segment,
               COUNT(DISTINCT cu.customer_id) AS customers,
               COUNT(s.sale_id) AS orders,
               ROUND(SUM(s.total_amount), 2) AS revenue,
               ROUND(AVG(s.total_amount), 2) AS avg_order_value
        FROM sales s
        JOIN customers cu ON s.customer_id = cu.customer_id
        WHERE s.sale_date >= ? AND s.sale_date <= ?
        GROUP BY cu.segment ORDER BY revenue DESC
    """, [str(start), str(end)])

@st.cache_data(ttl=300)
def load_channel_data(start, end):
    return get_data("""
        SELECT channel, COUNT(*) AS orders,
               SUM(quantity) AS units_sold,
               ROUND(SUM(total_amount), 2) AS revenue,
               ROUND(AVG(discount_percent), 1) AS avg_discount
        FROM sales
        WHERE sale_date >= ? AND sale_date <= ?
        GROUP BY channel ORDER BY revenue DESC
    """, [str(start), str(end)])

@st.cache_data(ttl=300)
def load_brand_share(start, end):
    return get_data("""
        SELECT p.brand,
               COUNT(DISTINCT p.product_id) AS products,
               SUM(s.quantity) AS units_sold,
               ROUND(SUM(s.total_amount), 2) AS revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE s.sale_date >= ? AND s.sale_date <= ?
        GROUP BY p.brand ORDER BY revenue DESC
    """, [str(start), str(end)])


# ── Color palette ──
COLORS = ["#6366f1", "#14b8a6", "#f59e0b", "#ec4899", "#8b5cf6",
          "#06b6d4", "#f97316", "#84cc16", "#a78bfa", "#fb7185"]


# ═══════════════════════════════════════════════════════════════
# HEADER & KPI CARDS
# ═══════════════════════════════════════════════════════════════

st.title("👗 Fashion Trend Forecasting & Sales Intelligence")
st.caption(f"Analytics for {start_date.strftime('%b %Y')} — {end_date.strftime('%b %Y')}")

df_monthly = load_monthly_sales(channel_filter, start_date, end_date)

if not df_monthly.empty:
    total_revenue = df_monthly["revenue"].sum()
    total_orders = int(df_monthly["total_orders"].sum())
    total_units = int(df_monthly["units_sold"].sum())
    avg_order = total_revenue / total_orders if total_orders > 0 else 0
    months_count = len(df_monthly)
    avg_monthly_rev = total_revenue / months_count if months_count > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    k2.metric("Total Orders", f"{total_orders:,}")
    k3.metric("Units Sold", f"{total_units:,}")
    k4.metric("Avg Order Value", f"₹{avg_order:,.0f}")
    k5.metric("Monthly Avg", f"₹{avg_monthly_rev:,.0f}")
else:
    st.warning("No data for selected filters.")

st.divider()


# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Sales Trends",
    "🎨 Attributes",
    "🗺️ Regions",
    "📦 Inventory",
    "🔗 Trends",
    "👥 Segments",
])


# ── Tab 1: Sales Trends ──
with tab1:
    if not df_monthly.empty:
        # Revenue line chart
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_monthly["month"], y=df_monthly["revenue"],
            mode="lines+markers",
            name="Revenue",
            line=dict(color="#6366f1", width=2.5),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(99,102,241,0.08)",
        ))
        fig_line.update_layout(
            title="Monthly Revenue Trend",
            template="plotly_white", height=380,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=50, b=20),
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig_line, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            df_top = load_top_products(top_n, start_date, end_date, selected_cats)
            if not df_top.empty:
                fig_top = px.bar(
                    df_top.sort_values("total_revenue"),
                    x="total_revenue", y="product_name",
                    orientation="h", color="category_name",
                    title=f"Top {top_n} Products by Revenue",
                    labels={"total_revenue": "Revenue (₹)", "product_name": ""},
                    color_discrete_sequence=COLORS,
                )
                fig_top.update_layout(template="plotly_white", height=420,
                                      margin=dict(l=20, r=20, t=50, b=20),
                                      font=dict(family="DM Sans"))
                st.plotly_chart(fig_top, use_container_width=True)

        with col2:
            df_channel = load_channel_data(start_date, end_date)
            if not df_channel.empty:
                fig_ch = px.pie(
                    df_channel, values="revenue", names="channel",
                    title="Revenue by Channel", hole=0.45,
                    color_discrete_sequence=["#6366f1", "#14b8a6", "#f59e0b"],
                )
                fig_ch.update_layout(height=420, font=dict(family="DM Sans"),
                                     margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_ch, use_container_width=True)

                st.dataframe(
                    df_channel.rename(columns={
                        "channel": "Channel", "orders": "Orders",
                        "units_sold": "Units", "revenue": "Revenue (₹)",
                        "avg_discount": "Avg Discount %",
                    }), use_container_width=True, hide_index=True,
                )


# ── Tab 2: Fashion Attributes ──
with tab2:
    df_attr = load_attribute_trends(attr_type, start_date, end_date)
    if not df_attr.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig_attr = px.bar(
                df_attr.head(12), x="attribute_value", y="units_sold",
                color="revenue", color_continuous_scale="Blues",
                title=f"Top {attr_type}s by Units Sold",
                labels={"attribute_value": attr_type, "units_sold": "Units Sold"},
            )
            fig_attr.update_layout(template="plotly_white", height=420,
                                   font=dict(family="DM Sans"),
                                   margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_attr, use_container_width=True)

        with col2:
            fig_pie = px.pie(
                df_attr.head(8), values="revenue", names="attribute_value",
                title=f"Revenue Share by {attr_type}", hole=0.45,
                color_discrete_sequence=COLORS,
            )
            fig_pie.update_layout(height=420, font=dict(family="DM Sans"),
                                  margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.dataframe(
            df_attr.rename(columns={
                "attribute_type": "Type", "attribute_value": attr_type,
                "units_sold": "Units Sold", "revenue": "Revenue (₹)",
            }), use_container_width=True, hide_index=True,
        )
    else:
        st.info("No attribute data for selected filters.")


# ── Tab 3: Regional Demand ──
with tab3:
    df_region = load_region_demand(start_date, end_date)
    if not df_region.empty:
        fig_region = px.bar(
            df_region, x="region", y="revenue",
            color="revenue", color_continuous_scale="Teal",
            title="Revenue by Region",
            labels={"region": "City", "revenue": "Revenue (₹)"},
        )
        fig_region.update_layout(template="plotly_white", height=400,
                                 font=dict(family="DM Sans"),
                                 margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_region, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig_scatter = px.scatter(
                df_region, x="total_orders", y="revenue",
                size="units_sold", color="region",
                title="Orders vs Revenue",
                labels={"total_orders": "Orders", "revenue": "Revenue (₹)"},
                color_discrete_sequence=COLORS,
            )
            fig_scatter.update_layout(template="plotly_white", height=400,
                                      showlegend=False, font=dict(family="DM Sans"),
                                      margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col2:
            st.dataframe(
                df_region.rename(columns={
                    "region": "City", "total_orders": "Orders",
                    "units_sold": "Units", "revenue": "Revenue (₹)",
                }), use_container_width=True, hide_index=True, height=380,
            )


# ── Tab 4: Inventory Risk ──
with tab4:
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### ⚠️ Low Stock Alert")
        df_risk = load_inventory_risk()
        if not df_risk.empty:
            fig_risk = px.bar(
                df_risk.head(12), x="product_name", y="deficit",
                color="deficit", color_continuous_scale="Reds",
                title=f"{len(df_risk)} Products Below Reorder Level",
                labels={"product_name": "", "deficit": "Units Short"},
            )
            fig_risk.update_layout(template="plotly_white", height=420,
                                   xaxis_tickangle=-45, font=dict(family="DM Sans"),
                                   margin=dict(l=20, r=20, t=50, b=80))
            st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.success("All products above reorder level!")

    with col_right:
        st.markdown("#### 🧊 Dead Stock")
        st.caption("Products with inventory but no sales in 90 days")
        df_dead = load_dead_stock()
        if not df_dead.empty:
            st.dataframe(
                df_dead.head(20).rename(columns={
                    "product_name": "Product", "brand": "Brand",
                    "stock_quantity": "Stock", "warehouse_location": "Warehouse",
                }), use_container_width=True, hide_index=True, height=420,
            )
            st.caption(f"Total dead stock: **{len(df_dead)} items**")
        else:
            st.success("No dead stock detected!")


# ── Tab 5: Trend Correlation ──
with tab5:
    df_trend = load_trend_correlation()
    if not df_trend.empty:
        fig_corr = px.scatter(
            df_trend, x="avg_trend_score", y="linked_revenue",
            size="linked_sales", color="keyword",
            title="Social Media Trend Score vs. Linked Revenue",
            labels={
                "avg_trend_score": "Avg Trend Score",
                "linked_revenue": "Linked Revenue (₹)",
                "linked_sales": "Sales Count",
            },
            hover_name="keyword",
            color_discrete_sequence=COLORS,
        )
        fig_corr.update_layout(template="plotly_white", height=500,
                               showlegend=False, font=dict(family="DM Sans"),
                               margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_corr, use_container_width=True)

        st.dataframe(
            df_trend.rename(columns={
                "keyword": "Trend Keyword", "avg_trend_score": "Score",
                "linked_sales": "Linked Sales", "linked_revenue": "Revenue (₹)",
            }), use_container_width=True, hide_index=True,
        )


# ── Tab 6: Customer Segments ──
with tab6:
    df_seg = load_segment_data(start_date, end_date)
    if not df_seg.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig_seg = px.bar(
                df_seg, x="segment", y="revenue", color="segment",
                title="Revenue by Segment",
                labels={"segment": "", "revenue": "Revenue (₹)"},
                color_discrete_sequence=["#14b8a6", "#0ea5e9", "#8b5cf6", "#e94560"],
            )
            fig_seg.update_layout(template="plotly_white", height=400,
                                  showlegend=False, font=dict(family="DM Sans"),
                                  margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_seg, use_container_width=True)

        with col2:
            fig_aov = px.bar(
                df_seg, x="segment", y="avg_order_value", color="segment",
                title="Avg Order Value by Segment",
                labels={"segment": "", "avg_order_value": "AOV (₹)"},
                color_discrete_sequence=["#14b8a6", "#0ea5e9", "#8b5cf6", "#e94560"],
            )
            fig_aov.update_layout(template="plotly_white", height=400,
                                  showlegend=False, font=dict(family="DM Sans"),
                                  margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_aov, use_container_width=True)

        # Brand market share
        df_brand = load_brand_share(start_date, end_date)
        if not df_brand.empty:
            fig_brand = px.treemap(
                df_brand, path=["brand"], values="revenue",
                title="Brand Market Share (by Revenue)",
                color="revenue", color_continuous_scale="Blues",
            )
            fig_brand.update_layout(height=400, font=dict(family="DM Sans"),
                                    margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_brand, use_container_width=True)


# ── Footer ──
st.divider()
st.markdown(
    "<div style='text-align:center; color:#94a3b8; font-size:0.75rem;'>"
    "Fashion Trend Forecasting & Sales Intelligence System &nbsp;•&nbsp; "
    "DBMS Course Project 2026"
    "</div>",
    unsafe_allow_html=True,
)
