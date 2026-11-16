#!/usr/bin/env python3
"""
Indian Railways AI Train Delay Prediction Platform - Demo & Launch Script
"""
import sys
import os
import argparse
from datetime import date

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.ml.predictor import TrainDelayPredictor

def run_cli_prediction():
    print("=" * 70)
    print(" INDIAN RAILWAYS AI TRAIN DELAY PREDICTION - CLI DEMO")
    print("=" * 70)
    
    predictor = TrainDelayPredictor()
    
    print("\n[INFO] Loaded Model:", predictor.model_name)
    print("[INFO] Model Ready:", predictor.is_ready())
    
    # Test cases representing various Indian railway scenarios
    scenarios = [
        {
            "name": "12951 Mumbai Tejas Rajdhani (Winter Fog @ Kota)",
            "train_number": "12951",
            "train_category": "Rajdhani",
            "distance_km": 920.0,
            "scheduled_departure": "17:00",
            "scheduled_arrival": "03:15",
            "journey_date": str(date(2026, 12, 15)),
            "previous_station_delay": 15.0,
            "weather_condition": "Fog",
            "congestion_level": "Normal"
        },
        {
            "name": "22436 Vande Bharat Express (Clear Corridor)",
            "train_number": "22436",
            "train_category": "Vande Bharat",
            "distance_km": 441.0,
            "scheduled_departure": "06:00",
            "scheduled_arrival": "10:08",
            "journey_date": str(date(2026, 11, 20)),
            "previous_station_delay": 0.0,
            "weather_condition": "Clear",
            "congestion_level": "Normal"
        },
        {
            "name": "12779 Goa Express (Severe Junction Congestion)",
            "train_number": "12779",
            "train_category": "Express",
            "distance_km": 1010.0,
            "scheduled_departure": "15:00",
            "scheduled_arrival": "06:10",
            "journey_date": str(date(2026, 11, 20)),
            "previous_station_delay": 45.0,
            "weather_condition": "Clear",
            "congestion_level": "High"
        }
    ]

    for sc in scenarios:
        print("\n" + "-" * 60)
        print(f"Scenario: {sc['name']}")
        print(f"Train: {sc['train_number']} ({sc['train_category']}) • Distance: {sc['distance_km']} km")
        print(f"Conditions: Weather={sc['weather_condition']}, Congestion={sc['congestion_level']}, Prev Delay={sc['previous_station_delay']}m")
        
        res = predictor.predict_delay(
            train_number=sc["train_number"],
            train_category=sc["train_category"],
            distance_km=sc["distance_km"],
            scheduled_departure=sc["scheduled_departure"],
            scheduled_arrival=sc["scheduled_arrival"],
            journey_date=sc["journey_date"],
            previous_station_delay=sc["previous_station_delay"],
            weather_condition=sc["weather_condition"],
            congestion_level=sc["congestion_level"]
        )

        print(f"\n>> AI Predicted Delay: +{res['predicted_delay_minutes']} minutes")
        print(f">> Expected Arrival:   {res['predicted_arrival_time']} (Scheduled: {sc['scheduled_arrival']})")
        print(f">> Delay Category:     {res['delay_category']}")
        print(f">> Late Probability:   {int(res['late_probability'] * 100)}%")
        print(f">> 90% Conf Interval:  [{res['confidence_interval']['lower']}m to {res['confidence_interval']['upper']}m]")
        print(">> Explanations:")
        for exp in res["explanation"]:
            print(f"   • {exp}")

    print("\n" + "=" * 70)
    print(" CLI Demo completed successfully!")
    print(" To launch the web application backend:")
    print("    python -m uvicorn backend.app.main:app --reload --port 8000")
    print(" To launch the frontend:")
    print("    cd frontend && npm run dev")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Indian Railways Delay Prediction Platform")
    parser.add_argument("--cli", action="store_true", help="Run interactive CLI delay predictions")
    parser.add_argument("--server", action="store_true", help="Start FastAPI uvicorn server")
    args = parser.parse_args()

    if args.server:
        import uvicorn
        uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        run_cli_prediction()

if __name__ == "__main__":
    main()
