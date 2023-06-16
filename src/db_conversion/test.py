import json
import import_database

with open("../gui/sightings.json") as f:
    fs = json.load(f)

for record in fs:
    record['date'] = import_database.convert_excel_date(record['date'])

with open("../gui/sightings.json", "w") as f:
    json.dump(fs, f, indent=4, separators=(',', ': '))