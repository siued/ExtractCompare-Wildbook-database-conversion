import os
import requests
import xlrd

# number of images to process
N = 10

# TODO: let user input the wildbook port number
port = str(8080)

# TODO: make this user inputtable
db_pic_folder = 'C:/Users/Matej/Desktop/Seal-Pattern-Recognition/Field_db/seal_demo/newpic'

# terminology:
# gid - id of an uploaded picture
# annotation - a section of an image with a seal in it
# aid - id of an annotation in a picture  (one-to-many relationship with gid)
# uuid - unique id of any object in the database (ex. annotation, picture, graph, job, etc.)
# imageset - set of images (obv)
# detect: request for animal detection in an image (find annotation in image)
# query: request for the matching engine (identify matching annotations)
# chip: TODO

def get_pic(db, n):
    path = db['photo'][n]
    pic = open(str(os.path.join(db_pic_folder, path)) + '.jpg', 'rb').read()
    return pic


# TODO: make this user inputtable
excel_exported_db = 'C:/Users/Matej/Desktop/Seal-Pattern-Recognition/fielddb_export.xls'

workbook = xlrd.open_workbook(excel_exported_db)
worksheet = workbook.sheet_by_index(0)
#  convert to dictionary of columns
db = {}
for i in range(1, worksheet.ncols):
    db[worksheet.cell_value(0, i)] = []
    for j in range(1, worksheet.nrows):
        db[worksheet.cell_value(0, i)].append(worksheet.cell_value(j, i))

pic_list = [get_pic(db, i) for i in range(N)]


def upload_pics(pic_list):
    url = "http://localhost:8080/api/upload/image"
    gid_list = []
    pic_gid_list = []

    for i in range(N):
        files = {'image': pic_list[i], 'name': 'test.jpg'}
        res = requests.post(url, files=files)
        assert res.json()['status']['success']
        gid_list.append(res.json()['response'])
        pic_gid_list.append({'gid': res.json()['response'], 'pic_index': i})
    return gid_list


# TODO: add date and other picture metadata


# upload pictures to database
gid_list = upload_pics(pic_list)
print('gids: ', gid_list)


def get_uuids(gid_list):
    url = "http://localhost:8080/api/image/uuid"
    res = requests.get(url, json={'gid_list': gid_list})
    assert res.json()['status']['success']
    return res.json()['response']


# get uuid identifiers for the uploaded pictures
# uuid_list = [get_uuids(gid_list)[i]['__UUID__'] for i in range(N)]
# print('uuids: ', uuid_list)


# TODO: check if all seals get detected, otherwise maybe detect manually?
def detect_seals(gid_list):
    url = "http://localhost:8080/api/detect/cnn/yolo"
    res = requests.put(url, json={'gid_list': gid_list})
    assert res.json()['status']['success']
    return res.json()['response']


# detect seals in the uploaded pictures, get annotation ids of each seal detected
aid_list = detect_seals(gid_list)
aid_list_flattened = [item for sublist in aid_list for item in sublist]
print('aids: ', aid_list_flattened)


