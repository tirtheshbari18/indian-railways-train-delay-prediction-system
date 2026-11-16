import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.models.schema import Train, TrainRoute, Station, HistoricalTrainRunning
from backend.app.ml.predictor import TrainDelayPredictor
from backend.app.core.logging import logger

class RouteDelayPredictionEngine:
    def __init__(self, predictor: TrainDelayPredictor):
        self.predictor = predictor

    def predict_route_delays(
        self,
        db: Session,
        train_number: str,
        journey_date: datetime.date,
        initial_delay_minutes: float = 0.0,
        weather_condition: str = "Clear"
    ) -> Dict[str, Any]:
        """
        Simulate and predict delay evolution along every intermediate stop of the train's route.
        Accounts for:
        - Propagation of delay from prior station
        - Inter-station distance and run time
        - Station halt duration and buffer / slack time
        - Junction congestion rating
        - Weather friction
        """
        train = db.query(Train).filter(Train.train_number == train_number).first()
        if not train:
            raise ValueError(f"Train {train_number} not found in railway database.")

        routes = (
            db.query(TrainRoute)
            .filter(TrainRoute.train_number == train_number)
            .order_by(TrainRoute.stop_number)
            .all()
        )

        if not routes:
            raise ValueError(f"No route stops registered for train {train_number}.")

        # Retrieve station names
        station_codes = [r.station_code for r in routes]
        stations = db.query(Station).filter(Station.station_code.in_(station_codes)).all()
        st_name_map = {s.station_code: s.station_name for s in stations}

        intermediate_predictions = []
        cumulative_delay = float(initial_delay_minutes or 0.0)
        previous_dist = 0.0
        high_risk_segments = []
        recovery_opportunities = []

        for idx, stop in enumerate(routes):
            st_code = stop.station_code
            st_name = st_name_map.get(st_code, st_code)
            dist_from_src = float(stop.distance_from_source_km or 0.0)
            inter_dist = max(10.0, dist_from_src - previous_dist) if idx > 0 else 0.0
            previous_dist = dist_from_src

            # Congestion score by junction
            congestion = "Normal"
            if st_code in ["CNB", "DDU", "ET", "BPL", "NDLS", "HWH", "CSMT"]:
                congestion = "High"

            if idx == 0:
                # Origin Station: initial delay at origin
                predicted_arr_delay = 0.0
                delay_change = 0.0
                cumulative_delay = float(initial_delay_minutes or 0.0)
                pred_arr_time = stop.scheduled_departure
            else:
                # Intermediate or Destination Station
                # Run ML inference using cumulative_delay as previous_station_delay
                pred_result = self.predictor.predict_delay(
                    train_number=train.train_number,
                    train_category=train.train_category,
                    distance_km=inter_dist,
                    scheduled_departure=stop.scheduled_departure or "12:00",
                    scheduled_arrival=stop.scheduled_arrival or "12:00",
                    journey_date=str(journey_date),
                    previous_station_delay=cumulative_delay,
                    halt_duration_minutes=stop.halt_minutes,
                    weather_condition=weather_condition,
                    congestion_level=congestion
                )

                predicted_arr_delay = pred_result["predicted_delay_minutes"]
                delay_change = round(predicted_arr_delay - cumulative_delay, 1)
                cumulative_delay = predicted_arr_delay
                pred_arr_time = pred_result["predicted_arrival_time"]

                # Detect bottlenecks vs recovery
                prev_stop = routes[idx - 1]
                prev_name = st_name_map.get(prev_stop.station_code, prev_stop.station_code)
                segment_label = f"{prev_name} ({prev_stop.station_code}) -> {st_name} ({st_code})"

                if delay_change >= 8.0:
                    high_risk_segments.append(
                        f"{segment_label}: Compounding delay (+{delay_change}m) due to {congestion} congestion & traffic density."
                    )
                elif delay_change <= -4.0:
                    recovery_opportunities.append(
                        f"{segment_label}: Schedule buffer recovery ({delay_change}m) over {int(inter_dist)} km stretch."
                    )

            # Categorize this stop
            cat = self.predictor.get_delay_category(cumulative_delay)
            # Late probability
            z = (15.0 - cumulative_delay) / 14.5
            from scipy.stats import norm
            prob_late = round(float(1.0 - norm.cdf(z)), 3)
            prob_late = max(0.01, min(0.99, prob_late))

            intermediate_predictions.append({
                "station_code": st_code,
                "station_name": st_name,
                "stop_number": stop.stop_number,
                "scheduled_arrival": stop.scheduled_arrival,
                "scheduled_departure": stop.scheduled_departure,
                "predicted_arrival_time": pred_arr_time,
                "predicted_arrival_delay_minutes": round(predicted_arr_delay, 1),
                "cumulative_delay_minutes": round(cumulative_delay, 1),
                "delay_change_minutes": delay_change,
                "late_probability": prob_late,
                "delay_category": cat,
                "distance_km": dist_from_src
            })

        final_stop = routes[-1]
        final_scheduled = final_stop.scheduled_arrival or final_stop.scheduled_departure
        final_predicted = self.predictor.calculate_expected_arrival(final_scheduled, cumulative_delay)

        return {
            "train_number": train.train_number,
            "train_name": train.train_name,
            "source_station": train.source_station_code,
            "destination_station": train.dest_station_code,
            "journey_date": journey_date,
            "initial_departure_delay": round(float(initial_delay_minutes or 0.0), 1),
            "final_predicted_delay_minutes": round(cumulative_delay, 1),
            "final_scheduled_arrival": final_scheduled,
            "final_predicted_arrival": final_predicted,
            "total_distance_km": train.total_distance_km,
            "intermediate_stations": intermediate_predictions,
            "high_risk_segments": high_risk_segments if high_risk_segments else ["No severe high-risk bottlenecks identified along standard schedule."],
            "recovery_opportunities": recovery_opportunities if recovery_opportunities else ["Minor incremental schedule adjustments applied."]
        }
