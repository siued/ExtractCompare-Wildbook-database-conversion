import json
import requests
import docker
import time

from PyQt5.QtWidgets import QApplication

from confirm_match import ConfirmDialog
from wildbook_util import get_name_from_aid

# this is a testing file where I run code which only needs to be run once or just tested once and does not need to be
# documented

with open("../db_conversion/matching_results_reverse.json") as f:
    matches = json.load(f)

app = QApplication([])

matched_aids = []
for match in matches:
    if match['score_list'] and max(match['score_list']) > 0.5:
        index = match['score_list'].index(max(match['score_list']))
        print(get_name_from_aid(match['daid_list'][index], 'http://localhost:8081/'), get_name_from_aid(match['qaid'], 'http://localhost:8081/'), match['score_list'][index])
        matched_aids.append((match['qaid'], match['daid_list'][index], match['score_list'][index]))
        ConfirmDialog(match['qaid'], match['daid_list'][index], match['score_list'][index], 'http://localhost:8081/').exec_()

print(matched_aids)

# the first two matches are correct
