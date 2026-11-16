# Indian Railways AI Train Delay Prediction & Punctuality Intelligence Platform

An enterprise-grade, machine-learning-driven analytics and delay prediction platform built for Indian Railways (भारतीय रेल). The system ingests historical operational run logs, performs strict chronological train/test splitting to eliminate future lookahead data leakage, trains and benchmarks multiple gradient boosting and regression algorithms, and provides route-level dynamic delay predictions with 90% confidence intervals and late arrival probabilities.

---

## Key Highlights & Capabilities

- **Real Machine Learning Engine**: Implements and benchmarks 4 models:
  1. **XGBoost Regressor** (Production default)
  2. **Gradient Boosting Regressor**
  3. **Random Forest Regressor**
  4. **Linear Regression**
- **Strict Chronological Splitting**: Enforces temporal integrity ($T_{\text{train}} < T_{\text{test}}$) to ensure zero future data leakage.
- **Route-Based Intermediate Station Engine**: Dynamically calculates delay propagation across every intermediate halt, accounting for bottleneck compounding at dense junctions (e.g., Kanpur Central, Pt. Deen Dayal Upadhyaya, Itarsi) and slack-time schedule buffer recovery on long clear stretches.
- **Uncertainty & Probability Modeling**: Computes 90% confidence intervals ($\pm 1.645 \times \text{RMSE}$) and normal CDF late arrival probabilities ($P(\text{Delay} > 15 \text{ min})$).
- **Clear AI Prediction Disclaimers**: Explicit visual demarcation separating AI predictions from actual GPS/live track circuit status.
- **Full Operational Data Ingestion**: Clean, validate, deduplicate, and impute missing values from CSV, Excel (`.xlsx`, `.xls`), and JSON formats.
- **Administrator Model Registry & Management**: Safe promotion safeguards—new models cannot be auto-promoted unless validation passes ($R^2 > 0$ and lower MAE).

---

## Architecture & Technology Stack

```
indian railway train delay prediction system/
├── backend/                       # Python FastAPI Backend
│   ├── app/
│   │   ├── api/                   # REST API Routers
│   │   │   ├── auth.py            # User authentication & RBAC
│   │   │   ├── trains.py          # Train routes & station catalog
│   │   │   ├── predictions.py     # Single-point delay prediction & confidence bounds
│   │   │   ├── routes.py          # Dynamic intermediate station prediction engine
│   │   │   ├── analytics.py       # Bottlenecks, sections, punctuality trends
│   │   │   ├── datasets.py        # File ingestion & cleaning pipeline
│   │   │   ├── models.py          # Training, benchmarking, activation
│   │   │   └── dashboard.py       # Aggregated KPIs & status metrics
│   │   ├── core/                  # Configuration, database engine, logging, security
│   │   ├── models/                # SQLAlchemy ORM models (13 relational tables)
│   │   ├── schemas/               # Pydantic validation schemas
│   │   ├── ml/                    # Feature engineering, model trainer, evaluator, predictor
│   │   │   └── artifacts/         # Stored .joblib models & standard scaler
│   │   ├── services/              # Data processor, benchmark seeder, route engine
│   │   └── main.py                # FastAPI app entry point & lifespan
│   ├── tests/                     # Pytest suite (ML, API, Data Processor)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                      # React 18 + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/            # Navbar, Sidebar, RouteTimeline, DelayGauge, MetricCard
│   │   ├── pages/                 # Dashboard, Prediction, Route, Analytics, Data, Models, History
│   │   ├── services/              # Axios API client
│   │   └── types/                 # TypeScript interfaces
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── data/                          # Sample benchmark datasets (CSV & JSON)
├── docker-compose.yml             # Orchestration: PostgreSQL 16 + Backend + Frontend
└── run_demo.py                    # Interactive CLI prediction demo & launch utility
```

### Stack Details
- **Frontend**: React.js 18, TypeScript, Tailwind CSS (Indian Railways Navy blue `#0B2545` & White aesthetic), Recharts, Lucide Icons, Vite.
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy ORM, Pydantic v2, Uvicorn.
- **Database**: PostgreSQL 16 (production) with automatic, zero-friction SQLite WAL fallback for local out-of-the-box development.
- **Machine Learning**: Scikit-learn, XGBoost, NumPy, Pandas, Joblib, SciPy.
- **Testing**: Pytest, Scikit-learn evaluation metrics (MAE, MSE, RMSE, $R^2$).

---

## Machine Learning Methodology

### 1. Feature Engineering
The pipeline processes raw railway operations into high-signal predictive features:
- `previous_station_delay`: Lag delay from prior checkpoint (momentum factor).
- `train_category_rank`: Signal priority hierarchy (Vande Bharat/Rajdhani = 1, Superfast = 2, Mail/Express = 3, Passenger = 4).
- `halt_duration_minutes`: Scheduled stoppage buffer at platform.
- `distance_km`: Inter-station distance.
- `dep_hour` & `dep_minute`: Time-of-day traffic density.
- `day_of_week_num` & `is_weekend`: Cyclical day effects.
- `weather_impact_score`: Fog and monsoon visibility friction factor (critical for Northern Railway winter corridors).
- `congestion_score`: Junction capacity rating (DDU, CNB, ET, BPL, NDLS).
- `historical_avg_route_delay`: Corridor-specific moving historical mean.

