#!/bin/bash

ENV_FILE=".env"

# Check if the .env file exists
if [ -f "$ENV_FILE" ]; then
    # Read values from the file and set them as variables
    while IFS='=' read -r key value || [[ -n "$key" ]]; do
        export "$key=$value"
    done < "$ENV_FILE"

    # Run your Python script or any other commands that need the environment variables
    # python njuskalo_scraper.py
    python summarize_cars.py
else
    echo "Error: $ENV_FILE not found."
fi
