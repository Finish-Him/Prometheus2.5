import requests
import json
import os

# API Key and Base URL
API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
BASE_URL = "https://api.opendota.com/api"
PRO_MATCHES_ENDPOINT = "/proMatches"

# Parameters for the API request
params = {
    "api_key": API_KEY
}

# Make the request
url = BASE_URL + PRO_MATCHES_ENDPOINT
print(f"Fetching pro matches from: {url}")
try:
    # Increased timeout for potentially slow API response
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

    # Parse the JSON response
    matches_data = response.json()
    print(f"Successfully fetched {len(matches_data)} pro matches.")

    # Get the latest 1000 match IDs (assuming the API returns them in descending order of start time)
    # Ensure we don't try to slice more matches than available
    num_matches_to_process = min(len(matches_data), 1000)
    match_ids = [match['match_id'] for match in matches_data[:num_matches_to_process]]
    print(f"Extracted {len(match_ids)} match IDs.")

    # Save match IDs to a file
    output_dir = "/home/ubuntu/dota_data"
    os.makedirs(output_dir, exist_ok=True)
    match_ids_file = os.path.join(output_dir, "pro_match_ids.json")

    with open(match_ids_file, 'w') as f:
        json.dump(match_ids, f)

    print(f"Saved {len(match_ids)} match IDs to {match_ids_file}")

except requests.exceptions.Timeout:
    print(f"Error: The request to {url} timed out after 120 seconds.")
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from OpenDota API: {e}")
except json.JSONDecodeError:
    print("Error decoding JSON response from OpenDota API.")
    # Avoid printing potentially huge invalid response text
    # print(f"Response text: {response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

