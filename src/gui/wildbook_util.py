import json

import requests


def get_uuids(gid_list, server_url):
    url = f"{server_url}/api/image/uuid"
    res = requests.get(url, json={'gid_list': gid_list})
    assert res.status_code == 200
    uuid_list = [uuid['__UUID__'] for uuid in res.json()['response']]
    return uuid_list


def get_comment(aid, server_url):
    url = f"{server_url}/api/annot/note"
    res = requests.get(url, json={'aid_list': [aid]})
    assert res.status_code == 200
    return res.json()['response'][0]


def rename_seal(old_name, new_name, server_url):
    gids, nid = get_gids_by_name(server_url, old_name)
    aids = get_aid_list_from_gids(server_url, gids)
    aids_to_rename = []
    for aid in aids:
        url = f"{server_url}/api/annot/name/text"
        res = requests.get(url, json={'aid_list': [aid]})
        assert res.status_code == 200
        name = res.json()['response'][0]
        if name == old_name:
            aids_to_rename.append(aid)

    url = f"{server_url}/api/annot/name"
    res = requests.put(url, json={'aid_list': aids_to_rename, 'name_list': [new_name] * len(aids_to_rename)})
    assert res.status_code == 200

    with open('sightings.json') as f:
        sightings = json.load(f)

    for sighting in sightings:
        if sighting['id'] == old_name:
            sighting['id'] = new_name

    with open('sightings.json', 'w') as f:
        json.dump(sightings, f, indent=4, separators=(',', ': '))


# returns gid_list, nid
def get_gids_by_name(server_url, name):
    url = f"{server_url}/api/name/dict"
    res = requests.get(url)
    assert res.status_code == 200
    name_dict = res.json()["response"]
    if name not in name_dict:
        return [], None
    nid = name_dict[name][0]
    gid_list = name_dict[name][1]
    return gid_list, nid


def get_name_from_aid(aid, server_url):
    url = f"{server_url}/api/annot/name/text"
    res = requests.get(url, json={'aid_list': [aid]})
    assert res.status_code == 200
    return res.json()['response'][0]


def get_aid_list_from_gids(server_url, gid_list):
    url = f"{server_url}/api/image/annot/rowid"
    res = requests.get(url, json={"gid_list": gid_list})
    assert res.status_code == 200
    aid_list = [aid for aids in res.json()["response"] for aid in aids]
    return aid_list


# returns sightings sorted by date, newest first
def get_sightings_from_name(name, server_url):
    gid_list, nid = get_gids_by_name(server_url, name)

    sighting_list = []

    if gid_list:
        aid_list = get_aid_list_from_gids(server_url, gid_list)

        url = f"{server_url}/api/annot/name/rowid"
        res = requests.get(url, json={"aid_list": aid_list})
        assert res.status_code == 200
        nid_list = res.json()["response"]

        url = f"{server_url}/api/annot/note"
        res = requests.get(url, json={"aid_list": aid_list})
        assert res.status_code == 200
        note_list = res.json()["response"]

        for sighting_nid, note in zip(nid_list, note_list):
            if sighting_nid == nid:
                note = json.loads(note)
                sighting_list.append({"date": note["date"], "location": note["location"], "comments": note["comments"], "with_photo": 'Yes', "with_pup": note["with_pup"], 'name': note['id'], 'age': note['age']})

    with open('sightings.json') as f:
        sightings = json.load(f)

    for sighting in sightings:
        if sighting["orig_ID"] == name or sighting["id"] == name:
            sighting_list.append({"date": sighting["date"], "location": sighting["location"], "comments": sighting["comments"], "with_photo": 'No', "with_pup": sighting["with_pup"], 'name': sighting['id'], 'age': sighting['age']})

    sighting_list.sort(key=lambda x: x["date"], reverse=True)

    return sighting_list


# merge two names, keep the non-numeric one or the oldest one in case both are non-numeric
# returns old_name, new_name
def merge_names(aid1, aid2, server_url):
    name1 = get_name_from_aid(aid1, server_url)
    name2 = get_name_from_aid(aid2, server_url)

    if name1 == name2:
        return None, None

    if not any(char.isalpha() for char in name1):
        new_name = name2
        old_name = name1
    elif not any(char.isalpha() for char in name2):
        new_name = name1
        old_name = name2
    else:
        sightings1 = get_sightings_from_name(name1, server_url)
        sightings2 = get_sightings_from_name(name2, server_url)

        oldest_sighting1 = sightings1[-1]
        oldest_sighting2 = sightings2[-1]

        if oldest_sighting1["date"] < oldest_sighting2["date"]:
            new_name = name1
            old_name = name2
        else:
            new_name = name2
            old_name = name1

    rename_seal(old_name, new_name, server_url)
    return old_name, new_name


