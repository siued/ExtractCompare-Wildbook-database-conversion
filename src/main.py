import os
import requests
import xlrd
import json

from PyQt5.QtWidgets import QFileDialog

import util

# terminology:
# gid - id of an uploaded picture
# annotation - a section of an image with an object of interest in it
# aid - id of an annotation in a picture  (many-to-one relationship with gid)
# uuid - unique id of any object in the database (ex. annotation, picture, graph, job, etc.)
# imageset - set of images (obv)
# detect: request for animal detection in an image (find annotation in image)
# query: request for the matching engine (identify matching annotations)

# TODO: if __main__
# TODO: let user input the wildbook port number
port = str(8081)
base_url = "http://localhost:" + port + "/"

# TODO: make this user inputtable
db_pic_folder = 'C:/Users/Matej/Desktop/Seal-Pattern-Recognition/Field_db/seal_demo/newpic'

# see if the database was already converted to json, use the Excel export if it hasn't
if not os.path.exists('db.json'):
    # TODO: make this user inputtable
    excel_exported_db = 'C:/Users/Matej/Desktop/Seal-Pattern-Recognition/fielddb_export.xls'

    workbook = xlrd.open_workbook(excel_exported_db)
    worksheet = workbook.sheet_by_index(0)

    # convert to list of dictionaries, each dict holds info about one seal (one line from the Excel file)
    db = []
    for j in range(1, worksheet.nrows):
        seal_info = {}
        for i in range(0, worksheet.ncols):
            col_name = worksheet.cell_value(0, i)
            seal_info[col_name] = worksheet.cell_value(j, i)
        db.append(seal_info)
else:
    with open('db.json') as f:
        db = json.load(f)

db = util.fix_unmatched_genders(db)

# get locations of all pictures in the database
for record in db:
    if 'photo_location' not in record:
        try:
            record['photo_location'] = str(os.path.join(db_pic_folder, record['photo'])) + '.jpg'
        except FileNotFoundError:
            # remove records with missing images
            db.remove(record)

# save the database in a json file for easier loading
with open('C:/Users/Matej/Desktop/Seal-Pattern-Recognition/src/db.json', 'w') as f:
    json.dump(db, f, indent=4, separators=(',', ': '))

print('found %s records' % len(db))
print('starting the upload, this might take a while depending on the number of photos you\'re uploading...')


def upload_pics():
    url = base_url + "api/upload/image"

    for record in db:
        # don't re-upload pictures that are already in the database
        if 'gid' in record:
            continue
        # there's no way to keep the image name, it'll be called upload_<timestamp>.jpg in the database
        files = {'image': open(record['photo_location'], 'rb').read()}
        res = requests.post(url, files=files)
        assert res.json()['status']['success']
        record['gid'] = res.json()['response']
        # save progress every 50 uploads
        if db.index(record) % 50 == 0:
            print('uploaded picture %s, saved progress' % i)
            # overwrite previous save
            with open('C:/Users/Matej/Desktop/Seal-Pattern-Recognition/src/db.json', 'w') as f:
                json.dump(db, f, indent=4, separators=(',', ': '))
    return


# TODO: add date and other picture metadata
# TODO: put pictures into imagesets


# upload pictures to database
upload_pics()
gid_list = [record['gid'] for record in db]

# remove duplicate gids
gid_list = list(set(gid_list))

print('uploaded %s pictures' % len(gid_list))
print('if this is less than the number of records, that means there were multiple records with the same picture, '
      'this is normal because ExtractCompare keeps multiple records if one picture  contains multiple aspects of a '
      'seal (ex. flank and neck)')

# save the final state
with open('db.json', 'w') as f:
    json.dump(db, f, indent=4, separators=(',', ': '))


# get uuid identifiers for the uploaded pictures, can be enabled if needed
def get_uuids(gid_list):
    url = base_url + "api/image/uuid"
    res = requests.get(url, json={'gid_list': gid_list})
    assert res.json()['status']['success']
    return res.json()['response']


# uuid_list = [get_uuids(gid_list)[i]['__UUID__'] for i in range(N)]
# print('uuids: ', uuid_list)


def detect_seals(gid_list):
    # use either lightnet or yolo in the url for different detection NN
    url = base_url + "api/detect/cnn/yolo"
    res = requests.put(url, json={'gid_list': gid_list})
    assert res.json()['status']['success']
    return res.json()['response']


# detect seals in the uploaded pictures, get annotation ids of each seal detected
detect_list = [record['gid'] for record in db if 'aids' not in record]
if len(detect_list) > 0:
    print('detecting seals in %s pictures, this might take a while' % len(detect_list))
    aid_list = detect_seals(detect_list)
    # add the annotation ids to the json database save
    zipped_list = list(zip(detect_list, aid_list))
    for gid, aids in zipped_list:
        for record in db:
            if record['gid'] == gid:
                record['aids'] = aids

# convert list of lists to a regular list
aid_list_flattened = [aid for record in db for aid in record['aids']]
print('found %s annotations' % len(aid_list_flattened))
print('this can be more than the number of uploaded pictures because some pictures have more than one seal in them')


