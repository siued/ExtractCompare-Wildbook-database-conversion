import base64
import requests
from PyQt5.QtGui import QImage, QPixmap


def fetchImage(annot_aid, server_url):
    # Fetch the image from the server using the API endpoint /api/image/<id>
    # Return the image as a QImage or None if fetching failed
    # For example:
    try:
        response = requests.get(f"{server_url}/api/annot/{annot_aid}")
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


def setPixmapFromImage(label, image):
    # Set the image as a pixmap for the given label
    pixmap = QPixmap.fromImage(image)
    label.setPixmap(pixmap)
    label.setScaledContents(True)
    label.setMaximumHeight(400)