"""Project 3: Universal Dashboard & Warning Agent.
Interactive Streamlit UI for multi-hour TimesFM forecasting and severe weather shift detection.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path so imports work seamlessly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import plotly.graph_objects as go
import streamlit as st

from project3_live_inference.inference_engine import LiveInferenceEngine

# Page Configuration
st.set_page_config(
    page_title="Weather Intelligence - Forecast & Warning Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1f2c; padding: 12px; border-radius: 8px; border: 1px solid #2d3748; }
    .alert-critical {
        background-color: #44131a;
        border-left: 5px solid #ff4b4b;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    .alert-warning {
        background-color: #3d2b0f;
        border-left: 5px solid #ffa500;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    .alert-stable {
        background-color: #123321;
        border-left: 5px solid #00c853;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar Controls
st.sidebar.title("⚡ Weather Intelligence")
st.sidebar.markdown("**Project 3: Global Forecast, Warning & Dashboard**")

db_path = st.sidebar.text_input("SQLite Database Path", value="data/weather.sqlite3")
horizon_hours = st.sidebar.slider("Forecast Horizon (Hours)", min_value=12, max_value=72, value=24, step=6)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Picks (Global Cities & Peaks)")
quick_picks = [
    "Tokyo", "London", "Dubai", "New York", "Namche Bazaar",
    "Paris", "Kathmandu", "Zurich", "Singapore", "Sydney"
]

selected_location = st.sidebar.selectbox("Choose a location or type below", quick_picks, index=0)
search_query = st.text_input("Search Location (Any city, country, or mountain village globally):", value=selected_location)

if search_query:
    engine = LiveInferenceEngine(db_path=db_path, horizon_len=horizon_hours)
    
    with st.spinner(f"Running TimesFM forecasting & risk analysis for '{search_query}'..."):
        result = engine.analyze_location(search_query)

    if "error" in result:
        st.error(result["error"])
    else:
        # Header Info
        col_title, col_stat = st.columns([3, 1])
        with col_title:
            country_display = f" ({result.get('country_code', '')})" if result.get('country_code') else ""
            st.title(f"📍 {result['location']}{country_display}")
            st.caption(f"{result['district']}, {result['province']} | Elevation: {result['elevation_m']} meters | Model: {result['model_used']}")

        with col_stat:
            prob = result["chance_of_weather_change_pct"]
            status = result["change_status"]
            st.metric(
                label="Chance of Weather Change",
                value=f"{prob}%",
                delta=status,
                delta_color="inverse" if prob >= 50 else "normal",
            )

        st.markdown("---")

        # Warning / Alert Section
        st.subheader("⚠️ Severe Weather Shift Alerts")
        alerts = result.get("active_alerts", [])
        if alerts:
            for al in alerts:
                css_class = "alert-critical" if al.get("severity") == "CRITICAL" else "alert-warning"
                st.markdown(
                    f"""
                    <div class="{css_class}">
                        <h4 style="margin:0 0 6px 0;">🚨 [{al.get('severity')}] {al.get('type')} (Probability: {al.get('probability_pct')}%)</h4>
                        <p style="margin:0 0 4px 0; font-size: 15px;">{al.get('summary')}</p>
                        <small style="color: #cbd5e1;">{al.get('detail')}</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div class="alert-stable">
                    <h4 style="margin:0; color:#4ade80;">✅ Conditions Stable</h4>
                    <p style="margin:4px 0 0 0; color:#94a3b8; font-size:14px;">No abrupt cloudburst, freezing shock, or gale surges detected in the current window.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # TimesFM Forecasting Trajectory
        st.subheader("📈 TimesFM Projected Temperature Trajectory")
        temps = result.get("projected_temperature_next_24h", [])
        
        if temps:
            hours = [f"+{i+1}h" for i in range(len(temps))]
            fig = go.Figure()
            
            fig.add_trace(
                go.Scatter(
                    x=hours,
                    y=temps,
                    mode="lines+markers",
                    name="Projected Temp (°C)",
                    line=dict(color="#38bdf8", width=3),
                    marker=dict(size=6, color="#0284c7"),
                )
            )

            # Highlighting freeze threshold
            if min(temps) <= 0.0:
                fig.add_hline(
                    y=0.0,
                    line_dash="dash",
                    line_color="#ef4444",
                    annotation_text="Freezing Threshold (0°C)",
                    annotation_position="bottom right",
                )

            fig.update_layout(
                template="plotly_dark",
                height=380,
                margin=dict(l=30, r=30, t=30, b=30),
                xaxis_title="Forecast Horizon",
                yaxis_title="Temperature (°C)",
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)

            col1, col2, col3 = st.columns(3)
            col1.metric("Projected Low", f"{min(temps):.1f} °C")
            col2.metric("Projected High", f"{max(temps):.1f} °C")
            col3.metric("Projected Delta", f"{max(temps) - min(temps):.1f} °C")

        # Life Safety Notice
        st.caption(f"**Safety Notice:** {result['disclaimer']}")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Project 1 collects data. Project 2 fine-tunes the TimesFM weights. Project 3 runs live forecasts, detects anomalies, and hosts this dashboard.")
