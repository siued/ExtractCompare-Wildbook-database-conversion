import json
import requests
import docker
import time

# this is a testing file where I run code which only needs to be run once or just tested once and does not need to be
# documented

res = requests.get('http://localhost:8081/api/test')
print(res.json())
