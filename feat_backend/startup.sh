#!/bin/bash
# gunicorn [워커개수] [워커타입] [폴더경로.파일이름:FastAPI객체이름]
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app