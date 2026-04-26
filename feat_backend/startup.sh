#!/bin/bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker feat_backend.main:app:app