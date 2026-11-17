# PULSE dashboard: most reliable T20 players under pressure

SupeRR Selector Season 2, Round 1. A Streamlit app showing the PULSE top-10 batters and bowlers under pressure,
with charts, full rankings, the methodology and a player lookup.

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

## Deploy on Render
1. Push this folder to a GitHub repository.
2. Render -> New -> Web Service -> connect the repository (or New -> Blueprint to use render.yaml).
3. Settings:
   - Runtime: Python 3
   - Build command: pip install -r requirements.txt
   - Start command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   - Environment variable: PYTHON_VERSION = 3.11.9
   - Instance type: Free
4. Deploy, then open the onrender.com URL.

## Files
- app.py: the dashboard
- data/: PULSE results (batters, bowlers, calibration, summary, phase)
- .streamlit/config.toml: Rajasthan Royals theme colours
