"""
Fashion Trend Forecasting & Sales Intelligence — Streamlit Dashboard
=====================================================================
Standalone version — reads directly from SQLite database.
No FastAPI backend needed for deployment.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import sqlite3
import os

# ── Page config ──
st.set_page_config(
    page_title="Fashion Trend Intelligence",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    h1 { color: #1a1a2e; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 6px;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# DATABASE CONNECTION
# ═══════════════════════════════════════════════════════════════

DB_PATH = os.path.join(os.path.dirname(__file__), "fashion_trend.db")

def get_data(query, params=None):
    """Run a SQL query and return a pandas DataFrame."""
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
    st.title("👗 Fashion Intelligence")
    st.caption("Trend Forecasting & Sales Analytics")
    st.divider()

    # Refresh
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # Filters
    st.subheader("Filters")
    attr_type = st.selectbox(
        "Attribute Type",
        ["Color", "Style", "Material", "Season", "Fit"],
        index=0,
    )
    top_n = st.slider("Top N Products", 5, 20, 10)

    # Channel filter
    channel_filter = st.multiselect(
        "Sales Channel",
        ["Online", "Store", "App"],
        default=["Online", "Store", "App"],
    )

    st.divider()
    st.caption("DBMS Course Project 2025")


# ═══════════════════════════════════════════════════════════════
# DATA LOADING (cached)
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def load_monthly_sales(channels):
    channels = list(channels)
    placeholders = ",".join(["?" for _ in channels])
    return get_data(f"""
        SELECT 
            strftime('%Y-%m', sale_date) AS month,
            COUNT(*) AS total_orders,
            SUM(quantity) AS units_sold,
            ROUND(SUM(total_amount), 2) AS revenue
        FROM sales
        WHERE channel IN ({placeholders})
        GROUP BY month
        ORDER BY month
    """, channels)

@st.cache_data(ttl=300)
def load_top_products(n):
    return get_data("""
        SELECT p.product_id, p.product_name, c.category_name,
               ROUND(SUM(s.total_amount), 2) AS total_revenue,
               SUM(s.quantity) AS total_units
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        GROUP BY p.product_id, p.product_name, c.category_name
        ORDER BY total_revenue DESC
        LIMIT ?
    """, [n])

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
        GROUP BY t.keyword
        ORDER BY avg_trend_score DESC
        LIMIT 15
    """)

@st.cache_data(ttl=300)
def load_region_demand():
    return get_data("""
        SELECT cu.region,
               COUNT(s.sale_id) AS total_orders,
               SUM(s.quantity) AS units_sold,
               ROUND(SUM(s.total_amount), 2) AS revenue
        FROM sales s
        JOIN customers cu ON s.customer_id = cu.customer_id
        GROUP BY cu.region
        ORDER BY revenue DESC
    """)

