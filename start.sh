#!/bin/bash
set -e
cd market-predictor
pip install -r requirements.txt
uvicorn app.api:app --host 0.0.0.0 --port $PORT