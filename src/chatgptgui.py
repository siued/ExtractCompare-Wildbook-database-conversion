from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, QPainter
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
        self.server_input.setText("https://wildbook.example.com")  # Set a default server URL
        self.upload_button = QPushButton("Upload Images")
        self.upload_button.clicked.connect(self.uploadImages)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.server_label)
        layout.addWidget(self.server_input)
        layout.addWidget(self.upload_button)
        self.setLayout(layout)

    def uploadImages(self):
        # Get the server URL from the input field
        server_url = self.server_input.text()

        # Perform image upload and recognition tasks
        image_urls = self.selectImages()
        if image_urls:
            try:
                for url in image_urls:
                    self.uploadImage(server_url, url)
                    self.detectImage(server_url)
                    matches = self.matchImage(server_url)

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
        # Here you can implement a file selection dialog or any other method to choose the images to upload
        # Return a list of image URLs or file paths
        # For example:
        image_urls = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
            "https://example.com/image3.jpg"
        ]
        return image_urls

    def uploadImage(self, server_url, image_url):
        # Perform the image upload using the API endpoint /api/upload/image
        # Use the server URL and the provided image URL or file path
        # For example:
        response = requests.post(f"{server_url}/api/upload/image", json={"url": image_url})
        if response.status_code == 200:
            print("Image uploaded successfully")
        else:
            print("Image upload failed")

    def detectImage(self, server_url):
        # Perform the detection algorithm on the new images using the API endpoint /api/detect/cnn/yolo
        # Use the server URL
        # For example:
        response = requests.post(f"{server_url}/api/detect/cnn/yolo")
        if response.status_code == 200:
            print("Detection completed")
        else:
            print("Detection failed")

    def matchImage(self, server_url):
        # Perform the matching algorithm on the new images using the API endpoint /api/query/chip/dict/simple
        # Use the server URL
        # For example:
        response = requests.post(f"{server_url}/api/query/chip/dict/simple")
        if response.status_code == 200:
            matches = response.json()
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

    def fetchImage(self, image_id):
        # Fetch the image from the server using the API endpoint /api/image/<id>
        # Return the image as a QImage or None if fetching failed
        # For example:
        try:
            response = requests.get(f"{server_url}/api/image/{image_id}")
            if response.status_code == 200:
                image_data = response.content
                image = QImage.fromData(image_data)
                return image
            else:
                print(f"Failed to fetch image with ID: {image_id}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching image with ID: {image_id}")
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
            # Populate the form with the best match details
            print("Populating form with best match details")
        else:
            # Display the form for filling in seal details
            print("Displaying form for filling in seal details")

    def showResult(self, message):
        # Display a message box with the result
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.exec_()

if __name__ == "__main__":
    app = QApplication([])
    seal_recognition_app = SealRecognitionApp()
    seal_recognition_app.show()
    app.exec_()
