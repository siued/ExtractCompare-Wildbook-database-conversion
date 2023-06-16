from datetime import datetime, timedelta
import json

with open("../db_conversion/fielddb2.json") as f:
    db = json.load(f)

count = 0
for record in db:
    date_value = record['sighting_info']['date']
    base_date = datetime(1900, 1, 1)  # Excel's base date

    converted_date = base_date + timedelta(days=date_value)

    formatted_date = converted_date.strftime("%Y-%m-%d")  # Format the date as desired

    if formatted_date != record['dt']:
        count += 1

print(count)