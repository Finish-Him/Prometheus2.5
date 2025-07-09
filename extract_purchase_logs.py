import requests
import json
import os
import time

# API Key and Base URL
API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
BASE_URL = "https://api.opendota.com/api"
MATCH_ENDPOINT = "/matches/{match_id}"
REQUEST_DELAY = 1.1 # Increased delay to be safer with OpenDota rate limits (60/min)
MAX_RETRIES = 3
RETRY_DELAY = 5 # Seconds to wait before retrying a failed request

# Input and Output paths
input_dir = "/home/ubuntu/dota_data"
output_dir = "/home/ubuntu/dota_data"
match_ids_file = os.path.join(input_dir, "pro_match_ids.json")
output_json_file = os.path.join(output_dir, "purchase_logs_raw.json")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load match IDs
try:
    with open(match_ids_file, 'r') as f:
        match_ids = json.load(f)
    print(f"Loaded {len(match_ids)} match IDs from {match_ids_file}")
except FileNotFoundError:
    print(f"Error: Match IDs file not found at {match_ids_file}")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {match_ids_file}")
    exit()

all_purchase_data = []
processed_count = 0
total_matches = len(match_ids)

print(f"Starting purchase log extraction for {total_matches} matches...")

for match_id in match_ids:
    retries = 0
    success = False
    while retries < MAX_RETRIES and not success:
        url = BASE_URL + MATCH_ENDPOINT.format(match_id=match_id)
        params = {"api_key": API_KEY}
        # print(f"Fetching match details for match_id: {match_id} (Attempt {retries + 1}/{MAX_RETRIES})")

        try:
            response = requests.get(url, params=params, timeout=120)

            if response.status_code == 429: # Rate limit exceeded
                print(f"Rate limit hit for match {match_id}. Waiting {RETRY_DELAY * (retries + 1)}s before retry...")
                time.sleep(RETRY_DELAY * (retries + 1))
                retries += 1
                continue

            response.raise_for_status() # Raise an exception for other bad status codes (4xx or 5xx)

            match_data = response.json()

            if 'players' in match_data:
                for player in match_data['players']:
                    hero_id = player.get('hero_id')
                    purchase_log = player.get('purchase_log')
                    # Ensure we have both hero_id and purchase_log
                    if hero_id is not None and purchase_log is not None:
                        # Add match_id for context
                        for purchase in purchase_log:
                            purchase['match_id'] = match_id
                            purchase['hero_id'] = hero_id
                        all_purchase_data.extend(purchase_log)
                success = True # Mark as successful for this match_id
            else:
                print(f"Warning: 'players' key not found in response for match_id: {match_id}")
                success = True # Mark as success to avoid retrying if data is missing

        except requests.exceptions.Timeout:
            print(f"Error: Timeout fetching match {match_id}. Retrying after {RETRY_DELAY}s...")
            retries += 1
            time.sleep(RETRY_DELAY)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching match {match_id}: {e}. Retrying after {RETRY_DELAY}s...")
            retries += 1
            time.sleep(RETRY_DELAY)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for match {match_id}. Skipping match.")
            break # Stop retrying for this match if JSON is invalid
        except Exception as e:
            print(f"An unexpected error occurred for match {match_id}: {e}. Skipping match.")
            break # Stop retrying for this match on unexpected errors

    processed_count += 1
    if success:
        print(f"Processed match {processed_count}/{total_matches} (ID: {match_id}) - Success")
    else:
        print(f"Processed match {processed_count}/{total_matches} (ID: {match_id}) - Failed after {MAX_RETRIES} retries")

    # Delay before next request
    time.sleep(REQUEST_DELAY)

# Save all collected data to JSON
try:
    with open(output_json_file, 'w') as f:
        json.dump(all_purchase_data, f, indent=4)
    print(f"Successfully saved all purchase log data to {output_json_file}")
except IOError as e:
    print(f"Error writing purchase log data to {output_json_file}: {e}")
except Exception as e:
    print(f"An unexpected error occurred while saving data: {e}")

print(f"Finished processing {total_matches} matches.")

