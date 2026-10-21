@echo off
title Smart Library - FastAPI Backend Server (:8000)
echo ======================================================================
echo  Starting FastAPI REST API Backend Server...
echo  URL: http://127.0.0.1:8000
echo  Interactive Swagger Docs: http://127.0.0.1:8000/docs
echo ======================================================================
python api_server.py
pause