# returns dict {name, gender, age: {min, max}}
def fetchSealDetails(aid, server_url):
    seal_details = {}

    url = f"{server_url}/api/annot/sex"
    res = requests.get(url, json={'aid_list': [aid]})
    assert res.status_code == 200
    gender = res.json()['response'][0]
    seal_details['gender'] = 'female' if gender == 0 else 'male' if gender == 1 else 'unknown'

    url = f"{server_url}/api/annot/age/months/min"
    res = requests.get(url, json={'aid_list': [aid]})
    assert res.status_code == 200
    seal_details['age'] = {'min': res.json()['response'][0]}

    url = f"{server_url}/api/annot/age/months/max"
    res = requests.get(url, json={'aid_list': [aid]})
    assert res.status_code == 200
    seal_details['age']['max'] = res.json()['response'][0]

    url = f"{server_url}/api/annot/name/text"
    res = requests.get(url, json={'aid_list': [aid]})
    assert res.status_code == 200
    seal_details['name'] = res.json()['response'][0]

    return seal_details


# takes dict {name, comments, age, viewpoint, gender}
def uploadSealDetails(form_values, aid, server_url):
    # Process the seal details and send them to the server using the API endpoint /api/annot/<id>
    # For example:
    print(f"Processing seal details: {form_values}")

    url = f"{server_url}/api/annot/interest"
    res = requests.put(url, json={'aid_list': [aid], 'flag_list': [1]})
    assert res.status_code == 200

    # set all annots as exemplars
    url = f"{server_url}/api/annot/exemplar"
    res = requests.put(url, json={'aid_list': [aid], 'flag_list': [1]})
    assert res.status_code == 200

    # set names for all annots
    url = f"{server_url}/api/annot/name"
    res = requests.put(url, json={'aid_list': [aid], 'name_list': [form_values['name']]})
    assert res.status_code == 200

    # add comments
    comment = form_values['comments']
    if comment != '':
        url = f"{server_url}/api/annot/note"
        res = requests.put(url, json={'aid_list': [aid], 'notes_list': [comment]})
        assert res.status_code == 200

    # set species
    url = f"{server_url}/api/annot/species"
    res = requests.put(url, json={'aid_list': [aid], 'species_text_list': ['harbour_seal']})
    assert res.status_code == 200

    # set gender for all annots
    url = f"{server_url}/api/annot/sex"
    # enum: 0: female, 1: male, 2: unknown
    gender = 0 if form_values['gender'] == 'female' else 1 if form_values['gender'] == 'male' else 2
    res = requests.put(url, json={'aid_list': [aid], 'name_sex_list': [gender]})
    assert res.status_code == 200

    # set quality as good
    # enum: 1: junk until 5: excellent
    url = f"{server_url}/api/annot/quality"
    res = requests.put(url, json={'aid_list': [aid], 'annot_quality_list': [5]})
    assert res.status_code == 200

    # set ages in months
    # assuming that pup: 0-3y, juvenile: 3-5y, adult: 5-30y
    age_min_dict = {'pup': 0, 'juv': 36, 'adult': 60, 'unknown': -1, '': -1}
    age_max_dict = {'pup': 36, 'juv': 60, 'adult': 360, 'unknown': -1, '': -1}

    url = f"{server_url}/api/annot/age/months/min"
    age = age_min_dict[form_values['age']]
    res = requests.put(url, json={'aid_list': [aid], 'annot_age_months_est_min_list': [age]})
    assert res.status_code == 200

    url = f"{server_url}/api/annot/age/months/max"
    age = age_max_dict[form_values['age']]
    res = requests.put(url, json={'aid_list': [aid], 'annot_age_months_est_max_list': [age]})
    assert res.status_code == 200

    # set viewpoint
    url = f"{server_url}/api/annot/viewpoint"
    res = requests.put(url, json={'aid_list': [aid], 'viewpoint_list': [form_values['viewpoint']]})
    assert res.status_code == 200

    print('Successfully uploaded the details for annotation with ID: ' + str(aid) + ' to the database')