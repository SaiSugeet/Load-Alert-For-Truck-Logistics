
import streamlit as st
import pandas as pd
import random
from datetime import datetime
import plotly.express as px
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="LoadAlert Simulator", layout="wide")

# --- Sidebar controls ---
st.sidebar.header("Simulator Controls")
truck_id = st.sidebar.text_input("Truck ID", value="KA01AB1234")
threshold = st.sidebar.number_input("Overload Threshold (tons)", value=10.0, min_value=0.1, step=0.5)
auto_stream = st.sidebar.checkbox("Auto stream data", value=False)
# Interval is only advisory for how many points to simulate per rerun (keeps UI responsive)
stream_interval = st.sidebar.slider("Stream interval (sec, advisory)", 0.5, 5.0, 1.0)
noise = st.sidebar.slider("Weight noise (%)", 0.0, 10.0, 1.0)
start_lat = st.sidebar.number_input("Start Latitude", value=12.9716, format="%.6f")
start_lon = st.sidebar.number_input("Start Longitude", value=77.5946, format="%.6f")
points_per_rerun = st.sidebar.slider("Points per rerun (auto)", 1, 20, 3)

# --- Session state to hold simulated log ---
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["timestamp", "truck_id", "weight_t", "lat", "lon", "alert"])

# keep a moving "current position" and "mean weight" for continuity
if "cur_lat" not in st.session_state:
    st.session_state.cur_lat = start_lat
if "cur_lon" not in st.session_state:
    st.session_state.cur_lon = start_lon
if "mean_weight" not in st.session_state:
    st.session_state.mean_weight = 8.0

# helper to simulate weight and GPS
def simulate_point(base_weight, threshold, lat, lon):
    # simulate slow movement
    lat += random.uniform(-0.0005, 0.0005)
    lon += random.uniform(-0.0005, 0.0005)
    # simulate weight around base with noise
    noise_factor = 1 + random.uniform(-noise/100.0, noise/100.0)
    weight = max(0.0, base_weight * noise_factor)
    # occasionally simulate a sudden change (load/unload)
    if random.random() < 0.08:
        weight += random.uniform(-base_weight * 0.6, base_weight * 0.6)
        weight = max(0.0, weight)
    alert = weight > threshold
    return round(weight, 3), round(lat, 6), round(lon, 6), alert

# --- Main layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.header("LoadAlert Dashboard (Simulator)")
    st.markdown(f"Simulating telemetry for: **{truck_id}**")

    # manual input
    base_weight = st.number_input("Manual weight input (tons)", value=st.session_state.mean_weight, step=0.1, key="manual_weight")
    manual_lat = st.number_input("Manual latitude", value=st.session_state.cur_lat)
    manual_lon = st.number_input("Manual longitude", value=st.session_state.cur_lon)
    if st.button("Send manual point"):
        w = float(base_weight)
        alert = w > threshold
        new_row = {
            "timestamp": datetime.utcnow().isoformat(),
            "truck_id": truck_id,
            "weight_t": round(w, 3),
            "lat": round(manual_lat, 6),
            "lon": round(manual_lon, 6),
            "alert": alert,
        }
        st.session_state.log = pd.concat([st.session_state.log, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.mean_weight = w
        st.session_state.cur_lat = manual_lat
        st.session_state.cur_lon = manual_lon

    st.markdown("---")

    # auto streaming: append a small batch of points each rerun to avoid blocking the UI
    if auto_stream:
        st.markdown("**Auto streaming is ON** — Streamlit will append points each rerun.")
        # Determine how many points to create this rerun. This keeps the app responsive.
        iterations = max(1, int(points_per_rerun))
        new_rows = []
        base = st.session_state.mean_weight
        lat = st.session_state.cur_lat
        lon = st.session_state.cur_lon
        for i in range(iterations):
            weight, lat, lon, alert = simulate_point(base, threshold, lat, lon)
            new_rows.append({
                "timestamp": datetime.utcnow().isoformat(),
                "truck_id": truck_id,
                "weight_t": weight,
                "lat": lat,
                "lon": lon,
                "alert": alert
            })
            # carry forward values so motion looks natural
            base = weight
        # append once
        st.session_state.log = pd.concat([st.session_state.log, pd.DataFrame(new_rows)], ignore_index=True)
        # update stored position/weight
        st.session_state.mean_weight = base
        st.session_state.cur_lat = lat
        st.session_state.cur_lon = lon
        st.info(f"Appended {len(new_rows)} simulated points (advisory interval {stream_interval}s).")

    # Show latest reading and alert + some metrics
    if not st.session_state.log.empty:
        latest = st.session_state.log.iloc[-1]
        st.subheader("Latest Telemetry")
        # metrics
        total_points = len(st.session_state.log)
        overload_count = st.session_state.log['alert'].sum()
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Weight (tons)", latest.weight_t)
        col_b.metric("Location", f"{latest.lat}, {latest.lon}")
        col_c.metric("Total points", total_points, delta=f"Overloads: {int(overload_count)}")
        if latest.alert:
            st.error(f"⚠ OVERLOAD detected! Weight > {threshold:.2f} tons")
        else:
            st.success("Normal: below threshold")

        # Plot weight history
        df = st.session_state.log.copy()
        df['ts'] = pd.to_datetime(df['timestamp'])
        fig = px.line(df, x='ts', y='weight_t', title='Weight history (tons)', markers=True)
        fig.add_hline(y=threshold, line_dash="dash", annotation_text="Threshold", annotation_position="top left")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No telemetry yet. Send a manual point or enable Auto stream.")

with col2:
    st.header("Map & Controls")
    st.markdown("Live truck position (last 30 points)")
    if st.session_state.log.empty:
        m = folium.Map(location=[start_lat, start_lon], zoom_start=12)
        folium.Marker([start_lat, start_lon], popup=f"{truck_id} (start)").add_to(m)
    else:
        latest = st.session_state.log.iloc[-1]
        m = folium.Map(location=[latest.lat, latest.lon], zoom_start=12)
        for _, r in st.session_state.log.tail(30).iterrows():
            color = "red" if r.alert else "blue"
            folium.CircleMarker(
                location=[r.lat, r.lon],
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f"{r.timestamp} | {r.weight_t}t"
            ).add_to(m)
        folium.Marker([latest.lat, latest.lon], popup=f"{truck_id} latest").add_to(m)
    st_folium(m, width=350, height=350)

    st.markdown("## Controls")
    if st.button("Clear log"):
        st.session_state.log = pd.DataFrame(columns=["timestamp", "truck_id", "weight_t", "lat", "lon", "alert"])
        st.success("Log cleared.")
    # provide CSV download of the full log
    if not st.session_state.log.empty:
        csv = st.session_state.log.to_csv(index=False)
        st.download_button("Download log as CSV", data=csv, file_name=f"{truck_id}_log.csv", mime="text/csv")

st.markdown("---")
st.caption("Simulator: Replace simulated points with HTTP/MQTT ingestion for real hardware integration.")
