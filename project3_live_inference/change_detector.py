"""Weather Change & Anomaly Detection Engine for Nepal.
Computes the 'Chance of Weather Change' (CWC) and identifies abrupt shifts
such as cloudbursts, sudden temperature drops, and barometric pressure crashes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class WeatherShiftAlert:
    alert_type: str
    severity: str  # INFO, WARNING, CRITICAL
    probability_pct: int
    summary: str
    detail: str


class NepalChangeDetector:
    """Analyzes forecasted future time-series against recent context to detect abrupt shifts."""

    @staticmethod
    def detect_temperature_shock(context_temps: list[float], forecast_temps: list[float]) -> WeatherShiftAlert | None:
        """Detect sudden cold plunge (frost/cold wave) or heat spike."""
        if not context_temps or not forecast_temps:
            return None

        current = context_temps[-1]
        min_forecast = min(forecast_temps[:12])  # next 12 hours
        drop = current - min_forecast

        if drop >= 7.0 or min_forecast <= 0.0:
            prob = min(95, int(50 + drop * 6))
            sev = "CRITICAL" if min_forecast <= 0.0 else "WARNING"
            return WeatherShiftAlert(
                alert_type="Rapid Temperature Plunge",
                severity=sev,
                probability_pct=prob,
                summary=f"Temperature expected to drop sharply by {round(drop, 1)}°C down to {round(min_forecast, 1)}°C.",
                detail="High risk of ground frost, mountain hypothermia, and ice on high-altitude passes.",
            )
        return None

    @staticmethod
    def detect_precipitation_burst(forecast_rain: list[float]) -> WeatherShiftAlert | None:
        """Detect sudden heavy downpour / cloudburst risk."""
        if not forecast_rain:
            return None

        total_6h = sum(forecast_rain[:6])
        max_hourly = max(forecast_rain[:12]) if forecast_rain else 0.0

        if max_hourly >= 15.0 or total_6h >= 35.0:
            prob = min(92, int(60 + max_hourly * 2))
            return WeatherShiftAlert(
                alert_type="Flash Rain / Cloudburst Alert",
                severity="CRITICAL",
                probability_pct=prob,
                summary=f"Intense rainfall burst projected ({round(max_hourly, 1)} mm/hr, {round(total_6h, 1)} mm in 6h).",
                detail="Elevated flash flood and landslide risk in mountain gullies and river valleys.",
            )
        elif total_6h >= 15.0:
            prob = min(80, int(45 + total_6h * 1.5))
            return WeatherShiftAlert(
                alert_type="Developing Rain Event",
                severity="WARNING",
                probability_pct=prob,
                summary=f"Persistent rainfall expected ({round(total_6h, 1)} mm over 6h).",
                detail="Slippery rural roads and swelling local streams.",
            )
        return None

    @staticmethod
    def detect_wind_surge(forecast_winds: list[float]) -> WeatherShiftAlert | None:
        """Detect sudden mountain gale wind spikes."""
        if not forecast_winds:
            return None

        max_wind = max(forecast_winds[:12])
        if max_wind >= 45.0:
            prob = min(90, int(50 + (max_wind - 45) * 2))
            return WeatherShiftAlert(
                alert_type="High-Altitude Gale Wind Surge",
                severity="WARNING" if max_wind < 60.0 else "CRITICAL",
                probability_pct=prob,
                summary=f"Peak winds reaching {round(max_wind, 1)} km/h.",
                detail="Hazardous for high-altitude trekking, ridge passes, and STOL air operations.",
            )
        return None

    def calculate_overall_chance_of_change(self, alerts: list[WeatherShiftAlert]) -> int:
        """Calculate single aggregate Chance of Weather Change (0% to 100%)."""
        if not alerts:
            return 15  # Baseline normal weather variance
        max_prob = max(a.probability_pct for a in alerts)
        return min(98, max_prob + (len(alerts) - 1) * 5)
