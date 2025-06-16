import csv
import random
import time
import json
import os
from program_details import get_details

def get_urls_from_csv(filename):
    """
    Generator function to yield each URL from the CSV file one by one.
    
    :param filename: The name of the CSV file containing the URLs.
    :yield: Each URL from the CSV file.
    """
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row ("URL")
        for row in reader:
            if row:  # Ensure the row is not empty
                yield row[0]

# Check if programmes.json exists and load existing data
if os.path.exists('programme_details.json'):
    with open('programme_details.json', 'r') as json_file:
        program_details_list = json.load(json_file)
else:
    program_details_list = []

urls = 'Business&Management_accounting_urls.csv'
# Process URLs from the CSV file
for url in get_urls_from_csv(urls):
    time.sleep(random.uniform(20, 30))  # Delay to avoid rate limiting
    
    try:
        discipline = "Business & Management"
        sub_discipline = "Accounting"
        details = get_details(url, discipline, sub_discipline)
        if details:  # Check if details were successfully retrieved
            program_details_list.append(details)
            print(f"Successfully retrieved details for URL: {url}")
        else:
            print(f"No details returned for URL: {url}")
    except Exception as e:
        print(f"Error processing URL {url}: {e}")

    
   

# Save the updated list back to programmes.json
with open('programme_details.json', 'w') as json_file:
    json.dump(program_details_list, json_file, indent=4)

print(f"Saved {len(program_details_list)} programs to programme_details.json")