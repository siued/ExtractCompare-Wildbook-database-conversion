import json
import requests
import docker
import time

# this is a testing file where I run code which only needs to be run once or just tested once and does not need to be
# documented


url = "http://localhost:8080/api/annot/viewpoint"
res = requests.put(url, json={'aid_list': [10], 'viewpoint_list': ['unknown']})
print(res.json())