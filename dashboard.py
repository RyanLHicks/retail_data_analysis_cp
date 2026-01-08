import streamlit as st
import pandas as pd
import sqlalchemy
import os
import altair as alt
import io
from datetime import timedelta
from optimization_engine import calculate_inventory_metrics
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px

# --- Configuration --- #
st.set_page_config(page_title="Retail Pulse", layout="wide")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "retail.db")

# --- Helper Functions --- #
def get_shelf_limit(category_name: str) -> int:
    """Determines shelf limit based on category keywords."""
    cat_lower = category_name.lower()
    if "grocer" in cat_lower: return 192
    elif "apparel" in cat_lower or "cloth" in cat_lower: return 144
    elif "home" in cat_lower: return 96
    else: return 48

def clean_columns(df):
    """
    Standardizes column names for display:
    - Replaces underscores with spaces
    - Title cases the words (e.g., "product_name" -> "Product Name")
    - Renames specific technical terms for clarity
    """
    rename_map = {
        'store_id': 'Store ID',
        'product_id': 'Product ID',
        'product_name': 'Product Name',
        'units_on_hand': 'On Hand',
        'current_stock_on_hand': 'Current Stock',
        'weeks_of_supply': 'Weeks of Supply',
        'current_inventory': 'Current Inv',
        'unit_cost': 'Unit Cost ($)',
        'liability': 'Liability Risk ($)',
        'total_units_sold': 'Units Sold',
        'sales_amount': 'Revenue ($)',
        'product_width_inches': 'Width (in)',
        'facings': 'Facings',
        'city': 'City',
        'state': 'State'
    }
    # First apply specific map, then fallback to general formatting
    df_renamed = df.rename(columns=rename_map)
    df_renamed.columns = [c.replace('_', ' ').title() for c in df_renamed.columns]
    return df_renamed

# --- Database Connection --- #
@st.cache_resource
def get_db_connection():
    engine = sqlalchemy.create_engine(f"sqlite:///{DATABASE_PATH}", connect_args={"check_same_thread": False})
    try:
        with engine.connect() as connection:
            connection.execute(sqlalchemy.text("SELECT 1")).fetchall()
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        st.stop()
    return engine

engine = get_db_connection()

# --- SQL Queries --- #
ZERO_SALES_ALERT_QUERY = """
SELECT
    fs.store_id, dp.product_name, ds.city, ds.state, fi.units_on_hand
FROM
    (SELECT store_id, product_id, SUM(units_sold) AS total_sales_7_days
     FROM fact_sales WHERE date >= DATE('now', '-7 days') GROUP BY store_id, product_id) AS fs
JOIN fact_inventory AS fi ON fs.store_id = fi.store_id AND fs.product_id = fi.product_id
JOIN dim_product AS dp ON fs.product_id = dp.product_id
JOIN dim_store AS ds ON fs.store_id = ds.store_id
WHERE fs.total_sales_7_days = 0 AND fi.units_on_hand > 10
ORDER BY fs.store_id, dp.product_name;
"""

TOTAL_UNITS_SOLD_LAST_60_DAYS_QUERY = """
SELECT date, SUM(units_sold) AS total_units_sold
FROM fact_sales WHERE date >= DATE('now', '-60 days') GROUP BY date ORDER BY date;
"""

# --- Page Logic Functions --- #

def scenario_planner_logic():
    st.subheader("🛠️ Scenario Planner")
    st.markdown("Simulate impact of promotions on revenue.")

    c1, c2 = st.columns(2)
    with c1: discount_pct = st.slider("Price Discount (%)", 0, 50, 10, format="%d%%")
    with c2: uplift_pct = st.slider("Sales Uplift (%)", 0, 200, 20, format="%d%%")

    baseline_query = "SELECT SUM(sales_amount) AS rev, SUM(units_sold) AS vol FROM fact_sales WHERE date >= DATE('now', '-30 days');"
    try:
        df = pd.read_sql(baseline_query, engine)
        curr_rev = df['rev'].iloc[0] or 0.0
        curr_vol = df['vol'].iloc[0] or 0.0
        avg_price = (curr_rev / curr_vol) if curr_vol > 0 else 0

        proj_rev = (avg_price * (1 - discount_pct/100)) * (curr_vol * (1 + uplift_pct/100))
        net_impact = proj_rev - curr_rev

        m1, m2, m3 = st.columns(3)
        m1.metric("Current Revenue", f"${curr_rev:,.0f}")
        m2.metric("Projected Revenue", f"${proj_rev:,.0f}")
        m3.metric("Net Impact", f"${net_impact:,.0f}", delta=f"{net_impact:,.0f}", delta_color="normal" if net_impact >= 0 else "inverse")
    except Exception as e:
        st.error(f"Error: {e}")

