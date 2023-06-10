# Excel for Windows stores dates by default as the number of days (or fraction thereof) since 1899-12-31T00:00:00
import json

with open("../db_conversion/scdb2.json") as f:
    db = json.load(f)

from datetime import datetime, timedelta

for i, record in enumerate(db):

    date_value = record['dt']
    if date_value == "":
        formatted_date = 'unknown'
    else:
        base_date = datetime(1900, 1, 1)  # Excel's base date

        converted_date = base_date + timedelta(days=date_value)

        formatted_date = converted_date.strftime("%Y-%m-%d")  # Format the date as desired
    record['dt'] = formatted_date

with open("../db_conversion/scdb2.json", 'w') as f:
    json.dump(db, f, indent=4)