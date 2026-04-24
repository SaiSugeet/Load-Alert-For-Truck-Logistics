# Smart LoadAlert: Real-Time Truck Load & GPS Monitoring System

Smart LoadAlert is a Streamlit-based logistics monitoring dashboard that simulates truck load telemetry and GPS movement in real time. It is designed to demonstrate how freight operators can detect overload conditions early, visualize route-level activity, and maintain exportable telemetry records from a single lightweight interface.

This project addresses a practical logistics problem: overloaded trucks increase accident risk, damage road infrastructure, reduce fuel efficiency, and create compliance exposure. Smart LoadAlert turns that problem into an interactive monitoring workflow by combining threshold-based alerting, live telemetry visualization, and map-based tracking in a deployable web app.

## Overview

The current version is a simulation-first prototype for truck load monitoring. It allows users to stream synthetic telemetry, manually inject readings, monitor threshold breaches, inspect movement on a live map, and download the full session log as CSV.

Although the app currently uses simulated inputs, the system is structured to represent a practical IoT dashboard pattern and can be extended to real sensor ingestion through HTTP or MQTT.

## Features

- Real-time truck telemetry simulation for load and GPS movement
- Configurable overload threshold for alert generation
- Manual telemetry entry for testing specific scenarios
- Auto-stream mode for continuous simulated data generation
- Live KPI cards for current weight, current location, total points, and overload count
- Interactive weight history chart with threshold reference line
- Map-based visualization of the latest truck path using Folium
- Color-coded alert markers to distinguish normal vs overload readings
- CSV export for session telemetry logs
- Lightweight single-file architecture that is easy to deploy and extend

## Architecture / How It Works

At a high level, Smart LoadAlert follows a simple telemetry monitoring flow:

1. A user configures truck identity, overload threshold, starting coordinates, and simulation controls from the sidebar.
2. The app generates telemetry points or accepts manual entries containing timestamp, truck ID, weight, latitude, longitude, and alert status.
3. Each incoming point is evaluated with rule-based overload logic:

```python
alert = weight > threshold
```

4. Telemetry is stored in Streamlit session state as an in-memory log for the active session.
5. The dashboard renders:
   - current truck metrics
   - a time-series weight chart
   - a live map showing recent truck movement and overload events
6. Users can clear the log or export the accumulated telemetry as a CSV file.

### Data Flow

`Sidebar Inputs / Manual Entry / Auto Stream`
-> `Telemetry Simulation`
-> `Threshold-Based Alert Evaluation`
-> `Session-State Log`
-> `Charts + Map + Metrics + CSV Export`

### Current System Scope

- Frontend/UI: Streamlit dashboard
- Processing: in-app simulation and rule-based alerting
- Storage: session memory only
- Integration model: prototype ready to be connected to live HTTP/MQTT telemetry later

## Tech Stack

### Machine Learning / AI

- No ML model in the current version
- Rule-based overload detection using configurable threshold logic

### Backend / APIs

- Python 3.12
- Streamlit for the application runtime and UI layer
- In-memory session-state processing for telemetry handling

### Cloud / Deployment

- Streamlit Community Cloud ready
- Local deployment supported out of the box
- No Docker or dedicated cloud infrastructure configuration included yet

### Tools / Libraries

- Pandas for telemetry logging and transformation
- Plotly for time-series visualization
- Folium for map rendering
- `streamlit-folium` for embedding Folium maps inside Streamlit

## Performance & Metrics

The current project is a simulation-driven dashboard, so metrics below are based on observed application behavior and code-level limits rather than production benchmarking.

- Alert detection accuracy: `100%` for the implemented rule logic, because overload detection is a direct threshold comparison on each telemetry point
- Update latency: `<1s (approx)` per interaction/rerun on a typical local setup, depending on machine performance and browser responsiveness
- Telemetry throughput: `1-20 points per rerun` configurable in auto-stream mode
- Map window: last `30` telemetry points visualized on the live route map
- Dataset size: session-based and user-driven, with no hard-coded storage cap beyond active app memory
- Export capability: full in-session telemetry log downloadable as CSV

## Getting Started

### Prerequisites

- Python `3.10+` recommended
- `pip`

### Installation

```bash
git clone https://github.com/SaiSugeet/Load-Alert-For-Truck-Logistics.git
cd Load-Alert-For-Truck-Logistics
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the Project

```bash
streamlit run app.py
```

After launch, Streamlit will open the local app in your browser, typically at:

```text
http://localhost:8501
```

## Deployment

### Local

The app runs locally with Streamlit and stores telemetry only for the active browser session.

### Streamlit Community Cloud

This project is a good fit for Streamlit Community Cloud deployment:

1. Push the repository to GitHub
2. Sign in to Streamlit Community Cloud
3. Select this repository
4. Set the main file path to `app.py`
5. Deploy

Required deployment file:

- `requirements.txt`

Current deployment note:

- No cloud database, message broker, or API service is configured yet
- No Dockerfile is included in the current version

## Project Structure

```text
Load-Alert-For-Truck-Logistics/
├── app.py
├── requirements.txt
└── README.md
```

- `app.py` contains the full Streamlit dashboard, telemetry simulation logic, alert evaluation, charting, map rendering, and CSV export
- `requirements.txt` defines the Python dependencies needed for local setup and Streamlit deployment
- `README.md` documents the project, setup flow, and architecture

## Use Cases

- Fleet monitoring demos for logistics and telematics portfolios
- Prototype validation for truck overload alert systems
- Academic or open-source demonstration of IoT-style logistics dashboards
- Early-stage UI foundation for real sensor integrations
- Compliance and safety monitoring concepts for freight operations

## Future Improvements

- Replace simulated telemetry with real sensor ingestion via HTTP or MQTT
- Add support for multiple trucks and fleet-wide monitoring
- Persist telemetry in a database for historical analytics
- Add authentication and role-based dashboard access
- Introduce alert notifications through email, SMS, or messaging apps
- Add route replay, geofencing, and trip summaries
- Extend overload logic with anomaly detection or predictive analytics

## Contributing

Contributions are welcome. If you want to improve the dashboard, add real telemetry ingestion, or expand the monitoring workflow, feel free to fork the repository and open a pull request.

## License

No license file is included in the current repository. Add a license if you want to make reuse terms explicit for contributors and employers reviewing the project.