### 2. Chronological Split (No Data Leakage)
To prevent future lookahead leakage, records are sorted strictly by `journey_date`. The earliest 80% form the training set; the final 20% form the unseen test evaluation set:
$$\max(T_{\text{train}}) \le \min(T_{\text{test}})$$

### 3. Model Evaluation on Unseen Test Data
All models are evaluated on the held-out chronological test set:
- **Mean Absolute Error (MAE)**: Average absolute deviation in minutes.
- **Mean Squared Error (MSE)**: Penalizes severe outlier delays.
- **Root Mean Squared Error (RMSE)**: Standard error of delay estimation.
- **Coefficient of Determination ($R^2$)**: Variance explained by features.

### 4. Confidence Intervals & Late Probability
- **90% Confidence Interval**:
  $$[\max(0, \hat{y} - 1.645 \times \text{RMSE}), \hat{y} + 1.645 \times \text{RMSE}]$$
- **Late Arrival Probability**:
  $$P(\text{Delay} > 15 \text{ min}) = 1 - \Phi\left(\frac{15 - \hat{y}}{\text{RMSE}}\right)$$

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) Docker & Docker Compose

### Quickstart (Local Development)

#### 1. Backend Setup
```bash
# From repository root
python -m pip install -r backend/requirements.txt

# Run automated tests
python -m pytest backend/tests/ -v

# Launch the FastAPI backend server
python -m uvicorn backend.app.main:app --reload --port 8000
```
*On initial startup, the backend automatically initializes tables, seeds standard Indian Railways benchmark data, and trains the initial model suite.*
- Interactive API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

#### 2. Frontend Setup
```bash
# In a new terminal
cd frontend
npm install
npm run dev
```
- Open browser at `http://localhost:5173`

---

## Interactive CLI Demo

To quickly inspect model inference and scenario evaluations directly from terminal:
```bash
python run_demo.py
```
This runs 3 realistic operational scenarios:
1. **12951 Mumbai Tejas Rajdhani**: Heavy winter fog near Kota.
2. **22436 Vande Bharat Express**: Clear track with high operational precedence.
3. **12779 Goa Express**: Compounding delays at congested junctions.

---

## Docker Deployment (PostgreSQL + Backend + Frontend)

To deploy the entire platform with PostgreSQL 16:
```bash
docker-compose up --build
```
- Frontend UI: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432` (`railway_delay_db`)

---

## Relational Database Schema (13 Tables)

1. `trains`: Master registry of trains, categories, source/destination, and distance.
2. `stations`: Railway station codes, zones (NR, WR, CR, ER, etc.), states, divisions, GPS coordinates.
3. `train_routes`: Intermediate station halts, stop numbers, scheduled arrival/departure, distances.
4. `train_schedules`: Frequency and schedule metadata.
5. `historical_train_running`: Historical operational log of scheduled vs actual times, delays, weather.
6. `delay_records`: Discrete incident categorizations (On-Time, Slight, Moderate, Severe).
7. `imported_datasets`: Dataset file tracking, cleaning reports, and row counts.
8. `model_registry`: Versioned model artifacts, metrics (MAE, RMSE, $R^2$), and active status.
9. `model_training_history`: Log of training runs, loss, durations, and sample sizes.
10. `prediction_results`: Saved prediction instances with timestamps, expected times, and bounds.
11. `prediction_features`: Input feature vectors linked to predictions.
12. `users`: Credentials, full names, and roles (`admin`, `analyst`, `viewer`).
13. `audit_logs`: User actions, logins, training runs, and prediction queries.

---

## Default User Accounts

| Username | Password | Role | Permissions |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | Administrator | Full access: dataset upload, retrain models, activate model |
| `analyst` | `analyst123` | Data Analyst | Upload datasets, run training pipelines, view deep analytics |
| `viewer` | `viewer123` | Viewer / Passenger | Train search, single & route delay predictions, logs |

---

## Automated Test Coverage

Run the comprehensive pytest suite:
```bash
python -m pytest backend/tests/ -v
```
Tests include:
- `test_chronological_split`: Verifies strict chronological ordering with zero temporal leakage.
- `test_feature_extraction`: Validates feature transformations and absence of NaNs.
- `test_evaluation_metrics`: Tests MAE, RMSE, and $R^2$ calculation.
- `test_model_training_pipeline`: Fits and validates all 4 models.
- `test_predictor_inference`: Checks confidence bounds, probability bounds, and category mapping.
- `test_validate_and_clean_data`: Tests deduplication, outlier clipping, and missing value handling.
- `test_api_endpoints`: Integration testing of all FastAPI endpoints.
