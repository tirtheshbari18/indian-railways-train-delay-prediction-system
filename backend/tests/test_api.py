import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(scope="session")
def client():
    # 'with' context manager ensures FastAPI lifespan (table creation, seeding, training) runs
    with TestClient(app) as test_client:
        yield test_client

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_root_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "api_v1" in res.json()

def test_trains_list(client):
    res = client.get("/api/v1/trains")
    assert res.status_code == 200
    trains = res.json()
    assert isinstance(trains, list)
    assert len(trains) > 0
    # Check that known train is present
    train_nums = [t["train_number"] for t in trains]
    assert "12951" in train_nums

def test_train_details(client):
    res = client.get("/api/v1/trains/12951")
    assert res.status_code == 200
    data = res.json()
    assert data["train_number"] == "12951"
    assert "routes" in data
    assert len(data["routes"]) > 0

def test_predict_delay(client):
    payload = {
        "train_number": "12951",
        "source_station": "MMCT",
        "destination_station": "NDLS",
        "target_station": "KOTA",
        "journey_date": "2026-11-20",
        "scheduled_departure": "17:00",
        "scheduled_arrival": "03:15",
        "previous_station_delay": 5.0,
        "weather_condition": "Clear",
        "congestion_level": "Normal"
    }
    res = client.post("/api/v1/predictions/predict-delay", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "prediction_id" in data
    assert "predicted_delay_minutes" in data
    assert "confidence_interval" in data
    assert "delay_category" in data
    assert "disclaimer" in data

def test_route_intermediate_predictions(client):
    payload = {
        "train_number": "12951",
        "journey_date": "2026-11-20",
        "initial_delay_minutes": 10.0,
        "weather_condition": "Clear"
    }
    res = client.post("/api/v1/routes/predict-intermediate-delays", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["train_number"] == "12951"
    assert "intermediate_stations" in data
    assert len(data["intermediate_stations"]) > 1

def test_dashboard_kpis(client):
    res = client.get("/api/v1/dashboard/kpis")
    assert res.status_code == 200
    data = res.json()
    assert "total_trains_analysed" in data
    assert "on_time_performance_pct" in data
    assert "active_model_name" in data

def test_analytics_endpoints(client):
    res1 = client.get("/api/v1/analytics/most-delayed-trains")
    assert res1.status_code == 200
    
    res2 = client.get("/api/v1/analytics/high-delay-sections")
    assert res2.status_code == 200
    
    res3 = client.get("/api/v1/analytics/punctuality-trends")
    assert res3.status_code == 200
