from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QMessageBox, QFileDialog, QDialogButtonBox, QCheckBox, QDialog, QToolBar, QAction
from PyQt5.QtGui import QPixmap, QImage, QPainter, QIcon, QDesktopServices
import requests


class SealRecognitionApp(QWidget):
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

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.server_label)
        layout.addWidget(self.server_input)
        layout.addWidget(self.upload_button)
        self.setLayout(layout)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Create an action for the website button
        website_action = QAction(QIcon("seal.png"), "Open WBIA", self)
        website_action.triggered.connect(self.openWebsite)

        # Add the action to the toolbar
        toolbar.addAction(website_action)

    def openWebsite(self):
        # Open the website in the default web browser
        website_url = QUrl("http://localhost:8081")
        QDesktopServices.openUrl(website_url)

    def uploadImages(self):
        # Get the server URL from the input field
        server_url = self.server_input.text()

        # Perform image upload and recognition tasks
        image_urls = self.selectImages()
        if image_urls:
            gids = []
            try:
                for url in image_urls:
                    gids += self.uploadImage(server_url, url)
                aids = self.detectImage(server_url, gids)
                matches = self.matchImage(server_url, aids)

                if matches:
                    best_match = matches[0]
                    confirmed = self.confirmMatch(best_match)
                    if not confirmed:
                        self.fillSealDetails(best_match)
                else:
                    self.fillSealDetails(None)

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

    def uploadImage(self, server_url, image_url):
        # Perform the image upload using the API endpoint /api/upload/image
        # Use the server URL and the provided image URL or file path
        # For example:
        response = requests.post(f"{server_url}/api/upload/image", files={"image": open(image_url).read()})
        if response.status_code == 200:
            print("Image uploaded successfully")
            gid = response.json()['response']
            return gid
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
            # TODO find highest match
            print(f"Matching completed. Matches: {matches}")
            return matches
        else:
            print("Matching failed")
            return None

    def confirmMatch(self, best_match):
        # Display the best match to the user and let them confirm if it's a match or not
        # Return True if confirmed, False otherwise
        # For example:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText(f"Best Match: {best_match}")

        # Fetch and display the images
        image1 = self.fetchImage(best_match['image1_id'])
        image2 = self.fetchImage(best_match['image2_id'])
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

    def fetchImage(self, server_url, image_gid):
        # Fetch the image from the server using the API endpoint /api/image/<id>
        # Return the image as a QImage or None if fetching failed
        # For example:
        try:
            response = requests.get(f"{server_url}/api/image/{image_gid}")
            if response.status_code == 200:
                image_data = response.content
                image = QImage.fromData(image_data)
                return image
            else:
                print(f"Failed to fetch image with ID: {image_gid}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching image with ID: {image_gid}")
            print(e)
            return None

    def setPixmapFromImage(self, label, image):
        # Set the image as a pixmap for the given label
        pixmap = QPixmap.fromImage(image)
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        label.setMaximumSize(400, 400)

    def fillSealDetails(self, best_match):
        # If no match, prompt the user to fill in the seal details using a form
        # Otherwise, populate the form with the details from the best match
        # For example:
        if best_match:
            # TODO make the form
            # Populate the form with the best match details
            print("Populating form with best match details")
        else:
            # Display the form for filling in seal details
            print("Displaying form for filling in seal details")
            self.showSealDetailsForm()

    def showResult(self, message):
        # Display a message box with the result
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.exec_()

    def showSealDetailsForm(self):
        # Create a custom dialog box for the seal details form
        dialog = QDialog()
        dialog.setWindowTitle("Seal Details")
        layout = QVBoxLayout(dialog)

        # Create form fields and labels
        species_label = QLabel("Species:")
        species_textbox = QLineEdit()
        layout.addWidget(species_label)
        layout.addWidget(species_textbox)

        gender_label = QLabel("Gender:")
        gender_textbox = QLineEdit()
        layout.addWidget(gender_label)
        layout.addWidget(gender_textbox)

        age_label = QLabel("Age:")
        age_textbox = QLineEdit()
        layout.addWidget(age_label)
        layout.addWidget(age_textbox)

        viewpoint_label = QLabel("Viewpoint:")
        viewpoint_textbox = QLineEdit()
        layout.addWidget(viewpoint_label)
        layout.addWidget(viewpoint_textbox)

        quality_label = QLabel("Quality:")
        quality_textbox = QLineEdit()
        layout.addWidget(quality_label)
        layout.addWidget(quality_textbox)

        comments_label = QLabel("Comments:")
        comments_textbox = QLineEdit()
        layout.addWidget(comments_label)
        layout.addWidget(comments_textbox)

        tagged_checkbox = QCheckBox("Tagged")
        layout.addWidget(tagged_checkbox)

        # Create dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)

        def accept():
            # Retrieve the values from the form fields when the OK button is clicked
            form_values = {
                'species': species_textbox.text(),
                'gender': gender_textbox.text(),
                'age': age_textbox.text(),
                'viewpoint': viewpoint_textbox.text(),
                'quality': quality_textbox.text(),
                'comments': comments_textbox.text(),
                'tagged': 'yes' if tagged_checkbox.isChecked() else 'no'
            }
            dialog.close()
            self.processSealDetails(form_values)
            # TODO process details

        button_box.accepted.connect(accept)
        button_box.rejected.connect(dialog.reject)

        # Show the dialog box
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication([])
    seal_recognition_app = SealRecognitionApp()
    seal_recognition_app.show()
    app.exec_()
