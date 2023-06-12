import json
import requests
import docker
import time
import gui
# this is a testing file where I run code which only needs to be run once or just tested once and does not need to be
# documented

with open("../db_conversion/matching_results.json") as f:
    matches = json.load(f)

matched_aids = []
for match in matches:
    if match['score_list'] and max(match['score_list']) > 0.5:
        index = match['score_list'].index(max(match['score_list']))
        matched_aids.append((match['qaid'], match['daid_list'][index], match['score_list'][index]))

print(matched_aids)

# the first two matches are correct