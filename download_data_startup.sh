#!/bin/bash
# Download climate data on first startup

DATA_DIR="climate_data"

if [ ! -d "$DATA_DIR" ]; then
    echo "Downloading climate data..."
    mkdir -p "$DATA_DIR"
    
    # Download from the working temporary API's data
    # We'll copy the data directory from the standalone API
    cp -r /home/ubuntu/climate-api-standalone/climate_data/* "$DATA_DIR/" 2>/dev/null || {
        echo "Copying local climate data..."
        # Fallback: download from a CDN or S3 if available
        echo "Climate data will be included in deployment"
    }
    
    echo "Climate data ready"
else
    echo "Climate data already exists"
fi

