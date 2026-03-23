# AutoNOC-X 💣
**Self-Healing Network Automation System** for Linux-first NOC.

## What this project does
- Monitors HTTP, TCP and ICMP-style latency targets
- Tracks local system health (CPU, memory, disk)
- Detects incidents using configurable rules
- Executes safe auto-healing actions (simulated by default)
- Stores incidents, metrics and actions in SQLite
- Exposes a FastAPI backend
- Renders a dark NOC dashboard in Streamlit
- Includes a simulator for multi-node demo traffic

## Project structure
```text
autonoc-x/
├── backend/app/
│   ├── api/
│   ├── core/
│   ├── services/
├── dashboard/
├── simulator/
├── recovery/
├── alerts/
├── config/
├── data/
└── scripts/
```

## Run order

### 1) Create environment
```bash
cd autonoc-x
python -m venv .venv
source .venv/bin/activate

# Windows:
# .venv\Scripts\activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Start backend
```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 4) Start dashboard in another terminal
```bash
cd autonoc-x
source .venv/bin/activate
streamlit run dashboard/app.py
```

### 5) Optional: run simulator / demo scans
```bash
python simulator/generate_demo_data.py
python scripts/run_scan.py
```

## Open
- API docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8501

## Default behavior
Auto-healing runs in **safe mode** by default.
That means actions like `systemctl restart nginx` are **logged, not executed**, so your real host is not modified.

To enable real actions, edit:
```yaml
safe_mode: false
```
in `config/settings.yaml`

## Default demo targets
The config includes:
- Localhost web check
- Localhost SSH/TCP check
- Public DNS latency check
- Unhealthy demo node

You can edit `config/nodes.yaml` to add your own servers.

## What gets stored
SQLite database: `data/autonoc.db`

Tables:
- `metrics`
- `incidents`
- `actions`

## Demo scenarios
1. Stop a local HTTP server or point a node to a dead port
2. Run `python scripts/run_scan.py`
3. View generated incident and auto-heal action in dashboard

## Notes
- The system is built to be demo-safe and portfolio-friendly
- The recovery engine is extensible for real Linux NOC commands
- The dashboard is optimized for desktop presentation
