import os
from tkinter import Tk, simpledialog
from tkinter.filedialog import askdirectory, askopenfilename

import requests
import xlrd
import json

# terminology:
# gid - id of an uploaded picture
# annotation - a section of an image with an object of interest in it
# aid - id of an annotation in a picture  (many-to-one relationship with gid)
# uuid - unique id of any object in the database (ex. annotation, picture, graph, job, etc.)
# imageset - set of images (obv)
# detect: request for animal detection in an image (find annotation in image)
# query: request for the matching engine (identify matching annotations)

def select_folder(title):
    Tk().withdraw()  # Hide the main window
    folder_path = askdirectory(title=title)
    return folder_path

def get_text_input(title, textfield):
    Tk().withdraw()  # Hide the main window
    text_input = simpledialog.askstring(textfield, title)
    return text_input

def select_file(title):
    Tk().withdraw()  # Hide the main window
    file_path = askopenfilename(title=title)
    return file_path


def main():
    # This program takes an Excel file of an ExtractCompare database and uploads it to a Wildbook server.
    # The process might take several hours, depending on the size of the database and the computing power of the server.

    default_port = str(8081)

    port = get_text_input(f'Enter the port number of the Wildbook server, leave blank for default port {default_port}',
                          'Port number')
    if port is None:
        exit()
    if port == '':
        port = default_port

    base_url = "http://localhost:" + port + "/"

    name = get_text_input('Enter the name of the database. This will be the name of the json file used to save progress',
                          'Database name')
    if name is None:
        exit()
    save_file = f'{name}.json'

    db_pic_folder = select_folder('Select the folder with the pictures of the database, will look something like '
                                  '/seal_demo/newpic')
    if db_pic_folder is None:
        exit()

    # see if the database was already converted to json, use the Excel export if it hasn't
    if not os.path.exists(save_file):
        excel_exported_db = select_file('Select the Excel file of the database')
        if excel_exported_db is None:
            exit()

        workbook = xlrd.open_workbook(excel_exported_db)
        worksheet = workbook.sheet_by_index(0)

        # convert to list of records, each record holds info about one seal (one line from the Excel file)
        json_save = []
        for j in range(1, worksheet.nrows):
            seal_info = {}
            for i in range(0, worksheet.ncols):
                col_name = worksheet.cell_value(0, i)
                seal_info[col_name] = worksheet.cell_value(j, i)
            json_save.append(seal_info)
    else:
        print('loading database from %s' % save_file)
        with open(save_file) as f:
            json_save = json.load(f)

    # set duplicate names' genders to be the same (only if one of them is unknown, not if one name is marked as male vs
    # female)
    def fix_unmatched_genders(json_save):
        names = [record['ID'] for record in json_save]
        genders = [record['gender'] for record in json_save]
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                if names[j] == names[i] and genders[i] != genders[j]:
                    unk = i if genders[i] == 'unknown' else j
                    k = j if unk == i else i
                    json_save[unk]['gender'] = json_save[k]['gender']

        return json_save

    json_save = fix_unmatched_genders(json_save)

    db2 = []
    # get locations of all pictures in the database
    for record in json_save:
        if 'photo_location' not in record:
            loc = str(os.path.join(db_pic_folder, record['photo'])) + '.jpg'
            if os.path.exists(loc):
                record['photo_location'] = loc
                db2.append(record)
        else:
            db2.append(record)

    json_save = db2

    # save the database in a json file for easier loading
    with open(save_file, 'w') as f:
        json.dump(json_save, f, indent=4, separators=(',', ': '))

    print('found %s records' % len(json_save))
    print('starting the upload, this might take a while depending on the number of photos you\'re uploading...')

    def upload_pics():
        url = base_url + "api/upload/image"

        print('uploading pictures to the database...')

        for record in json_save:
            # don't re-upload pictures that are already in the database
            if 'gid' in record:
                continue
            # there's no way to keep the image name, it'll be called upload_<timestamp>.jpg in the database
            try:
                files = {'image': open(record['photo_location'], 'rb').read()}
            except FileNotFoundError:
                print('removing record %s because the picture is missing' % record['ID'])
                json_save.remove(record)
                continue
            res = requests.post(url, files=files)
            assert res.json()['status']['success']
            record['gid'] = res.json()['response']
            # save progress every 50 uploads
            if json_save.index(record) % 50 == 0:
                print('uploaded picture %s, saved progress' % json_save.index(record))
                # overwrite previous save
                with open(save_file, 'w') as f:
                    json.dump(json_save, f, indent=4, separators=(',', ': '))
        return

    with open(save_file, 'w') as f:
        json.dump(json_save, f, indent=4, separators=(',', ': '))

    # upload pictures to database
    upload_pics()

    gid_list = [record['gid'] for record in json_save]

    # remove records referring to the same picture
    for record in json_save:
        if gid_list.count(record['gid']) > 1:
            # there is no need to check the info, if the records refer to the same picture they match
            json_save.remove(record)
            gid_list.remove(record['gid'])

    print('uploaded %s pictures' % len(gid_list))
    print('if this is less than the number of records, that means there were multiple records with the same picture, '
          'this is normal because ExtractCompare keeps multiple records if one picture contains multiple aspects of a '
          'seal (ex. flank and neck). Also, some records may have been removed because the picture wasn\'t found')

    # save the final state
    with open(save_file, 'w') as f:
        json.dump(json_save, f, indent=4, separators=(',', ': '))

    # get uuid identifiers for the uploaded pictures, can be enabled if needed
    def get_uuids(gid_list):
        url = "http://localhost:8081/api/image/uuid"
        res = requests.get(url, json={'gid_list': gid_list})
        assert res.json()['status']['success']
        uuid_list = [uuid['__UUID__'] for uuid in res.json()['response']]
        return uuid_list

    # seems to take about 40 seconds per batch of 8 pictures
    def detect_seals_yolo(gid_list):
        url = base_url + "api/detect/cnn/yolo"
        res = requests.put(url, json={'gid_list': gid_list})
        assert res.json()['status']['success']
        return res.json()['response']

    def detect_seals_lightnet(gid_list):
        url = base_url + "api/detect/cnn/lightnet"
        # split into batches of 5, API likes to crash during large requests
        batch_size = 5
        res = []
        for i in range(0, len(gid_list), batch_size):
            res += requests.put(url, json={'gid_list': gid_list[i:i + batch_size]}).json()['response']
        return res

    # detect seals in the uploaded pictures, get annotation ids of each seal detected
    detect_list = [record['gid'] for record in json_save if 'aids' not in record]
    if len(detect_list) > 0:
        print('detecting seals in %s pictures using the yolo algorithm, this might take a while. During this phase the '
              'database web UI will be unavailable due to the detection running in the background. ' % len(detect_list))
        aid_list = detect_seals_yolo(detect_list)
        # add the annotation ids to the json database save
        zipped_list = list(zip(detect_list, aid_list))
        for gid, aids in zipped_list:
            for record in json_save:
                if record['gid'] == gid:
                    record['aids'] = aids

    detect_list = [record['gid'] for record in json_save if not record['aids']]
    if len(detect_list) > 0:
        print(
            'detecting seals in %s pictures using the lightnet algorithm, this might take a while. During this phase the '
            'database web UI will be unavailable due to the detection running in the background. ' % len(detect_list))
        aid_list = detect_seals_lightnet(detect_list)
        # add the annotation ids to the json database save
        zipped_list = list(zip(detect_list, aid_list))
        for gid, aids in zipped_list:
            for record in json_save:
                if record['gid'] == gid:
                    record['aids'] = aids

    # for the pictures where nothing was detected, add an annotation over the entire picture
    def add_annots_undetected_images():
        undetected_records = [record for record in json_save if not record['aids']]

        # need the image uuid to add an annotation
        gid_list = [record['gid'] for record in undetected_records]
        image_uuid_list = get_uuids(gid_list)

        # get picture dimensions
        url = base_url + "api/image/height"
        res = requests.get(url, json={'gid_list': gid_list})
        assert res.json()['status']['success']
        height_list = res.json()['response']

        url = base_url + "api/image/width"
        res = requests.get(url, json={'gid_list': gid_list})
        assert res.json()['status']['success']
        width_list = res.json()['response']

        # add annotation over the entire picture
        url = base_url + "api/annot/json"
        res = requests.post(url,
                            json={'image_uuid_list': image_uuid_list,
                                  'annot_bbox_list': [(0, 0, width, height) for width, height in
                                                      zip(width_list, height_list)],
                                  'annot_theta_list': [0] * len(image_uuid_list)})
        assert res.json()['status']['success']
        annot_uuid_list = [annot['__UUID__'] for annot in res.json()['response']]

        # get the aid of the annotation and add it to the json database save
        url = base_url + "api/annot/rowid/uuid"
        res = requests.get(url, json={'uuid_list': annot_uuid_list})
        assert res.json()['status']['success']

        # add the annotation ids to the json database save
        zipped_list = list(zip(gid_list, res.json()['response']))
        for gid, aid in zipped_list:
            for record in json_save:
                if record['gid'] == gid:
                    record['aids'] = [aid]

        print('Added full-picture annotations to all pictures where nothing was detected')

    add_annots_undetected_images()

    with open(save_file, 'w') as f:
        json.dump(json_save, f, indent=4, separators=(',', ': '))

    # convert list of lists to a regular list
    aid_list_flattened = [aid for record in json_save for aid in record['aids']]
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
        for record in json_save:
            if len(record['aids']) == 0:
                continue
            elif len(record['aids']) == 1:
                name_list.append(record['ID'])
            else:
                # more than one seal detected in the picture, unsure which one the original db is referring to
                # name the annots as unknown_NAME_0, unknown_NAME_1, etc
                name = record['ID']
                name_list += [f'unknown_{name}_{i}' for i, aid in enumerate(record['aids'])]
        res = requests.put(url, json={'aid_list': aid_list_flattened, 'name_list': name_list})
        assert res.json()['status']['success']
        print('set names for all annots')

        # add comments, append whether the seal is tagged or not to the end of each comment
        url = base_url + "api/annot/note"
        note_list = []
        for record in json_save:
            if len(record['aids']) == 0:
                continue
            elif len(record['aids']) == 1:
                note = record['comments']
                tagged = 'yes' if record['tagged'] == 1 else 'no'
                date = record['dt']
                note_list.append(f'{note}, tagged:{tagged}, date: {date}')
            else:
                # more than one seal detected in the picture, unsure which one the original db is referring to
                tagged = 'yes' if record['tagged'] == 1 else 'no'
                note_list += [f'unknown annot from image of {record["ID"]}, tagged: {tagged}, date: {record["dt"]}'] * len(record['aids'])
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
        for record in json_save:
            if len(record['aids']) == 0:
                continue
            elif len(record['aids']) == 1:
                gender_list.append(record['gender'])
            else:
                # more than one seal detected in the picture, unsure which one the original db is referring to
                gender_list += ['unknown'] * len(record['aids'])
        # enum: 0: female, 1: male, 2: unknown
        genders = {'female': 0, 'male': 1, 'unknown': 2, '': 2}
        for i in range(len(gender_list)):
            gender_list[i] = genders[gender_list[i]]
        res = requests.put(url, json={'aid_list': aid_list_flattened, 'name_sex_list': gender_list})
        assert res.json()['status']['success']
        print('set gender for all annots')

        # set quality as good
        # enum: 1: junk until 5: excellent
        url = base_url + "api/annot/quality"
        res = requests.put(url,
                           json={'aid_list': aid_list_flattened, 'annot_quality_list': [5] * len(aid_list_flattened)})
        assert res.json()['status']['success']
        print('set quality as excellent')

        # set ages in months
        # assuming that pup: 0-3y, juvenile: 3-5y, adult: 5-30y
        age_min_dict = {'pup': 0, 'juv': 36, 'adult': 60, 'Unknown': -1, '': -1}
        age_min_list = []
        age_max_dict = {'pup': 36, 'juv': 60, 'adult': 360, 'Unknown': -1, '': -1}
        age_max_list = []
        for record in json_save:
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
        viewpoint_dict = {'L': 'left', 'R': 'right', 'M': 'down', '': 'unknown'}
        viewpoint_list = []
        for record in json_save:
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

    # this function is used to match annotations, enable it if desired
    def match_annots():
        # get a list of all valid aids
        url = base_url + "api/annot"
        res = requests.get(url)
        assert res.status_code == 200
        valid_aid_list = res.json()['response']

        # get a list of all aids in the database that were not just added
        aid_list = [aid for record in json_save for aid in record['aids']]
        daid_list = [aid for aid in valid_aid_list if aid not in aid_list]

        if not daid_list:
            print('matching is not being performed because there were no annotations in the database to match against')
            return

        url = base_url + "api/query/chip/dict/simple"
        res = requests.get(url, json={'qaid_list': aid_list, 'daid_list': daid_list})
        response = res.json()['response']
        # save the matching results to a file
        with open('matching_results2.json', 'w') as f:
            json.dump(response, f, indent=4, separators=(',', ': '))
        return

    # TODO comment this out
    match_annots()


if __name__ == '__main__':
    main()