def optimization_engine_logic():
    st.subheader("📦 Reset Readiness Tracker")
    st.markdown("Monitor inventory health for upcoming modular resets.")
    try:
        metrics_df = calculate_inventory_metrics(engine)
        if not metrics_df.empty:
            if 'Status' not in metrics_df.columns:
                np.random.seed(42)
                metrics_df['Status'] = np.random.choice(['Active', 'New Modular', 'Deleted'], size=len(metrics_df))
            
            flagged = metrics_df[(metrics_df['Status'] == 'New Modular') & (metrics_df['weeks_of_supply'] < 2)]
            
            if not flagged.empty:
                st.error(f"🚨 **Jeopardy Alert**: {len(flagged)} New Items have insufficient stock.")
                # CLEAN AND DISPLAY
                display_df = clean_columns(flagged[['product_name', 'current_inventory', 'weeks_of_supply', 'Status']])
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ All New Modular items are adequately stocked.")
    except Exception as e:
        st.error(f"Error: {e}")

def planogram_logic_page():
    st.subheader("📏 Planogram Validator")
    st.markdown("Validate if merchandising strategy fits physical shelf constraints.")
    try:
        df = pd.read_sql("SELECT product_name, category FROM dim_product", engine)
        if df.empty: return
        
        np.random.seed(42)
        df['product_width_inches'] = np.random.uniform(3, 8, len(df)).round(2)
        df['facings'] = 2 

        cats = sorted(df['category'].unique())
        selected_cat = st.selectbox("Select Category", cats)

        if selected_cat:
            limit = get_shelf_limit(selected_cat)
            df_cat = df[df['category'] == selected_cat].copy()
            total_needed = (df_cat['product_width_inches'] * df_cat['facings']).sum()

            c1, c2 = st.columns(2)
            c1.metric("Fixture Space", f"{limit}\"")
            c2.metric("Required Space", f"{total_needed:.1f}\"")

            if total_needed > limit:
                st.error(f"⚠️ **Overflow**: Cut **{total_needed - limit:.1f} inches**.")
            else:
                st.success(f"✅ **Fit Approved**: **{limit - total_needed:.1f} inches** spare.")
    except Exception as e:
        st.error(f"Error: {e}")

def markdowns_liability_logic():
    st.subheader("📉 Markdowns & Liability")
    try:
        metrics_df = calculate_inventory_metrics(engine)
        if not metrics_df.empty:
            if 'Status' not in metrics_df.columns:
                np.random.seed(42)
                metrics_df['Status'] = np.random.choice(['Active', 'New Modular', 'Deleted'], size=len(metrics_df))
            metrics_df['unit_cost'] = np.random.uniform(1.0, 20.0, len(metrics_df)).round(2)

            orphaned = metrics_df[(metrics_df['Status'] == 'Deleted') & (metrics_df['current_inventory'] > 0)].copy()
            if not orphaned.empty:
                orphaned['liability'] = orphaned['current_inventory'] * orphaned['unit_cost']
                # CLEAN AND DISPLAY
                display_df = clean_columns(orphaned[['product_name', 'current_inventory', 'unit_cost', 'liability']])
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No dead stock found.")
    except Exception as e:
        st.error(f"Error: {e}")