def set_data_for_annots():
    # set all annots as annot of interest
    url = "http://localhost:8080/api/annot/interest"
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'flag_list': [1] * len(aid_list_flattened)})
    assert res.json()['status']['success']
    print('set all annots as annot of interest')

    # set all annots as exemplars
    url = "http://localhost:8080/api/annot/exemplar"
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'flag_list': [1] * len(aid_list_flattened)})
    assert res.json()['status']['success']
    print('set all annots as exemplars')

    # set names for all annots
    url = "http://localhost:8080/api/annot/name"
    name_list = []
    for i in range(len(gid_list)):
        if len(aid_list[i]) == 0:
            continue
        elif len(aid_list[i]) == 1:
            name_list.append(db['ID'][i])
        else:
            # more than one seal detected in the picture, unsure which one the original db is referring to
            name_list.append(['unknown'] * len(aid_list[i]))
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'name_list': name_list})
    assert res.json()['status']['success']
    print('set names for all annots')

    # add comments
    url = "http://localhost:8080/api/annot/note"
    note_list = []
    for i in range(len(gid_list)):
        if len(aid_list[i]) == 0:
            continue
        elif len(aid_list[i]) == 1:
            note_list.append(db['comments'][i] + ', tagged: %s' % 'yes' if db['tagged'][i] == 1 else 'no')
        else:
            # more than one seal detected in the picture, unsure which one the original db is referring to
            note_list.append(['unknown'] * len(aid_list[i]))
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'notes_list': note_list})
    assert res.json()['status']['success']
    print('added comments')

    # set species
    url = "http://localhost:8080/api/annot/species"
    res = requests.put(url, json={'aid_list': aid_list_flattened,
                                  'species_text_list': ['harbour_seal'] * len(aid_list_flattened)})
    assert res.json()['status']['success']
    print('set species')

    # set gender for all annots
    url = "http://localhost:8080/api/annot/sex"
    gender_list = []
    for i in range(len(gid_list)):
        if len(aid_list[i]) == 0:
            continue
        elif len(aid_list[i]) == 1:
            gender_list.append(db['gender'][i])
        else:
            # more than one seal detected in the picture, unsure which one the original db is referring to
            gender_list.append(['unknown'] * len(aid_list[i]))
    # 0: female, 1: male, 2: unknown
    for i in range(len(gender_list)):
        genders = {'female': 0, 'male': 1, 'unknown': 2}
        gender_list[i] = genders[gender_list[i]]
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'name_sex_list': gender_list})
    assert res.json()['status']['success']
    print('set gender for all annots')

    # set quality as good
    # quality enum is 1: junk until 5: excellent
    url = "http://localhost:8080/api/annot/quality"
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'annot_quality_list': [5] * len(aid_list_flattened)})
    assert res.json()['status']['success']
    print('set quality as excellent')

    # set ages
    # assuming that pup: 0-3y, juvenile: 3-5y, adult: 5-30y
    age_min_dict = {'pup': 0, 'juv': 36, 'adult': 60, 'Unknown': -1}
    age_min_list = []
    age_max_dict = {'pup': 36, 'juv': 60, 'adult': 360, 'Unknown': -1}
    age_max_list = []
    for i in range(len(gid_list)):
        if len(aid_list[i]) == 0:
            continue
        elif len(aid_list[i]) == 1:
            age_min_list.append(age_min_dict[db['age'][i]])
            age_max_list.append(age_max_dict[db['age'][i]])
        else:
            # more than one seal detected in the picture, unsure which one the original db is referring to
            age_min_list.append([-1] * len(aid_list[i]))
            age_max_list.append([-1] * len(aid_list[i]))
    url = "http://localhost:8080/api/annot/age/months/min"
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'annot_age_months_est_min_list': age_min_list})
    assert res.json()['status']['success']
    url = "http://localhost:8080/api/annot/age/months/max"
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'annot_age_months_est_max_list': age_max_list})
    assert res.json()['status']['success']
    print('set ages')

    # set viewpoint
    url = "http://localhost:8080/api/annot/viewpoint"
    viewpoint_dict = {'L': 'left', 'R': 'right', 'M': 'bottom', '': 'unspecified'}
    viewpoint_list = []
    for i in range (len(gid_list)):
        viewpoint = viewpoint_dict[db['side'][i]]
        if len(aid_list[i]) == 0:
            continue
        elif len(aid_list[i]) == 1:
            viewpoint_list.append(viewpoint)
        else:
            # more than one seal detected in the picture, unsure which one the original db is referring to
            viewpoint_list.append(['unknown'] * len(aid_list[i]))
    res = requests.put(url, json={'aid_list': aid_list_flattened, 'viewpoint_list': viewpoint_list})
    assert res.json()['status']['success']
    print('set viewpoints')


set_data_for_annots()


def match_annots():
    # testing for now
    aid_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    url = "http://localhost:8080/api/query/chip/dict/simple"
    res = requests.get(url, json={'qaid_list': aid_list, 'daid_list': aid_list})
    response = res.json()['response']
    for i in range(len(response)):
        qaid = response[i]['qaid']
        match_list =  response[i]['daid_list']
        score_list = response[i]['score_list']
        best_match_index = score_list.index(max(score_list))
        print('qaid: ' + str(qaid) + ', best match: ' + str(match_list[best_match_index]) + ', score: ' + str(max(score_list)))

    # THIS WORKS \/
    # url = "http://localhost:8080/api/query/graph/complete"
    # res = requests.get(url, json={'aid_list': [1, 2, 3, 4, 5, 6, 7, 8, 9]})
    # print(res.json())


match_annots()

# api/query/chip to compare list vs db_list, use chip/dict/simple, because chip and chip/dict throw internal errors (unrelated to the matching process, caused by returning incorrect values)
# /api/query/graph/complete/ to compare everything against everything, returns a graph with weights per uuid pair - a way to use query/chip indirectly, but compares all to all, pass arg k to get more/less than 5 best matches per annot
# /api/review/query/chip/best/ tries to match an annot against everything, then shows the best match for review - useful for adding new images, doesnt give score, only gives uuid of best match and name etc
# NOUSE /api/review/query/graph/ for reviewing graph in html, needs a cm_list so can't be used due to query/chip not working
# NOUSE /api/query/graph/v2/ needs a graph_uuid returns a match_list (POST makes a graph, GET returns the match_list) - match list is all null/unspecified
# NOUSE api/review/identification/graph?graph_uuid=... when reviewing things through browser


