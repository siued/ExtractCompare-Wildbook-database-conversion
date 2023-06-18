import requests
from PyQt5.QtWidgets import QFileDialog

import docker_util
from add_sighting_details import SealSightingDialog
from confirm import ConfirmDialog
from wildbook_util import get_uuids


def add_annots_undetected_images(gid_list, server_url):
    # need the image uuid to add an annotation
    image_uuid_list = get_uuids(gid_list, server_url)

    # get picture dimensions
    url = f"{server_url}/api/image/height"
    res = requests.get(url, json={'gid_list': gid_list})
    assert res.status_code == 200
    height_list = res.json()['response']

    url = f"{server_url}/api/image/width"
    res = requests.get(url, json={'gid_list': gid_list})
    assert res.status_code == 200
    width_list = res.json()['response']

    # add annotation over the entire picture
    url = f"{server_url}/api/annot/json"
    res = requests.post(url,
                        json={'image_uuid_list': image_uuid_list,
                              'annot_bbox_list': [(0, 0, width, height) for width, height in
                                                  zip(width_list, height_list)],
                              'annot_theta_list': [0]})
    assert res.status_code == 200
    annot_uuid_list = [annot['__UUID__'] for annot in res.json()['response']]

    # get the aid of the annotation and add it to the json database save
    url = f"{server_url}/api/annot/rowid/uuid"
    res = requests.get(url, json={'uuid_list': annot_uuid_list})
    assert res.status_code == 200

    # add the annotation ids to the json database save
    zipped_list = list(zip(gid_list, [[aid] for aid in res.json()['response']]))

    print('Added full-picture annotations to all pictures where nothing was detected')
    return zipped_list


def uploadImages(server_url):
    # Get the server URL from the input field

    # Perform image upload and recognition tasks
    image_urls = selectImages()
    sightings = []
    if image_urls:
        try:
            gids = []
            for url in image_urls:
                gids.append(uploadImage(server_url, url))

            # returns zipped list: [gid, [aid]]
            aids_list = detectImage(server_url, gids)

            # in images where no annot was detected, add a full-picture annotation
            undetected_gid_list = [gid for gid, aids in aids_list if not aids]
            aids_list = [(gid, aids) for gid, aids in aids_list if aids]
            if undetected_gid_list:
                aids_list += add_annots_undetected_images(undetected_gid_list, server_url)

            # do the matching in one call to make it faster
            list_to_match = [aid for gid, aids in aids_list for aid in aids]
            matches = matchImage(server_url, list_to_match)

            print('Matches found: ' + str(matches))

            for match in matches:
                confirmed = False
                confirmed_match_aid = None
                # check if any matches were found
                if match['daid_list']:
                    qaid = match['qaid']
                    daid_list = match['daid_list']
                    score_list = match['score_list']
                    best_match_index = score_list.index(max(score_list))
                    print('qaid: ' + str(qaid) + ', best match: ' + str(daid_list[best_match_index]) +
                          ', score: ' + str(max(score_list)))
                    best_match_aid = daid_list[best_match_index]
                    try:
                        confirm_dialog = ConfirmDialog(qaid, best_match_aid, max(score_list), server_url)
                    except Exception as e:
                        print(e)
                        continue
                    confirmed = confirm_dialog.exec_()
                    print('Match confirmed' if confirmed else 'Match rejected')
                    if confirmed:
                        sighting_dialog = SealSightingDialog(qaid, server_url, best_match_aid)
                        confirmed_match_aid = best_match_aid
                    else:
                        sighting_dialog = SealSightingDialog(qaid, server_url)
                else:
                    print(f'No matches found for aid {match["qaid"]}.')
                    sighting_dialog = SealSightingDialog(match["qaid"], server_url)
                sighting_dialog.exec_()
                sighting = sighting_dialog.getSighting()
                if confirmed:
                    sighting['confirmed_aid'] = confirmed_match_aid
                sightings.append(sighting)
            for sighting in sightings:
                sighting['image'] = 'yes'
            return sightings

        except requests.exceptions.RequestException as e:
            print(e)
            print("An error occurred during API requests.")
            return []


def selectImages():
    # Open a file dialog to select multiple image files
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    file_dialog.setNameFilter("Image files (*.jpg *.jpeg *.png *.bmp)")
    if file_dialog.exec_():
        selected_files = file_dialog.selectedFiles()
        return selected_files
    else:
        return []


def uploadImage(server_url, image_path):
    # Perform the image upload using the API endpoint /api/upload/image
    # Use the server URL and the provided image URL or file path
    # For example:
    print(f"Uploading image {image_path}")
    response = requests.post(f"{server_url}/api/upload/image", files={"image": open(image_path, 'rb').read()})
    if response.status_code == 200:
        print("Image uploaded successfully")
        return response.json()['response']
    else:
        print("Image upload failed")
        return None


def detectImage(server_url, gid_list):
    print("Performing detection")
    # Perform the detection algorithm on the new images using the API endpoint /api/detect/cnn/yolo
    # Use the server URL
    # For example:
    response = requests.put(f"{server_url}/api/detect/cnn/yolo", json={'gid_list': gid_list})
    if response.status_code == 200:
        print("Detection completed")
        aids = list(zip(gid_list, response.json()['response']))
        return aids
    else:
        print("Detection failed")
        return None


def matchImage(server_url, aid_list):
    # First get the list of all annotations using the API endpoint /api/annot
    res = requests.get(f"{server_url}/api/annot")
    assert res.status_code == 200
    daid_list = res.json()['response']
    # Perform the matching algorithm on the new images using the API endpoint /api/query/chip/dict/simple
    # The server sometimes crashes during the matching procedure, so the loop handles that
    # The matches computed up to the crash get cached in Wildbook, so this should never result in an infinite loop
    while True:
        try:
            print("Performing matching")
            response = requests.get(f"{server_url}/api/query/chip/dict/simple",
                                    json={'qaid_list': aid_list, 'daid_list': daid_list})
            break
        except requests.exceptions.RequestException as e:
            print('Backend crashed while trying to match image, restarting and retrying')
            docker_util.ensure_docker_wbia()
    if response.status_code == 200:
        matches = response.json()['response']
        print(f"Matching completed.")
        return matches
    else:
        print("Matching failed")
        return None
