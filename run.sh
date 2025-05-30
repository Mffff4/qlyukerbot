#!/bin/bash

first_run=true

check_uv() {
    if ! command -v uv &> /dev/null; then
        echo "uv is not installed. Installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        echo "Reloading shell to update PATH..."
        exec "$SHELL"
    fi
}

if [ ! -f ".env" ]; then
    echo "Copying configuration file..."
    cp .env-example .env
fi

check_uv

while true; do
    echo "Checking for updates..."
    git fetch
    git pull
    
    if [ "$first_run" = true ]; then
        echo "Starting the application for the first time..."
        uv run main.py
        first_run=false
    else
        echo "Restarting the application..."
        uv run main.py -a 1
    fi
    
    echo "Restarting program in 10 seconds..."
    sleep 10
done
