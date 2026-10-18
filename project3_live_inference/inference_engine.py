"""Universal Live Inference Engine for Project 3.
Bridges Project 1 (live data collector) and Project 2 (TimesFM forecasting model)
to forecast future trajectories and evaluate 'Chance of Weather Change' globally.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from project2_timesfm_model.timesfm_pipeline import TimesFMPipeline
from project3_live_inference.change_detector import WeatherChangeDetector
from weather_agent.geocoding import resolve_location
from weather_agent.service import get_forecast
from weather_agent.storage import connect


class LiveInferenceEngine:
    def __init__(
        self,
        db_path: str = "data/weather.sqlite3",
        horizon_len: int = 24,
    ):
        self.db_path = db_path
        self.horizon_len = horizon_len
        self.detector = WeatherChangeDetector()
        self.model = TimesFMPipeline(horizon_len=horizon_len)

    def analyze_location(self, location_query: str) -> dict[str, Any]:
        """Fetch recent context, run TimesFM inference, and compute chance of weather change."""
        con = connect(self.db_path)
        loc = resolve_location(con, location_query)
        if not loc:
            return {"error": f"Location '{location_query}' could not be resolved."}

        # 1. Retrieve recent context values from SQLite
        rows = con.execute(
            """SELECT valid_at, temperature_c, humidity_pct, precipitation_mm, wind_speed_kmh
               FROM weather_records
               WHERE location_id = ?
               ORDER BY valid_at ASC
               LIMIT 168""",
            (loc.location_id,),
        ).fetchall()

        temps = [r["temperature_c"] for r in rows if r["temperature_c"] is not None]
        rains = [r["precipitation_mm"] or 0.0 for r in rows]
        winds = [r["wind_speed_kmh"] or 0.0 for r in rows]

        # If sparse history in DB, fetch live forecast baseline from Project 1 service
        forecast_service_data = get_forecast(con, loc.location_id, days=1)
        hourly_preview = forecast_service_data.get("hourly_preview", [])
        
        forecast_temps = [h["temp_c"] for h in hourly_preview if h.get("temp_c") is not None]
        forecast_rains = [h["rain_mm"] for h in hourly_preview if h.get("rain_mm") is not None]
        forecast_winds = [h["wind_kmh"] for h in hourly_preview if h.get("wind_kmh") is not None]

        # Run TimesFM inference if context exists
        if len(temps) >= 12:
            tfm_predicted_temps = self.model.forecast(temps, horizon_len=self.horizon_len)
        else:
            tfm_predicted_temps = forecast_temps

        # 2. Detect abrupt shifts & anomalies
        alerts = []
        
        # Cold plunge
        temp_alert = self.detector.detect_temperature_shock(temps if temps else [20.0], tfm_predicted_temps)
        if temp_alert:
            alerts.append(temp_alert)

        # Extreme heat surge
        heat_alert = self.detector.detect_heatwave(temps if temps else [20.0], tfm_predicted_temps)
        if heat_alert:
            alerts.append(heat_alert)

        # Rain / flood burst
        rain_alert = self.detector.detect_precipitation_burst(forecast_rains)
        if rain_alert:
            alerts.append(rain_alert)

        # Wind surge
        wind_alert = self.detector.detect_wind_surge(forecast_winds)
        if wind_alert:
            alerts.append(wind_alert)

        chance_of_change = self.detector.calculate_overall_chance_of_change(alerts)

        return {
            "location": loc.name,
            "district": loc.district,
            "province": loc.province,
            "country_code": getattr(loc, "country_code", ""),
            "elevation_m": loc.elevation_m,
            "forecast_horizon_hours": self.horizon_len,
            "chance_of_weather_change_pct": chance_of_change,
            "change_status": "STABLE" if chance_of_change < 30 else ("MODERATE_SHIFT" if chance_of_change < 65 else "HIGH_VOLATILITY"),
            "model_used": f"Google TimesFM ({self.model.backend})",
            "active_alerts": [
                {
                    "type": a.alert_type,
                    "severity": a.severity,
                    "probability_pct": f"{a.probability_pct}%",
                    "summary": a.summary,
                    "detail": a.detail,
                }
                for a in alerts
            ],
            "projected_temperature_next_24h": tfm_predicted_temps[:24],
            "disclaimer": "Experimental AI inference. For official life-safety warnings, refer to your national meteorological agency (e.g. DHM, NOAA, Met Office, JMA).",
        }
