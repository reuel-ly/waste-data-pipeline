import streamlit as st
import requests
import pandas as pd
from config.settings import API_URL

API_URL = API_URL

st.set_page_config(
    page_title="Waste IoT Dashboard",
    page_icon="🗑️",
    layout="wide"
)

st.title("🗑️ Waste IoT Pipeline Dashboard")


st.subheader("📊 Overview")

stats = requests.get(f"{API_URL}/stats").json()
col1, col2 = st.columns(2)
col1.metric("Total Readings", stats["total_readings"])

st.subheader("📡 Latest Sensor Readings")

latest = requests.get(f"{API_URL}/latest").json()["data"]
for item in latest:
    sensor = item["latest"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Sensor",      sensor.get("sensor_id"))
    col2.metric("Waste Level", f"{sensor.get('waste_level')}%")
    col3.metric("Battery",     f"{sensor.get('battery')}%")

st.subheader("📋 Recent Readings")

readings = requests.get(f"{API_URL}/readings?limit=20").json()["data"]
if readings:
    df = pd.DataFrame(readings)
    st.dataframe(df)

    # ── CHART ───────────────────────────────────
    st.subheader("📈 Waste Level Over Time")
    if "waste_level" in df.columns:
        st.line_chart(df.set_index("ingested_at")["waste_level"])
else:
    st.warning("No data yet — make sure your pipeline is running!")

# Auto refresh every 10 seconds
st.button("🔄 Refresh Data")