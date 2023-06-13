import json

with open("matching_results2.json") as f:
    matches = json.load(f)

count = 0
for match in matches:
    if match['score_list'] and max(match['score_list']) > 0.1:
        count += 1

print(count)