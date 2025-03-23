#!/bin/bash

# Configuration variables
URL="https://matrikacbs-dev.azurewebsites.net/api/TournamentFunbridgeImportHandler.ashx"  # Replace with your actual URL in the environment or when running
KEY="${KEY}"  # Replace with your API key in the environment or when running

# Check if the funbridge directory exists
if [ ! -d "funbridge" ]; then
    echo "Error: 'funbridge' directory not found."
    exit 1
fi

# Check if URL and KEY are provided
if [ -z "$URL" ] || [ -z "$KEY" ]; then
    echo "Error: URL or KEY environment variables are not set."
    echo "Usage: URL=your_url KEY=your_api_key ./upload_funbridge.sh"
    exit 1
fi

# Count the number of CSV files
csv_count=$(find funbridge -name "*.csv" | wc -l)
echo "Found $csv_count CSV files in the funbridge directory."

# Process each CSV file
for csv_file in funbridge/*.csv; do
    if [ -f "$csv_file" ]; then
        echo "Uploading: $csv_file"
        
        # Send POST request with curl
        response=$(curl -s -w "\n%{http_code}" \
            -X POST \
            -H "Authorization: Bearer $KEY" \
            -F "file=@$csv_file" \
            "$URL/api/tournaments")
        
        # Extract HTTP status code and response body
        http_code=$(echo "$response" | tail -n1)
        response_body=$(echo "$response" | sed '$d')
        
        # Check if the upload was successful
        if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
            echo "Success: $csv_file uploaded (HTTP $http_code)"
        else
            echo "Error uploading $csv_file (HTTP $http_code): $response_body"
        fi
    fi
done

echo "Upload process completed."
