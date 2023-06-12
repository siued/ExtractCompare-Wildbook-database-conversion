# load the field database, assume the names are labelled correctly

import json
import requests

with open("../db_conversion/fielddb2.json") as f:
    fdb = json.load(f)

# get a list of aid-name pairs
aid_name_list = [(aid, record['ID']) for record in fdb for aid in record['aids'] if len(record['aids']) == 1]
name_dict = dict(aid_name_list)

aid_list = [aid for aid, name in aid_name_list]

res = requests.get("http://localhost:8081/api/query/chip/dict/simple", json={'daid_list': aid_list, 'qaid_list': aid_list})
matches = res.json()['response']

match_aid_list = []
match_score_list = []
empty_match_count = 0
for match in matches:
    qaid = match['qaid']
    match_list = match['daid_list']
    if not match_list:
        empty_match_count += 1
        continue
    score_list = match['score_list']
    best_match_index = score_list.index(max(score_list))
    score = score_list[best_match_index]
    match_aid_list.append((qaid, match_list[best_match_index]))
    match_score_list.append((qaid, match_list[best_match_index], name_dict[qaid], name_dict[match_list[best_match_index]], score))

with open('match_score_list_test_algo.json', 'w') as f:
    json.dump(match_score_list, f, indent=4, separators=(',', ': '))

# find how many names match from the match_aid_list
name_match_count = 0
for aid, aid2 in match_aid_list:
    if name_dict[aid] == name_dict[aid2] and aid != aid2:
        name_match_count += 1

print('empty match count: ' + str(empty_match_count))
print('name match count: ' + str(name_match_count) + ' out of ' + str(len(match_aid_list)) + ' matches')

# old testing:
# no args: 892 empty, 375/598 name matches
# proot=smk: 3 empty, 242/1487 name matches - takes longer (did not measure)
# sv_on=True, fg_on=True: was cached, clearly those are the default (so result same as no args)
# sv_on=False, fg_on=False:

# new testing:
# started 13:57
# 1300 empty, 431/792 matches, but only 196 of bad matches are > 0.5 score  - 165 are < 0.5
# so 1465 empty, 431/627

