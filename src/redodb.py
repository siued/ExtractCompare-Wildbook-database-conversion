import json
import requests
import docker
import time

# TODO rename
# this is a one-time fix to force the database to preprocess images for matching, which speeds things up and avoids crashes

client = docker.from_env()
container = client.containers.get('test-db-load-wbia')

with open("scdb.json") as f:
    scdb = json.load(f)

with open("fielddb.json") as f:
    fdb = json.load(f)

sc_aid_list = [aid for record in scdb for aid in record['aids']]
f_aid_list = [aid for record in fdb for aid in record['aids']]


def match_annots(idx):
    url = "http://localhost:8081/api/query/chip/dict/simple"
    res = requests.get(url, json={'qaid_list': sc_aid_list[0:1], 'daid_list': f_aid_list[idx:idx+50], 'verbose': False})
    # print(res.json())
    response = res.json()['response']
    for i in range(len(response)):
        qaid = response[i]['qaid']
        match_list = response[i]['daid_list']
        score_list = response[i]['score_list']
        best_match_index = score_list.index(max(score_list))
        print('qaid: ' + str(qaid) + ', best match: ' + str(match_list[best_match_index]) + ', score: ' + str(
            max(score_list)))


i = 0
while i < len(f_aid_list):
    try:
        match_annots(i)
        i += 50
    except Exception as e:
        print(e)
        print('crashed, restarting')
        container.start()
        time.sleep(30)
