# Global Live Weather Inference, Forecast & Warning Dashboard

Project 3 provides **universal multi-hour weather forecasting**, **severe weather anomaly warnings**, and an **interactive visual Streamlit dashboard** for any city, village, or terrain globally.

Powered by Google's TimesFM foundation model and real-time open atmospheric data.

---

## ⚡ Features

- **Worldwide Location Coverage**: Search and forecast for any city or mountain village on Earth (Tokyo, London, Dubai, Zurich, Namche Bazaar, New York).
- **Multi-Hour Future Trajectory**: Generates 24-hour to 72-hour projected temperature curves with freezing thresholds.
- **Severe Weather Anomaly Rules**:
  * ☀️ **Severe Heatwave Spike**: Alerts for extreme heat surges (>= 38°C to 42°C+).
  * ❄️ **Rapid Temperature Plunge**: Alerts for sharp cold drops (>= 7°C) and sub-zero frostbite/hypothermia conditions.
  * 🌧️ **Downpour / Cloudburst Alert**: Flags dangerous flash flood precipitation bursts (>= 15mm/hr or >= 35mm in 6h).
  * 💨 **Severe Gale Surge**: Flags high wind speeds (>= 45 to 60+ km/h).
- **Chance of Weather Change (CWC)**: Single aggregate volatility metric (0% to 100%) indicating impending atmospheric shocks.
- **Interactive Web Dashboard**: Streamlit + Plotly visual interface.

---

## 🚀 Setup & Execution

### 1. Install Dependencies
```powershell
pip install -e ..\global-weather-data-agent
pip install -e .
```

*(Optional: To use pre-trained fine-tuned weights for Nepal's Himalayas, also install `pip install -e ..\nepal-timesfm-model`)*

### 2. Terminal Live Inference & Report
Run forecasting and anomaly risk evaluation for any city worldwide:
```powershell
weather-inference "Tokyo"
weather-inference "London"
weather-inference "Dubai"
weather-inference "Namche Bazaar"
```

### 3. Interactive Web Dashboard
Launch the interactive Streamlit dashboard:
```powershell
streamlit run project3_live_inference/dashboard.py
```

---

## 📊 Architecture

Project 3 is 100% modular:
- It consumes live atmospheric data from `global-weather-data-agent` (Project 1).
- It forecasts future steps using Google TimesFM foundation models (Project 2).
- It triggers automated safety warning banners and serves the UI.

## License
MIT. See [LICENSE](LICENSE).