def set_data_for_annots():
    # set all annots as annot of interest
    url = base_url + "/api/annot/interest"
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'flag_list': [1] * len(aid_list_flattened)})
    assert res.json()['status']['success']
    print('set all annots as annot of interest')

    # set all annots as exemplars
    url = base_url + "api/annot/exemplar"
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'flag_list': [1] * len(aid_list_flattened)})
    assert res.json()['status']['success']
    print('set all annots as exemplars')

    # set names for all annots
    url = base_url + "api/annot/name"
    name_list = []
    for record in db:
        if len(record['aids']) == 0:
            continue
        elif len(record['aids']) == 1:
            name_list.append(record['ID'])
        else:
            # more than one seal detected in the picture, unsure which one the original db is referring to
            name_list += ['unknown_' + record['ID']] * len(record['aids'])
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'name_list': name_list})
    assert res.json()['status']['success']
    print('set names for all annots')

    # add comments, append whether the seal is tagged or not to the end of each comment
    url = base_url + "api/annot/note"
    note_list = []
    for record in db:
        if len(record['aids']) == 0:
            continue
        elif len(record['aids']) == 1:
            note_list.append(record['comments'] + ', tagged: %s' % 'yes' if record['tagged'] == 1 else 'no')
        else:
            # more than one seal detected in the picture, unsure which one the original db is referring to
            note_list += ['unknown'] * len(record['aids'])
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'notes_list': note_list})
    assert res.json()['status']['success']
    print('added comments')

    # set species
    url = base_url + "api/annot/species"
    res = requests.put(url, json={'aid_list': aid_list_flattened,
                                  'species_text_list': ['harbour_seal'] * len(aid_list_flattened)})
    assert res.json()['status']['success']
    print('set species')

    # set gender for all annots
    url = base_url + "api/annot/sex"
    gender_list = []
    for record in db:
        if len(record['aids']) == 0:
            continue
        elif len(record['aids']) == 1:
            gender_list.append(record['gender'])
        else:
            # more than one seal detected in the picture, unsure which one the original db is referring to
            gender_list += ['unknown'] * len(record['aids'])
    # enum: 0: female, 1: male, 2: unknown
    for i in range(len(gender_list)):
        genders = {'female': 0, 'male': 1, 'unknown': 2, '': 2}
        gender_list[i] = genders[gender_list[i]]
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'name_sex_list': gender_list})
    assert res.json()['status']['success']
    print('set gender for all annots')

    # set quality as good
    # enum: 1: junk until 5: excellent
    url = base_url + "api/annot/quality"
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'annot_quality_list': [5] * len(aid_list_flattened)})
    assert res.json()['status']['success']
    print('set quality as excellent')

    # set ages in months
    # assuming that pup: 0-3y, juvenile: 3-5y, adult: 5-30y
    age_min_dict = {'pup': 0, 'juv': 36, 'adult': 60, 'Unknown': -1}
    age_min_list = []
    age_max_dict = {'pup': 36, 'juv': 60, 'adult': 360, 'Unknown': -1}
    age_max_list = []
    for record in db:
        if len(record['aids']) == 0:
            continue
        elif len(record['aids']) == 1:
            age_min_list.append(age_min_dict[record['age']])
            age_max_list.append(age_max_dict[record['age']])
        else:
            # more than one seal detected in the picture, unsure which one the original db is referring to
            age_min_list += [-1] * len(record['aids'])
            age_max_list += [-1] * len(record['aids'])

    url = base_url + "api/annot/age/months/min"
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'annot_age_months_est_min_list': age_min_list})
    assert res.json()['status']['success']

    url = base_url + "api/annot/age/months/max"
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'annot_age_months_est_max_list': age_max_list})
    assert res.json()['status']['success']
    print('set ages')

    # set viewpoint
    url = base_url + "api/annot/viewpoint"
    viewpoint_dict = {'L': 'left', 'R': 'right', 'M': 'bottom', '': 'unspecified'}
    viewpoint_list = []
    for record in db:
        viewpoint = viewpoint_dict[record['side']]
        if len(record['aids']) == 0:
            continue
        elif len(record['aids']) == 1:
            viewpoint_list.append(viewpoint)
        else:
            # more than one seal detected in the picture, unsure which one the original db is referring to
            viewpoint_list += ['unknown'] * len(record['aids'])
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'viewpoint_list': viewpoint_list})
    assert res.json()['status']['success']
    print('set viewpoints')


set_data_for_annots()


def match_annots():
    #TODO get aid lists of field and sealcentre dbs
    url = base_url + "api/query/chip/dict/simple"
    res = requests.get(url, json={'qaid_list': aid_list, 'daid_list': aid_list})
    response = res.json()['response']
    for i in range(len(response)):
        qaid = response[i]['qaid']
        match_list = response[i]['daid_list']
        score_list = response[i]['score_list']
        best_match_index = score_list.index(max(score_list))
        print('qaid: ' + str(qaid) + ', best match: ' + str(match_list[best_match_index]) + ', score: ' + str(
            max(score_list)))


# match_annots()

# api/query/chip to compare list vs db_list, use chip/dict/simple, because chip and chip/dict throw internal errors (unrelated to the matching process, caused by returning incorrect values)
# /api/query/graph/complete/ to compare everything against everything, returns a graph with weights per uuid pair - a way to use query/chip indirectly, but compares all to all, pass arg k to get more/less than 5 best matches per annot
# /api/review/query/chip/best/ tries to match an annot against everything, then shows the best match for review - useful for adding new images, doesnt give score, only gives uuid of best match and name etc
# NOUSE /api/review/query/graph/ for reviewing graph in html, needs a cm_list so can't be used due to query/chip not working
# NOUSE /api/query/graph/v2/ needs a graph_uuid returns a match_list (POST makes a graph, GET returns the match_list) - match list is all null/unspecified
# NOUSE api/review/identification/graph?graph_uuid=... when reviewing things through browser
