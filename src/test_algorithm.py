# load the field database,  assume the names are labelled correctly

import json
import requests

with open("fielddb.json") as f:
    fdb = json.load(f)

# get a list of aid-name pairs
aid_name_list = [(aid, record['ID']) for record in fdb for aid in record['aids'] if len(record['aids']) == 1]
name_dict = dict(aid_name_list)

aid_list = [aid for aid, name in aid_name_list]

res = requests.get("http://localhost:8081/api/query/chip/dict/simple", json={'daid_list': aid_list, 'qaid_list': aid_list, 'cfgdict': {'sv_on': False, 'fg_on': False}})
matches = res.json()['response']

match_aid_list = []
empty_match_count = 0
for match in matches:
    qaid = match['qaid']
    match_list = match['daid_list']
    if not match_list:
        empty_match_count += 1
        continue
    score_list = match['score_list']
    best_match_index = score_list.index(max(score_list))
    match_aid_list.append((qaid, match_list[best_match_index]))

# find how many names match from the match_aid_list
name_match_count = 0
for aid, aid2 in match_aid_list:
    if name_dict[aid] == name_dict[aid2] and aid != aid2:
        name_match_count += 1

print('empty match count: ' + str(empty_match_count))
print('name match count: ' + str(name_match_count) + ' out of ' + str(len(match_aid_list)) + ' matches')

# no args: 892 empty, 375/598 name matches
# proot=smk: 3 empty, 242/1487 name matches - takes longer (did not measure)
# sv_on=True, fg_on=True: was  cached, clearly  those are the default
# sv_on=False, fg_on=False:
