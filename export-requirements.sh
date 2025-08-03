#!/bin/bash

# Export requirements.txt for Poetry/pip deployment compatibility
# This script maintains a requirements.txt file from uv.lock for deployment environments

echo "Exporting requirements.txt from uv.lock..."
uv export --format requirements-txt --output-file requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Successfully exported requirements.txt"
    echo "📦 $(wc -l < requirements.txt) packages exported"
else
    echo "❌ Failed to export requirements.txt"
    exit 1
fi