def ai_demand_forecasting_logic():
    st.subheader("🔮 AI Demand Forecasting")
    try:
        cats = pd.read_sql("SELECT DISTINCT category FROM dim_product", engine)
        if cats.empty: return
        
        sel_cat = st.selectbox("Select Category for Forecast", cats['category'].tolist())
        if sel_cat:
            df = pd.read_sql(f"""
                SELECT date, SUM(units_sold) as units, SUM(sales_amount) as rev 
                FROM fact_sales fs JOIN dim_product dp ON fs.product_id = dp.product_id
                WHERE dp.category = '{sel_cat}' AND fs.date >= DATE('now', '-30 days')
                GROUP BY date ORDER BY date""", engine)
            
            df['date'] = pd.to_datetime(df['date'])
            if len(df) < 2: 
                st.info("Insufficient data.")
                return

            df['day'] = (df['date'] - df['date'].min()).dt.days
            model = LinearRegression().fit(df[['day']], df['units'])
            
            last_day = df['day'].max()
            fut_days = np.array(range(last_day + 1, last_day + 8)).reshape(-1, 1)
            pred = np.maximum(0, model.predict(fut_days)).astype(int)
            
            avg_price = df['rev'].sum() / df['units'].sum() if df['units'].sum() else 0
            proj_rev = sum(pred) * avg_price

            fut_dates = pd.date_range(df['date'].max() + timedelta(1), periods=7)
            chart_df = pd.concat([
                df[['date', 'units']].assign(Type='Historical'),
                pd.DataFrame({'date': fut_dates, 'units': pred, 'Type': 'Predicted'})
            ])

            c1, c2 = st.columns([3, 1])
            fig = px.line(chart_df, x='date', y='units', color='Type', 
                          color_discrete_map={'Historical': '#1f77b4', 'Predicted': '#ff7f0e'})
            fig.update_traces(selector={'name': 'Predicted'}, line=dict(dash='dot', width=3))
            c1.plotly_chart(fig, use_container_width=True)
            c2.metric("Projected Revenue", f"${proj_rev:,.0f}")

    except Exception as e:
        st.error(f"Error: {e}")

# --- Main Layout --- #
st.title("Retail Pulse Dashboard")
st.markdown("A unified command center for retail analytics and operational insights.")

# Scorecard
try:
    rev = pd.read_sql("SELECT SUM(sales_amount) FROM fact_sales WHERE date >= DATE('now', '-30 days')", engine).iloc[0,0] or 0
    
    # Readiness logic simplified for scorecard
    m_df = calculate_inventory_metrics(engine)
    if not m_df.empty:
        if 'Status' not in m_df.columns: 
            np.random.seed(42)
            m_df['Status'] = np.random.choice(['Active','New Modular','Deleted'], size=len(m_df))
        new_m = m_df[m_df['Status'] == 'New Modular']
        ready_score = (len(new_m[new_m['weeks_of_supply']>=2]) / len(new_m) * 100) if not new_m.empty else 100
    else: ready_score = 0

    st.markdown("### 📊 Executive Overview")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("30-Day Revenue", f"${rev:,.0f}")
    k2.metric("Reset Readiness", f"{ready_score:.0f}%")
    k3.metric("Modular Integrity", "92%") # Hardcoded for stability in demo
    k4.metric("Liability Risk", "$12,450") # Hardcoded for stability in demo
except: pass

st.divider()

st.header("Vendor Control Tower")
try:
    df_u = pd.read_sql(TOTAL_UNITS_SOLD_LAST_60_DAYS_QUERY, engine)
    df_u['date'] = pd.to_datetime(df_u['date'])
    chart = alt.Chart(df_u).mark_line().encode(x='date:T', y='total_units_sold:Q', tooltip=['date', 'total_units_sold'])
    st.altair_chart(chart, use_container_width=True)
except: pass

st.divider()
st.markdown("### 🧩 Strategic Modules")

with st.expander("🛠️ Scenario Planner", expanded=False): scenario_planner_logic()
with st.expander("📦 Reset Readiness", expanded=False): optimization_engine_logic()
with st.expander("📏 Planogram Validator", expanded=False): planogram_logic_page()
with st.expander("📉 Liability Manager", expanded=False): markdowns_liability_logic()
with st.expander("🔮 AI Forecasting", expanded=False): ai_demand_forecasting_logic()