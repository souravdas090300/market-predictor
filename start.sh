#!/bin/bash
cd market-predictor && uvicorn app.api:app --host 0.0.0.0 --port $PORT