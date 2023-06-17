import requests
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QComboBox

from fetch_image import fetchImage, setPixmapFromImage


def fetchSealDetails(aid, server_url):
    seal_details = {}

    url = f"{server_url}/api/annot/sex"
    res = requests.get(url, json={'aid_list': [aid]})
    print(res.json())
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
    print(res.json())
    assert res.status_code == 200
    seal_details['name'] = res.json()['response'][0]

    return seal_details


class SealSightingDialog(QDialog):
    sighting: dict

    def __init__(self, qaid, server_url, best_match_aid=None):
        super().__init__()
        self.setWindowTitle("Seal Sighting Details")

        if best_match_aid:
            print("Populating form with best match details")
            best_match_details = fetchSealDetails(best_match_aid, server_url)
        else:
            print("Displaying form for filling in seal details")
            best_match_details = None

        self.sighting = {'aid': qaid}

        layout = QVBoxLayout(self)

        label = QLabel("Seal details" + ", match found" if best_match_details else "")
        layout.addWidget(label)

        image = fetchImage(qaid, server_url)
        if image:
            image_label = QLabel()
            setPixmapFromImage(label, image)
            layout.addWidget(image_label)

        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.comments_edit = QLineEdit()
        self.with_pup_edit = QLineEdit()

        self.age_dropdown = QComboBox()
        self.age_dropdown.addItems(["pup", "juv", "adult", "unknown"])

        self.gender_dropdown = QComboBox()
        self.gender_dropdown.addItems(["male", "female", "unknown"])

        self.viewpoint_dropdown = QComboBox()
        self.viewpoint_dropdown.addItems(["left", "right", "down", "up", "unknown"])

        if best_match_details:
            self.name_edit.setText(best_match_details['name'])
            self.age_dropdown.setCurrentText('unknown' if best_match_details['age']['min'] == -1 else
                                             'pup' if best_match_details['age']['min'] == 0 else
                                             'juv' if best_match_details['age']['min'] == 36 else
                                             'adult')
            self.gender_dropdown.setCurrentText(best_match_details['gender'])

        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Comments:", self.comments_edit)
        form_layout.addRow("With Pup:", self.with_pup_edit)
        form_layout.addRow("Age:", self.age_dropdown)
        form_layout.addRow("Gender:", self.gender_dropdown)
        form_layout.addRow("Viewpoint:", self.viewpoint_dropdown)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()

        done_button = QPushButton("Done")
        done_button.clicked.connect(self.addSighting)
        button_layout.addWidget(done_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def addSighting(self):
        name = self.name_edit.text()
        comments = self.comments_edit.text()
        with_pup = self.with_pup_edit.text()
        age = self.age_dropdown.currentText()
        gender = self.gender_dropdown.currentText()
        viewpoint = self.viewpoint_dropdown.currentText()

        sighting_details = {
            "orig_ID": name,
            "id": name,
            "comments": comments,
            "with_pup": with_pup,
            "age": age,
            "gender": gender,
            "viewpoint": viewpoint
        }

        self.sighting.update(sighting_details)
        self.accept()
        self.hide()

    def getSighting(self):
        print(self.sighting)
        return self.sighting
