import requests
import json
import os
import time

# API Key and Base URL
API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
BASE_URL = "https://api.opendota.com/api"
PRO_MATCHES_ENDPOINT = "/proMatches"
TARGET_MATCH_COUNT = 1000
REQUEST_DELAY = 1 # Delay in seconds between requests to avoid rate limiting

# Parameters for the API request
params = {
    "api_key": API_KEY
}

all_match_ids = []
last_match_id = None

print(f"Attempting to fetch {TARGET_MATCH_COUNT} pro match IDs...")

while len(all_match_ids) < TARGET_MATCH_COUNT:
    if last_match_id:
        params["less_than_match_id"] = last_match_id

    url = BASE_URL + PRO_MATCHES_ENDPOINT
    print(f"Fetching matches from: {url} with params: {params}")

    try:
        # Increased timeout for potentially slow API response
        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Parse the JSON response
        matches_data = response.json()

        if not matches_data:
            print("No more matches found from the API.")
            break # Exit loop if API returns empty list

        print(f"Fetched {len(matches_data)} matches in this batch.")

        # Extract match IDs from the current batch
        batch_match_ids = [match["match_id"] for match in matches_data]
        all_match_ids.extend(batch_match_ids)

        # Update the last_match_id for the next iteration
        last_match_id = matches_data[-1]["match_id"]

        print(f"Total match IDs collected: {len(all_match_ids)}")

        # Remove less_than_match_id if it was added, to avoid sending it if the loop finishes
        if "less_than_match_id" in params:
             del params["less_than_match_id"]

        # Optional: Add a delay to respect potential API rate limits
        time.sleep(REQUEST_DELAY)

    except requests.exceptions.Timeout:
        print(f"Error: The request to {url} timed out after 120 seconds. Retrying after delay...")
        time.sleep(5)
        continue # Retry the same request
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from OpenDota API: {e}. Stopping fetch.")
        break # Stop fetching on other request errors
    except json.JSONDecodeError:
        print("Error decoding JSON response from OpenDota API. Stopping fetch.")
        # print(f"Response text: {response.text}") # Avoid printing potentially large invalid response
        break
    except Exception as e:
        print(f"An unexpected error occurred: {e}. Stopping fetch.")
        break

# Ensure we only keep the target number of matches
final_match_ids = all_match_ids[:TARGET_MATCH_COUNT]
print(f"Collected a total of {len(final_match_ids)} match IDs.")

# Save match IDs to a file
output_dir = "/home/ubuntu/dota_data"
os.makedirs(output_dir, exist_ok=True)
match_ids_file = os.path.join(output_dir, "pro_match_ids.json")

with open(match_ids_file, "w") as f:
    json.dump(final_match_ids, f)

print(f"Saved {len(final_match_ids)} match IDs to {match_ids_file}")