@st.cache_data(ttl=300)
def load_inventory_risk():
    return get_data("""
        SELECT p.product_id, p.product_name,
               i.stock_quantity, i.reorder_level,
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
def load_attribute_trends(atype):
    return get_data("""
        SELECT a.attribute_type, a.attribute_value,
               SUM(s.quantity) AS units_sold,
               ROUND(SUM(s.total_amount), 2) AS revenue
        FROM sales s
        JOIN product_attributes pa ON s.product_id = pa.product_id
        JOIN attributes a ON pa.attribute_id = a.attribute_id
        WHERE a.attribute_type = ?
        GROUP BY a.attribute_type, a.attribute_value
        ORDER BY units_sold DESC
    """, [atype])

@st.cache_data(ttl=300)
def load_segment_data():
    return get_data("""
        SELECT cu.segment,
               COUNT(DISTINCT cu.customer_id) AS customers,
               COUNT(s.sale_id) AS orders,
               ROUND(SUM(s.total_amount), 2) AS revenue,
               ROUND(AVG(s.total_amount), 2) AS avg_order_value
        FROM sales s
        JOIN customers cu ON s.customer_id = cu.customer_id
        GROUP BY cu.segment
        ORDER BY revenue DESC
    """)

@st.cache_data(ttl=300)
def load_channel_data():
    return get_data("""
        SELECT channel,
               COUNT(*) AS orders,
               SUM(quantity) AS units_sold,
               ROUND(SUM(total_amount), 2) AS revenue,
               ROUND(AVG(discount_percent), 1) AS avg_discount
        FROM sales
        GROUP BY channel
        ORDER BY revenue DESC
    """)


# ═══════════════════════════════════════════════════════════════
# HEADER & KPI CARDS
# ═══════════════════════════════════════════════════════════════

st.title("👗 Fashion Trend Forecasting & Sales Intelligence")
st.caption("Real-time analytics dashboard • DBMS Course Project 2025")

df_monthly = load_monthly_sales(channel_filter)

if not df_monthly.empty:
    total_revenue = df_monthly["revenue"].sum()
    total_orders = df_monthly["total_orders"].sum()
    total_units = df_monthly["units_sold"].sum()
    avg_order = total_revenue / total_orders if total_orders > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
    k2.metric("📦 Total Orders", f"{total_orders:,}")
    k3.metric("👕 Units Sold", f"{total_units:,}")
    k4.metric("📊 Avg Order Value", f"₹{avg_order:,.0f}")

st.divider()


# ═══════════════════════════════════════════════════════════════
# DASHBOARD TABS
# ═══════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Sales Trends",
    "🎨 Fashion Attributes",
    "🗺️ Regional Demand",
    "📦 Inventory Risk",
    "🔗 Trend Correlation",
    "👥 Customer Segments",
])


# ── Tab 1: Sales Trends ──
with tab1:
    if not df_monthly.empty:
        col1, col2 = st.columns([2, 1])

        with col1:
            fig_line = px.line(
                df_monthly, x="month", y="revenue",
                title="Monthly Revenue Trend",
                labels={"month": "Month", "revenue": "Revenue (₹)"},
                markers=True,
            )
            fig_line.update_layout(template="plotly_white", hovermode="x unified", height=400)
            st.plotly_chart(fig_line, use_container_width=True)

        with col2:
            fig_bar = px.bar(
                df_monthly, x="month", y="units_sold",
                title="Units Sold per Month",
                labels={"month": "Month", "units_sold": "Units"},
                color="units_sold",
                color_continuous_scale="Teal",
            )
            fig_bar.update_layout(template="plotly_white", showlegend=False, height=400)
            st.plotly_chart(fig_bar, use_container_width=True)

        # Top products
        df_top = load_top_products(top_n)
        if not df_top.empty:
            st.subheader(f"🏆 Top {top_n} Products by Revenue")
            fig_top = px.bar(
                df_top.sort_values("total_revenue"),
                x="total_revenue", y="product_name",
                orientation="h",
                color="category_name",
                labels={"total_revenue": "Revenue (₹)", "product_name": "Product"},
            )
            fig_top.update_layout(template="plotly_white", height=450, yaxis_title="")
            st.plotly_chart(fig_top, use_container_width=True)

        # Channel performance
        df_channel = load_channel_data()
        if not df_channel.empty:
            st.subheader("📱 Channel Performance")
            col1, col2 = st.columns(2)
            with col1:
                fig_ch = px.pie(
                    df_channel, values="revenue", names="channel",
                    title="Revenue by Channel", hole=0.4,
                )
                fig_ch.update_layout(height=350)
                st.plotly_chart(fig_ch, use_container_width=True)
            with col2:
                st.dataframe(
                    df_channel.rename(columns={
                        "channel": "Channel", "orders": "Orders",
                        "units_sold": "Units", "revenue": "Revenue (₹)",
                        "avg_discount": "Avg Discount %",
                    }),
                    use_container_width=True, hide_index=True,
                )
    else:
        st.info("No sales data available for selected filters.")


# ── Tab 2: Fashion Attributes ──
with tab2:
    df_attr = load_attribute_trends(attr_type)
    if not df_attr.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig_attr = px.bar(
                df_attr.head(15),
                x="attribute_value", y="units_sold",
                color="revenue",
                color_continuous_scale="Viridis",
                title=f"Top {attr_type}s by Units Sold",
                labels={"attribute_value": attr_type, "units_sold": "Units Sold"},
            )
            fig_attr.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig_attr, use_container_width=True)

        with col2:
            fig_pie = px.pie(
                df_attr.head(10),
                values="revenue", names="attribute_value",
                title=f"Revenue Share by {attr_type}", hole=0.4,
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.dataframe(
            df_attr.rename(columns={
                "attribute_value": attr_type,
                "units_sold": "Units Sold",
                "revenue": "Revenue (₹)",
            }),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No attribute data available.")


# ── Tab 3: Regional Demand ──
with tab3:
    df_region = load_region_demand()
    if not df_region.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig_region = px.bar(
                df_region.sort_values("revenue", ascending=False),
                x="region", y="revenue",
                color="total_orders",
                title="Revenue by Region",
                labels={"region": "City", "revenue": "Revenue (₹)"},
                color_continuous_scale="RdYlGn",
            )
            fig_region.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig_region, use_container_width=True)

        with col2:
            fig_scatter = px.scatter(
                df_region,
                x="total_orders", y="revenue",
                size="units_sold", color="region",
                title="Orders vs Revenue (bubble = units)",
                labels={"total_orders": "Orders", "revenue": "Revenue (₹)"},
            )
            fig_scatter.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No regional data available.")


# ── Tab 4: Inventory Risk ──
with tab4:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("⚠️ Low Stock Alert")
        df_risk = load_inventory_risk()
        if not df_risk.empty:
            fig_risk = px.bar(
                df_risk.head(15),
                x="product_name", y="deficit",
                color="deficit",
                color_continuous_scale="Reds",
                title="Stock Deficit (Reorder Level - Current Stock)",
                labels={"product_name": "Product", "deficit": "Deficit"},
            )
            fig_risk.update_layout(template="plotly_white", height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.success("All products are above reorder level!")

    with col_right:
        st.subheader("🧊 Dead Stock (No sales in 90 days)")
        df_dead = load_dead_stock()
        if not df_dead.empty:
            st.dataframe(
                df_dead.rename(columns={
                    "product_name": "Product", "brand": "Brand",
                    "stock_quantity": "Stock", "warehouse_location": "Warehouse",
                }),
                use_container_width=True, hide_index=True, height=400,
            )
            st.caption(f"Total dead stock items: {len(df_dead)}")
        else:
            st.success("No dead stock detected!")


# ── Tab 5: Trend Correlation ──
with tab5:
    df_trend = load_trend_correlation()
    if not df_trend.empty:
        fig_corr = px.scatter(
            df_trend,
            x="avg_trend_score", y="linked_revenue",
            size="linked_sales", color="keyword",
            title="Social Trend Score vs. Linked Revenue",
            labels={
                "avg_trend_score": "Avg Trend Score",
                "linked_revenue": "Revenue from Linked Products (₹)",
                "linked_sales": "Linked Sales Count",
            },
            hover_name="keyword",
        )
        fig_corr.update_layout(template="plotly_white", height=500, showlegend=False)
        st.plotly_chart(fig_corr, use_container_width=True)

        st.subheader("📊 Trend Details")
        st.dataframe(
            df_trend.rename(columns={
                "keyword": "Trend Keyword",
                "avg_trend_score": "Trend Score",
                "linked_sales": "Linked Sales",
                "linked_revenue": "Revenue (₹)",
            }),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No trend correlation data available.")


# ── Tab 6: Customer Segments ──
with tab6:
    df_seg = load_segment_data()
    if not df_seg.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig_seg = px.bar(
                df_seg, x="segment", y="revenue",
                color="segment",
                title="Revenue by Customer Segment",
                labels={"segment": "Segment", "revenue": "Revenue (₹)"},
            )
            fig_seg.update_layout(template="plotly_white", height=400, showlegend=False)
            st.plotly_chart(fig_seg, use_container_width=True)

        with col2:
            fig_aov = px.bar(
                df_seg, x="segment", y="avg_order_value",
                color="segment",
                title="Avg Order Value by Segment",
                labels={"segment": "Segment", "avg_order_value": "Avg Order Value (₹)"},
            )
            fig_aov.update_layout(template="plotly_white", height=400, showlegend=False)
            st.plotly_chart(fig_aov, use_container_width=True)

        st.dataframe(
            df_seg.rename(columns={
                "segment": "Segment", "customers": "Customers",
                "orders": "Orders", "revenue": "Revenue (₹)",
                "avg_order_value": "Avg Order Value (₹)",
            }),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No segment data available.")


# ── Footer ──
st.divider()
st.caption(
    "Fashion Trend Forecasting & Sales Intelligence System • "
    "Built with Streamlit + SQLite + Plotly • "
    "DBMS Course Project 2025"
)
