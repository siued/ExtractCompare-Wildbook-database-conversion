import base64
import datetime
import json
import time
from tkinter import Tk
from tkinter.simpledialog import askstring

from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, \
    QFileDialog, QDialogButtonBox, QCheckBox, QDialog, QToolBar, QAction, \
    QComboBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt5.QtGui import QPixmap, QImage, QIcon, QDesktopServices
import requests
import docker_util


def get_comment(aid, server_url):
    url = f"{server_url}/api/annot/note"
    res = requests.get(url, json={'aid_list': [aid]})
    assert res.status_code == 200
    return res.json()['response'][0]


def get_uuids(gid_list, server_url):
    url = f"{server_url}/api/image/uuid"
    res = requests.get(url, json={'gid_list': gid_list})
    assert res.status_code == 200
    uuid_list = [uuid['__UUID__'] for uuid in res.json()['response']]
    return uuid_list


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

def get_aid_list_from_gids(server_url, gid_list):
    url = f"{server_url}/api/image/annot/rowid"
    res = requests.get(url, json={"gid_list": gid_list})
    assert res.status_code == 200
    aid_list = [aid for aids in res.json()["response"] for aid in aids]
    return aid_list

class SealRecognitionApp(QWidget):
    server_url: str

    def __init__(self,  port):
        super().__init__()
        self.setWindowTitle("Seal Pattern Recognition")
        self.resize(200, 150)
        self.server_url = f"http://localhost:{port}"
        self.initUI(port)

    def initUI(self, port):
        # Create widgets
        self.server_label = QLabel("Wildbook Server URL:")
        self.server_input = QLineEdit()
        self.server_input.setText(f"http://localhost:{port}")  # Set a default server URL
        self.upload_button = QPushButton("Upload Images")
        self.upload_button.clicked.connect(self.uploadImages)
        self.toolbar = QToolBar("Toolbar")
        self.sightingsButton = QPushButton("View Sightings")
        self.sightingsButton.clicked.connect(self.viewSightings)
        self.changeDetailsButton = QPushButton("Change Seal Details")
        self.changeDetailsButton.clicked.connect(self.changeSealDetails)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.server_label)
        layout.addWidget(self.server_input)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.sightingsButton)
        layout.addWidget(self.changeDetailsButton)
        self.setLayout(layout)

        # Create an action for the website button
        website_action = QAction(QIcon("seal.png"), "Open WBIA", self)
        website_action.triggered.connect(self.openWildbook)

        # Add the action to the toolbar
        self.toolbar.addAction(website_action)

    def changeSealDetails(self):
        dialog = QDialog()
        dialog.setWindowTitle("Change Seal Details")
        layout = QVBoxLayout()

        name_label = QLabel("Name:")
        name_textbox = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(name_textbox)

        gender_label = QLabel("Gender:")
        gender_dropdown = QComboBox()
        gender_dropdown.addItems(['female', 'male', 'unknown'])
        layout.addWidget(gender_label)
        layout.addWidget(gender_dropdown)

        button = QPushButton("Submit")

        def submit():
            gid_list, nid = get_gids_by_name(self.server_url, name_textbox.text())

            if not nid:
                self.showResult("Name not found")
            else:
                # change the gender for the given name
                url = f"{self.server_url}/api/name/sex"
                sex = 0 if gender_dropdown.currentText() == 'female' else 1 if gender_dropdown.currentText() == 'male' else 2
                res = requests.put(url, json={'name_rowid_list': [nid], 'name_sex_list': [sex]})
                assert res.status_code == 200
                print('Gender changed successfully for ' + name_textbox.text())

            dialog.close()

        button.clicked.connect(submit)
        layout.addWidget(button)

        dialog.setLayout(layout)
        dialog.exec_()

    def viewSightings(self):
        widget = QDialog()
        widget.setWindowTitle("Sightings")
        widget.resize(800, 800)
        layout = QVBoxLayout()

        label = QLabel("Enter name to view sightings:")
        layout.addWidget(label)

        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(lambda: self.updateSightingsTable(widget))
        layout.addWidget(self.refresh_button)

        self.sightingsTable = QTableWidget()
        headers = ["Date", "Location", " Comments", "Photo",  "With pup"]
        self.sightingsTable.setColumnCount(len(headers))
        self.sightingsTable.setRowCount(0)

        self.sightingsTable.setHorizontalHeaderLabels(headers)
        self.sightingsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sightingsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sightingsTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.sightingsTable.setMaximumWidth(widget.width())

        layout.addWidget(self.sightingsTable)
        widget.setLayout(layout)
        widget.exec_()

    def updateSightingsTable(self, widget):
        name = self.name_input.text()
        sightings = self.getSightings(name)
        self.sightingsTable.setRowCount(len(sightings))
        for i, sighting in enumerate(sightings):
            self.sightingsTable.setItem(i, 0, QTableWidgetItem(sighting["date"]))
            self.sightingsTable.setItem(i, 1, QTableWidgetItem(sighting["location"]))
            self.sightingsTable.setItem(i, 2, QTableWidgetItem(sighting["comments"]))
            self.sightingsTable.setItem(i, 3, QTableWidgetItem(sighting["with_photo"]))
            self.sightingsTable.setItem(i, 4, QTableWidgetItem(sighting["with_pup"]))
        self.sightingsTable.resizeColumnsToContents()
        self.sightingsTable.resizeRowsToContents()

    def getSightings(self, name):
        gid_list, nid = get_gids_by_name(self.server_url, name)

        sighting_list = []

        if gid_list:
            aid_list = get_aid_list_from_gids(self.server_url, gid_list)

            url = f"{self.server_url}/api/annot/name/rowid"
            res = requests.get(url, json={"aid_list": aid_list})
            assert res.status_code == 200
            nid_list = res.json()["response"]

            url = f"{self.server_url}/api/annot/note"
            res = requests.get(url, json={"aid_list": aid_list})
            assert res.status_code == 200
            note_list = res.json()["response"]

            for sighting_nid, note in zip(nid_list, note_list):
                if sighting_nid == nid:
                    note = json.loads(note)
                    sighting_list.append({"date": note["date"], "location": note["location"], "comments": note["comments"], "with_photo": 'Yes', "with_pup": note["with_pup"]})

        with open('sightings.json') as f:
            sightings = json.load(f)

        for sighting in sightings:
            if sighting["orig_ID"] == name or sighting["id"] == name:
                sighting_list.append({"date": sighting["date"], "location": sighting["location"], "comments": sighting["comments"], "with_photo": 'No', "with_pup": sighting["with_pup"]})

        sighting_list.sort(key=lambda x: x["date"])

        return sighting_list

    def openWildbook(self):
        # Open the website in the default web browser
        website_url = QUrl(self.server_input.text())
        QDesktopServices.openUrl(website_url)

    def uploadImages(self):
        # Get the server URL from the input field
        self.server_url = self.server_input.text()

        # Perform image upload and recognition tasks
        image_urls = self.selectImages()
        if image_urls:

            try:
                gids = []
                for url in image_urls:
                    gids.append(self.uploadImage(self.server_url, url))

                # returns zipped list: [gid, [aid]]
                aids_list = self.detectImage(self.server_url, gids)

                # in images where no annot was detected, add a full-picture annotation
                undetected_gid_list = [gid for gid, aids in aids_list if not aids]
                aids_list = [(gid, aids) for gid, aids in aids_list if aids]
                if undetected_gid_list:
                    aids_list += add_annots_undetected_images(undetected_gid_list, self.server_url)

                # do the matching in one call to make it faster
                list_to_match = [aid for gid, aids in aids_list for aid in aids]
                matches = self.matchImage(self.server_url, list_to_match)

                print('Matches found: ' + str(matches))
                for match in matches:
                    # check if any matches were found
                    if match['daid_list']:
                        qaid = match['qaid']
                        daid_list = match['daid_list']
                        score_list = match['score_list']
                        best_match_index = score_list.index(max(score_list))
                        print('qaid: ' + str(qaid) + ', best match: ' + str(daid_list[best_match_index]) +
                              ', score: ' + str(max(score_list)))
                        best_match_aid = daid_list[best_match_index]
                        confirmed = self.confirmMatch(qaid, best_match_aid, max(score_list), self.server_url)
                        print('Match confirmed' if confirmed else 'Match rejected')
                        if confirmed:
                            self.fillSealDetails(qaid, best_match_aid)
                        else:
                            self.fillSealDetails(qaid)
                    else:
                        print(f'No matches found for aid {match["qaid"]}.')
                        self.fillSealDetails(match['qaid'])

            except requests.exceptions.RequestException as e:
                print(e)
                self.showResult("An error occurred during API requests.")

    def selectImages(self):
        # Open a file dialog to select multiple image files
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Image files (*.jpg *.jpeg *.png *.bmp)")
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            return selected_files
        else:
            return []

    def uploadImage(self, server_url, image_path):
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

    def detectImage(self, server_url, gid_list):
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

    def matchImage(self, server_url, aid_list):
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
                response = requests.get(f"{server_url}/api/query/chip/dict/simple", json={'qaid_list': aid_list, 'daid_list': daid_list})
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

    def confirmMatch(self, qaid, best_match, score, server_url):
        # Display the best match to the user and let them confirm if it's a match or not
        # Return True if confirmed, False otherwise

        dialog = QDialog()
        dialog.setWindowTitle("Confirm Match")
        dialog.setMinimumSize(800, 400)

        layout = QVBoxLayout()

        # Display the best match text
        match_label = QLabel(f"Best Match: {best_match}, score: {score}")
        layout.addWidget(match_label)

        # Fetch and display the images
        image1 = self.fetchImage(qaid)
        image2 = self.fetchImage(best_match)
        if image1 and image2:
            image1_label = QLabel()
            image2_label = QLabel()

            # Display the images in the labels
            self.setPixmapFromImage(image1_label, image1)
            self.setPixmapFromImage(image2_label, image2)

            # Add the image labels to the layout
            layout.addWidget(image1_label)
            layout.addWidget(image2_label)

            comment_label = QLabel(f'Comment: {get_comment(best_match, server_url)}')
            layout.addWidget(comment_label)
        else:
            return False

        # Create buttons for confirmation
        confirm_button = QPushButton("Confirm")
        cancel_button = QPushButton("Reject")
        layout.addWidget(confirm_button)
        layout.addWidget(cancel_button)

        # Connect button signals
        confirm_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        dialog.setLayout(layout)

        # Execute the dialog and return the result
        result = dialog.exec_()
        return result == QDialog.Accepted

    def fetchImage(self, annot_aid):
        # Fetch the image from the server using the API endpoint /api/image/<id>
        # Return the image as a QImage or None if fetching failed
        self.server_url = self.server_input.text()
        # For example:
        try:
            response = requests.get(f"{self.server_url}/api/annot/{annot_aid}")
            if response.status_code == 200:
                # wildbook returns all image requests as base64 encoded jpeg
                image_data = response.json()['response']
                base64_string = image_data.split(',')[1]
                image_bytes = base64.b64decode(base64_string)
                image = QImage.fromData(image_bytes, "JPEG")
                return image
            else:
                print(f"Failed to fetch annot with ID: {annot_aid}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching image with ID: {annot_aid}")
            print(e)
            return None

    def setPixmapFromImage(self, label, image):
        # Set the image as a pixmap for the given label
        pixmap = QPixmap.fromImage(image)
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        label.setMaximumHeight(400)

    def fillSealDetails(self, qaid, best_match=None):
        # If no match, prompt the user to fill in the seal details using a form
        # Otherwise, populate the form with the details from the best match
        # For example:
        if best_match:
            # Populate the form with the best match details
            print("Populating form with best match details")
            details = self.fetchSealDetails(best_match)
        else:
            # Display the form for filling in seal details
            details = {}
            print("Displaying form for filling in seal details")
        self.showSealDetailsForm(details, qaid)

    def showResult(self, message):
        # Display a message box with the result
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Message")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.exec_()

    def showSealDetailsForm(self,  details, aid):
        print("Displaying seal details form: " + str(details))
        # Create a custom dialog box for the seal details form
        dialog = QDialog()
        dialog.setWindowTitle("Seal Details")
        layout = QVBoxLayout(dialog)

        image = self.fetchImage(aid)
        if image:
            image_label = QLabel()
            self.setPixmapFromImage(image_label, image)
            layout.addWidget(image_label)

        name_label = QLabel("Name:")
        name_textbox = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(name_textbox)

        gender_label = QLabel("Gender:")
        gender_dropdown = QComboBox()
        gender_dropdown.addItems(['female', 'male', 'unknown'])
        layout.addWidget(gender_label)
        layout.addWidget(gender_dropdown)

        age_label = QLabel("Age:")
        # make a dropdown menu
        age_dropdown = QComboBox()
        age_dropdown.addItems(["pup", "juv", "adult", "unknown"])
        layout.addWidget(age_label)
        layout.addWidget(age_dropdown)

        viewpoint_label = QLabel("Side: (which side of the seal is visible?)")
        viewpoint_dropdown = QComboBox()
        viewpoint_dropdown.addItems(["left", "right", "down", "up", "unknown"])
        layout.addWidget(viewpoint_label)
        layout.addWidget(viewpoint_dropdown)

        comments_label = QLabel("Comments:")
        comments_textbox = QLineEdit()
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        comments_textbox.setText(f"date: {current_date}")
        layout.addWidget(comments_label)
        layout.addWidget(comments_textbox)

        # Populate the form fields with the details from the best match if available
        if details != {}:
            name_textbox.setText(details['name'])
            gender_dropdown.setCurrentText(details['gender'])
            age_dict = {0: 'pup', 36: 'juv', 60: 'adult', -1: 'unknown'}
            age_dropdown.setCurrentText(age_dict[details['age']['min']])
            comments_textbox.setText('')

        # Create dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)

        def accept():
            # Retrieve the values from the form fields when the OK button is clicked
            form_values = {
                'name': name_textbox.text(),
                'species': 'harbour_seal',
                'gender': gender_dropdown.currentText(),
                'age': age_dropdown.currentText(),
                'viewpoint': viewpoint_dropdown.currentText(),
                'quality': 'excellent',
                'comments': comments_textbox.text()
            }
            dialog.close()
            self.processSealDetails(form_values, aid)

        button_box.accepted.connect(accept)
        button_box.rejected.connect(dialog.reject)

        # Show the dialog box
        dialog.exec_()

    def fetchSealDetails(self, aid):
        self.server_url = self.server_input.text()
        seal_details = {}

        url = f"{self.server_url}/api/annot/sex"
        res = requests.get(url, json={'aid_list': [aid]})
        print(res.json())
        assert res.status_code == 200
        gender = res.json()['response'][0]
        seal_details['gender'] = 'female' if gender == 0 else 'male' if gender == 1 else 'unknown'

        url = f"{self.server_url}/api/annot/age/months/min"
        res = requests.get(url, json={'aid_list': [aid]})
        assert res.status_code == 200
        seal_details['age'] = {'min': res.json()['response'][0]}

        url = f"{self.server_url}/api/annot/age/months/max"
        res = requests.get(url, json={'aid_list': [aid]})
        assert res.status_code == 200
        seal_details['age']['max'] = res.json()['response'][0]

        url = f"{self.server_url}/api/annot/name/text"
        res = requests.get(url, json={'aid_list': [aid]})
        print(res.json())
        assert res.status_code == 200
        seal_details['name'] = res.json()['response'][0]

        return seal_details

    def processSealDetails(self, form_values, aid):
        self.server_url = self.server_input.text()
        # Process the seal details and send them to the server using the API endpoint /api/annot/<id>
        # For example:
        print(f"Processing seal details: {form_values}")

        url = f"{self.server_url}/api/annot/interest"
        res = requests.put(url, json={'aid_list': [aid], 'flag_list': [1]})
        assert res.status_code == 200

        # set all annots as exemplars
        url = f"{self.server_url}/api/annot/exemplar"
        res = requests.put(url, json={'aid_list': [aid], 'flag_list': [1]})
        assert res.status_code == 200

        # set names for all annots
        url = f"{self.server_url}/api/annot/name"
        res = requests.put(url, json={'aid_list': [aid], 'name_list': [form_values['name']]})
        assert res.status_code == 200

        # add comments
        comment = form_values['comments']
        if comment != '':
            url = f"{self.server_url}/api/annot/note"
            res = requests.put(url, json={'aid_list': [aid], 'notes_list': [comment]})
            assert res.status_code == 200

        # set species
        url = f"{self.server_url}/api/annot/species"
        res = requests.put(url, json={'aid_list': [aid], 'species_text_list': ['harbour_seal']})
        assert res.status_code == 200

        # set gender for all annots
        url = f"{self.server_url}/api/annot/sex"
        # enum: 0: female, 1: male, 2: unknown
        gender = 0 if form_values['gender'] == 'female' else 1 if form_values['gender'] == 'male' else 2
        res = requests.put(url, json={'aid_list': [aid], 'name_sex_list': [gender]})
        assert res.status_code == 200

        # set quality as good
        # enum: 1: junk until 5: excellent
        url = f"{self.server_url}/api/annot/quality"
        res = requests.put(url, json={'aid_list': [aid], 'annot_quality_list': [5]})
        assert res.status_code == 200

        # set ages in months
        # assuming that pup: 0-3y, juvenile: 3-5y, adult: 5-30y
        age_min_dict = {'pup': 0, 'juv': 36, 'adult': 60, 'unknown': -1, '': -1}
        age_max_dict = {'pup': 36, 'juv': 60, 'adult': 360, 'unknown': -1, '': -1}

        url = f"{self.server_url}/api/annot/age/months/min"
        age = age_min_dict[form_values['age']]
        res = requests.put(url, json={'aid_list': [aid], 'annot_age_months_est_min_list': [age]})
        assert res.status_code == 200

        url = f"{self.server_url}/api/annot/age/months/max"
        age = age_max_dict[form_values['age']]
        res = requests.put(url, json={'aid_list': [aid], 'annot_age_months_est_max_list': [age]})
        assert res.status_code == 200

        # set viewpoint
        if form_values['viewpoint']:
            url = f"{self.server_url}/api/annot/viewpoint"
            res = requests.put(url, json={'aid_list': [aid], 'viewpoint_list': [form_values['viewpoint']]})
            assert res.status_code == 200

        self.showResult('Successfully updated the details for annotation with ID: ' + str(aid))

    def closeEvent(self, event):
        # TODO: uncomment for production
        # docker_util.stop_wbia_container()
        self.close()
        super().closeEvent(event)


def get_text_input(title, textfield):
    Tk().withdraw()  # Hide the main window
    text_input = askstring(textfield, title)
    return text_input


if __name__ == "__main__":
    # docker_util assumes the name of the Wildbook container is 'wildbook-ia'
    default_port = 8081
    port = get_text_input(f'Enter the port number of the Wildbook server, leave blank for default port {default_port}',
                          'Port number')
    if port is None:
        exit()
    if port == '':
        port = default_port
    if not docker_util.ensure_docker_wbia(port):
        print(f'ERROR: Please make sure Docker Desktop is running and try again. Also make sure you typed in the '
              f'correct port number: {port}')
        time.sleep(2)
        exit(1)
    app = QApplication([])
    seal_recognition_app = SealRecognitionApp(port)
    seal_recognition_app.show()
    app.exec_()
