#!/bin/bash

streamlit run app.py --server.port 8000 --server.address 0.0.0.0 --server.enableCORS false
chmod +x startup.sh     