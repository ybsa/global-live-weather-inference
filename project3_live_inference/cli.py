"""CLI tool for Project 3: Live Inference & Weather Change Detection."""
from __future__ import annotations

import argparse
import json
from project3_live_inference.inference_engine import NepalLiveInferenceEngine


def main():
    parser = argparse.ArgumentParser(description="Project 3: Live Inference & Weather Change Forecast for Nepal")
    parser.add_argument("location", help="Town or village name (e.g. 'Ghandruk', 'Namche Bazaar', 'Jumla')")
    parser.add_argument("--horizon", type=int, default=24, help="Forecast horizon hours (default: 24)")
    parser.add_argument("--database", default="data/weather.sqlite3", help="Path to Project 1 SQLite database")

    args = parser.parse_args()

    engine = NepalLiveInferenceEngine(db_path=args.database, horizon_len=args.horizon)
    result = engine.analyze_location(args.location)

    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)

    print("\n=======================================================")
    print(f"  NEPAL WEATHER INTELLIGENCE — LIVE INFERENCE REPORT")
    print(f"  Location: {result['location']} ({result['district']}, {result['province']})")
    print(f"  Elevation: {result['elevation_m']} m")
    print("=======================================================")
    print(f"  CHANCE OF WEATHER CHANGE: {result['chance_of_weather_change_pct']}%  [{result['change_status']}]")
    print(f"  Model Engine: {result['model_used']}")
    print("-------------------------------------------------------")

    if result["active_alerts"]:
        print("  ACTIVE WEATHER SHIFT ALERTS:")
        for al in result["active_alerts"]:
            print(f"   [{al['severity']}] {al['type']} (Prob: {al['probability_pct']})")
            print(f"      • {al['summary']}")
            print(f"      • {al['detail']}")
    else:
        print("  Status: No abrupt shocks (cloudburst, frost plunge, or gale winds) detected in current window.")

    print("\n  24-Hour Projected Temperature Trajectory:")
    sample_temps = result["projected_temperature_next_24h"]
    if sample_temps:
        print(f"    Min: {min(sample_temps)}°C | Max: {max(sample_temps)}°C")
        print(f"    Hourly: {sample_temps[:12]}...")

    print(f"\n  Disclaimer: {result['disclaimer']}")
    print("=======================================================\n")


if __name__ == "__main__":
    main()
