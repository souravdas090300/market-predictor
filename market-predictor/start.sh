#!/bin/bash
set -e
uvicorn app.api:app --host 0.0.0.0 --port $PORT
