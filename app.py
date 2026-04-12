import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from config.settings import API_URL

st.set_page_config(
    page_title="Waste IoT Dashboard",
    page_icon="🗑️",
    layout="wide"
)

# ✅ Auto-refresh every 10 seconds
st_autorefresh(interval=10_000, key="autorefresh")

st.title("🗑️ Waste IoT Pipeline Dashboard")


# ✅ Cache API calls for 10 seconds to avoid hammering the API
@st.cache_data(ttl=10)
def fetch_stats():
    return requests.get(f"{API_URL}/stats").json()

@st.cache_data(ttl=10)
def fetch_latest():
    return requests.get(f"{API_URL}/latest").json()["data"]

@st.cache_data(ttl=10)
def fetch_readings(limit=20):
    return requests.get(f"{API_URL}/readings?limit={limit}").json()["data"]

@st.cache_data(ttl=10)
def fetch_alerts():
    return requests.get(f"{API_URL}/alerts").json()




st.subheader("📊 Overview")
stats = fetch_stats()
col1, col2 = st.columns(2)
col1.metric("Total Readings", stats["total_readings"])

st.subheader("📡 Latest Sensor Readings")
latest = fetch_latest()
for item in latest:
    sensor = item["latest"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sensor",      sensor.get("sensor_id"))
    col2.metric("Waste Level", f"{sensor.get('waste_level')}%")
    col3.metric("Battery",     f"{sensor.get('battery')}%") 
    is_full = sensor.get("is_full", False)
    col4.metric("Status", "🔴 FULL" if is_full else "🟢 OK")


st.subheader("🚨 Full Bins Alert")

alerts = fetch_alerts()
if alerts["count"] > 0:
    st.error(f"{alerts['count']} bin(s) need emptying!")
    for item in alerts["full_bins"]:
        st.warning(f"📍 {item['latest'].get('location')} — {item['latest'].get('sensor_id')}")
else:
    st.success("All bins are OK")

st.subheader("📋 Recent Readings")
readings = fetch_readings(limit=20)
if readings:
    df = pd.DataFrame(readings)
    st.dataframe(df)

    st.subheader("📈 Waste Level Over Time")
    if "waste_level" in df.columns and "ingested_at" in df.columns:
        st.line_chart(df.set_index("ingested_at")["waste_level"])
else:
    st.warning("No data yet — make sure your pipeline is running!")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()  # clear cache so fresh data is fetched
    st.rerun()