#!/usr/bin/env bash

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment"
    python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter Notebook
jupyter notebook lookatdata.ipynb
