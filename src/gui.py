from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QMessageBox, QFileDialog, QDialogButtonBox, QCheckBox, QDialog, QToolBar, QAction, QMainWindow, QComboBox
from PyQt5.QtGui import QPixmap, QImage, QPainter, QIcon, QDesktopServices
import requests


class SealRecognitionApp(QWidget):
    server_url: str
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seal Pattern Recognition")
        self.initUI()

    def initUI(self):
        # Create widgets
        self.server_label = QLabel("Wildbook Server URL:")
        self.server_input = QLineEdit()
        self.server_input.setText("http://localhost:8081")  # Set a default server URL
        self.upload_button = QPushButton("Upload Images")
        self.upload_button.clicked.connect(self.uploadImages)
        self.toolbar = QToolBar("Toolbar")

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.server_label)
        layout.addWidget(self.server_input)
        layout.addWidget(self.upload_button)
        self.setLayout(layout)

        # Create an action for the website button
        website_action = QAction(QIcon("seal.png"), "Open WBIA", self)
        website_action.triggered.connect(self.openWebsite)

        # Add the action to the toolbar
        self.toolbar.addAction(website_action)

    def openWebsite(self):
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
                    gids += self.uploadImage(self.server_url, url)

                # returns zipped list: [gid, [aid]]
                aids = self.detectImage(self.server_url, gids)

                matches = []
                for gid, aids in aids:
                    matches += gid, aids, self.matchImage(self.server_url, aids)

                # Todo add match threshold?
                if matches:
                    for gid, aids, matches in matches:
                        for match in matches:
                            qaid = match['qaid']
                            match_list = match['daid_list']
                            score_list = match['score_list']
                            best_match_index = score_list.index(max(score_list))
                            print('qaid: ' + str(qaid) + ', best match: ' + str(match_list[best_match_index]) +
                                  ', score: ' + str(max(score_list)))
                            best_match_aid = matches[0]
                            confirmed = self.confirmMatch(qaid, best_match_aid)
                            if not confirmed:
                                self.fillSealDetails(qaid, best_match_aid)
                else:
                    for gid, aids in aids:
                        for aid in aids:
                            #   todo: maybe pass in the gid and show entire picture?
                            self.fillSealDetails(aid, None)

                self.showResult("Image upload and recognition completed.")
            except requests.exceptions.RequestException:
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
        response = requests.post(f"{server_url}/api/upload/image", files={"image": open(image_path).read()})
        if response.status_code == 200:
            print("Image uploaded successfully")
            return response.json()['response']
        else:
            print("Image upload failed")
            return None

    def detectImage(self, server_url, gid_list):
        # Perform the detection algorithm on the new images using the API endpoint /api/detect/cnn/yolo
        # Use the server URL
        # For example:
        response = requests.put(f"{server_url}/api/detect/cnn/yolo", json={'gid_list': gid_list})
        if response.status_code == 200:
            print("Detection completed")
            aids = zip(gid_list, response.json()['response'])
            return aids
        else:
            print("Detection failed")
            return None

    def matchImage(self, server_url, aid_list):
        # Perform the matching algorithm on the new images using the API endpoint /api/query/chip/dict/simple
        # Use the server URL
        # For example:
        response = requests.get(f"{server_url}/api/query/chip/dict/simple", json={'qaid_list': aid_list})
        if response.status_code == 200:
            matches = response.json()['response']
            print(f"Matching completed. Matches: {matches}")
            return matches
        else:
            print("Matching failed")
            return None

    def confirmMatch(self, qaid, best_match):
        # Display the best match to the user and let them confirm if it's a match or not
        # Return True if confirmed, False otherwise
        # For example:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText(f"Best Match: {best_match}")

        # Fetch and display the images
        image1 = self.fetchImage(qaid)
        image2 = self.fetchImage(best_match)
        if image1 and image2:
            image1_label = QLabel()
            image2_label = QLabel()

            # Display the images in the message box
            self.setPixmapFromImage(image1_label, image1)
            self.setPixmapFromImage(image2_label, image2)
            msg_box.layout().addWidget(image1_label)
            msg_box.layout().addWidget(image2_label)

        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        result = msg_box.exec_()
        return result == QMessageBox.Yes

    def fetchImage(self, annot_aid):
        # Fetch the image from the server using the API endpoint /api/image/<id>
        # Return the image as a QImage or None if fetching failed
        self.server_url = self.server_input.text()
        # For example:
        try:
            response = requests.get(f"{self.server_url}/api/annot/{annot_aid}")
            if response.status_code == 200:
                image_data = response.content
                image = QImage.fromData(image_data)
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
        label.setMaximumSize(400, 400)

    def fillSealDetails(self, qaid, best_match):
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
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.exec_()

    def showSealDetailsForm(self,  details, aid):
        # Create a custom dialog box for the seal details form
        dialog = QDialog()
        dialog.setWindowTitle("Seal Details")
        layout = QVBoxLayout(dialog)

        name_label = QLabel("Name:")
        name_textbox = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(name_textbox)

        gender_label = QLabel("Gender:")
        gender_dropdown = QComboBox()
        gender_dropdown.addItem('female')
        gender_dropdown.addItem('male')
        gender_dropdown.addItem('unknown')
        layout.addWidget(gender_label)
        layout.addWidget(gender_dropdown)

        age_label = QLabel("Age:")
        # make a dropdown menu
        age_dropdown = QComboBox()
        age_dropdown.addItem("pup")
        age_dropdown.addItem("juv")
        age_dropdown.addItem("adult")
        layout.addWidget(age_label)
        layout.addWidget(age_dropdown)

        viewpoint_label = QLabel("Viewpoint:")
        viewpoint_dropdown = QComboBox()
        viewpoint_dropdown.addItem("left")
        viewpoint_dropdown.addItem("right")
        viewpoint_dropdown.addItem("bottom")
        viewpoint_dropdown.addItem("other")
        layout.addWidget(viewpoint_label)
        layout.addWidget(viewpoint_dropdown)

        comments_label = QLabel("Comments:")
        comments_textbox = QLineEdit()
        layout.addWidget(comments_label)
        layout.addWidget(comments_textbox)

        tagged_checkbox = QCheckBox("Tagged")
        layout.addWidget(tagged_checkbox)

        if details != {}:
            name_textbox.setText(details['name'])
            gender_dropdown.setCurrentText(details['gender'])
            age_dict = {0: 'pup', 60: 'juv', 360: 'adult'}
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
                'gender': gender_dropdown.text(),
                'age': age_dropdown.text(),
                'viewpoint': viewpoint_dropdown.text(),
                'quality': 'excellent',
                'comments': comments_textbox.text(),
                'tagged': 'yes' if tagged_checkbox.isChecked() else 'no'
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
        assert res.json()['status']['success']
        seal_details['gender'] = res.json()['response'][0]

        url = f"{self.server_url}/api/annot/age/months/min"
        res = requests.get(url, json={'aid_list': [aid]})
        assert res.json()['status']['success']
        seal_details['age'] = {'min': res.json()['response'][0]}

        url = f"{self.server_url}/api/annot/age/months/max"
        res = requests.get(url, json={'aid_list': [aid]})
        assert res.json()['status']['success']
        seal_details['age']['max'] = res.json()['response'][0]

        url = f"{self.server_url}/api/annot/name"
        res = requests.get(url, json={'aid_list': [aid]})
        assert res.json()['status']['success']
        seal_details['name'] = res.json()['response'][0]

        return seal_details

    def processSealDetails(self, form_values, aid):
        self.server_url = self.server_input.text()
        # Process the seal details and send them to the server using the API endpoint /api/annot/<id>
        # For example:
        print(f"Processing seal details: {form_values}")

        url = f"{self.server_url}/api/annot/interest"
        res = requests.put(url, json={'aid_list': [aid], 'flag_list': [1]})
        assert res.json()['status']['success']

        # set all annots as exemplars
        url = f"{self.server_url}/api/annot/exemplar"
        res = requests.put(url, json={'aid_list': [aid], 'flag_list': [1]})
        assert res.json()['status']['success']

        # set names for all annots
        url = f"{self.server_url}/api/annot/name"
        res = requests.put(url, json={'aid_list': [aid], 'name_list': [form_values['name']]})
        assert res.json()['status']['success']

        # add comments, append whether the seal is tagged or not to the end of each comment
        url = f"{self.server_url}/api/annot/note"
        res = requests.put(url, json={'aid_list': [aid], 'notes_list': form_values['comments'] + ', tagged: ' + form_values['tagged']})
        assert res.json()['status']['success']

        # set species
        url = f"{self.server_url}/api/annot/species"
        res = requests.put(url, json={'aid_list': [aid], 'species_text_list': ['harbour_seal']})
        assert res.json()['status']['success']

        # set gender for all annots
        url = f"{self.server_url}/api/annot/sex"
        # enum: 0: female, 1: male, 2: unknown
        gender = 0 if form_values['gender'] == 'female' else 1 if form_values['gender'] == 'male' else 2
        res = requests.put(url, json={'aid_list': [aid], 'name_sex_list': [gender]})
        assert res.json()['status']['success']

        # set quality as good
        # enum: 1: junk until 5: excellent
        url = f"{self.server_url}/api/annot/quality"
        res = requests.put(url, json={'aid_list': [aid], 'annot_quality_list': [5]})
        assert res.json()['status']['success']

        # set ages in months
        # assuming that pup: 0-3y, juvenile: 3-5y, adult: 5-30y
        age_min_dict = {'pup': 0, 'juv': 36, 'adult': 60, 'Unknown': -1, '': -1}
        age_max_dict = {'pup': 36, 'juv': 60, 'adult': 360, 'Unknown': -1, '': -1}

        url = f"{self.server_url}/api/annot/age/months/min"
        res = requests.put(url, json={'aid_list': [aid], 'annot_age_months_est_min_list': age_min_dict[form_values['age']]})
        assert res.json()['status']['success']

        url = f"{self.server_url}/api/annot/age/months/max"
        res = requests.put(url, json={'aid_list': [aid], 'annot_age_months_est_max_list': age_max_dict[form_values['age']]})
        assert res.json()['status']['success']

        # set viewpoint
        url = f"{self.server_url}/api/annot/viewpoint"
        viewpoint_dict = {'L': 'left', 'R': 'right', 'M': 'bottom', '': 'unspecified'}
        res = requests.put(url, json={'aid_list': [aid], 'viewpoint_list': form_values['viewpoint']})
        assert res.json()['status']['success']

        print('done')


if __name__ == "__main__":
    app = QApplication([])
    seal_recognition_app = SealRecognitionApp()
    seal_recognition_app.show()
    app.exec_()
