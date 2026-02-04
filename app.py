import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# We don't need a DB file anymore. We generate data in memory (RAM) every time.

@st.cache_data
def get_mock_data():
    """
    Generates 30 days of mock traffic data instantly.
    '@st.cache_data' ensures we only generate it once per session.
    """
    data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        dow = current_date.weekday() 
        
        for hour in range(24):
            # Logic: Highway is bad at Rush Hour
            if not (dow >= 5) and (hour in [8, 9, 17, 18]):
                d_highway = 55 
            else:
                d_highway = 20 
            
            d_local = 35 
            d_toll = 18 

            data.append(("Route A: Highway", dow, hour, d_highway + random.randint(-2,2), current_date))
            data.append(("Route B: Local", dow, hour, d_local + random.randint(-2,2), current_date))
            data.append(("Route C: Toll Rd", dow, hour, d_toll + random.randint(-1,1), current_date))

    df = pd.DataFrame(data, columns=['route_name', 'day_of_week', 'hour', 'duration_min', 'timestamp'])
    return df

def get_predictions(df, day_of_week, hour):
    # Filter the in-memory DataFrame
    filtered = df[(df['day_of_week'] == day_of_week) & (df['hour'] == hour)]
    
    # Calculate averages
    results = filtered.groupby('route_name')['duration_min'].mean().reset_index()
    results = results.sort_values(by='duration_min')
    return results

# --- UI ---
st.set_page_config(page_title="TrafficPredict AI", layout="centered")

st.title("🚦 TrafficPredict AI")
st.markdown("An intelligent route predictor using historical traffic analysis.")

# Get the data
df = get_mock_data()

col1, col2 = st.columns(2)
with col1:
    d_input = st.date_input("Date", datetime.now())
with col2:
    t_input = st.time_input("Time", datetime(2023, 1, 1, 17, 0))

target = datetime.combine(d_input, t_input)

if st.button("Predict Best Route", type="primary"):
    results = get_predictions(df, target.weekday(), target.hour)
    
    if not results.empty:
        best = results.iloc[0]
        
        st.success(f"🏆 Recommendation: **{best['route_name']}**")
        st.metric("Est. Duration", f"{best['duration_min']:.1f} mins")
        
        st.subheader("Comparison")
        chart = results.set_index('route_name')
        st.bar_chart(chart)
    else:

        st.error("No data found.")
