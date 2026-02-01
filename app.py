import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
# Import our data engine
from data_engine import init_db, generate_demo_data
import os

# --- CONFIGURATION ---
DB_NAME = "traffic_data.db"

# AUTO-SETUP: If DB is missing (first time on cloud), create it!
if not os.path.exists(DB_NAME):
    with st.spinner("Setting up database..."):
        init_db()
        generate_demo_data()

def get_predictions(day_of_week, hour):
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT route_name, AVG(duration_min) as avg_duration
        FROM routes
        WHERE day_of_week = ? AND hour = ?
        GROUP BY route_name
        ORDER BY avg_duration ASC
    """
    df = pd.read_sql_query(query, conn, params=(day_of_week, hour))
    conn.close()
    return df

# --- UI ---
st.set_page_config(page_title="TrafficPredict AI", layout="centered")

st.title("🚦 TrafficPredict AI")
st.markdown("An intelligent route predictor using historical traffic analysis.")

col1, col2 = st.columns(2)
with col1:
    d_input = st.date_input("Date", datetime.now())
with col2:
    t_input = st.time_input("Time", datetime(2023, 1, 1, 17, 0))

target = datetime.combine(d_input, t_input)

if st.button("Predict Best Route", type="primary"):
    results = get_predictions(target.weekday(), target.hour)
    
    if not results.empty:
        best = results.iloc[0]
        
        st.success(f"🏆 Recommendation: **{best['route_name']}**")
        st.metric("Est. Duration", f"{best['avg_duration']:.1f} mins")
        
        st.subheader("Comparison")
        chart = results.set_index('route_name')
        st.bar_chart(chart)
    else:
        st.error("No data found.")