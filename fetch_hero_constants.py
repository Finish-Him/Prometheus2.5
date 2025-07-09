import requests
import json
import sys

output_file = "/home/ubuntu/dota_hero_constants.json"
url = "https://api.opendota.com/api/constants/heroes"

print(f"Fetching hero constants from {url}...")
try:
    response = requests.get(url)
    response.raise_for_status() # Raise an exception for bad status codes
    hero_data = response.json()
    
    # Save the data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hero_data, f, indent=4)
        
    print(f"Hero constants successfully fetched and saved to {output_file}")

except requests.exceptions.RequestException as e:
    print(f"Error fetching hero constants: {e}")
    sys.exit(1)
except json.JSONDecodeError:
    print("Error decoding JSON response from OpenDota API.")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)

