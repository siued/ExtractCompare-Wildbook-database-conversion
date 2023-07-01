import json

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QDialog, QPushButton

from wildbook_util import setPixmapFromImage, fetchImage, get_comments


class ConfirmDialog(QDialog):
    def __init__(self, qaid, best_match, score, server_url):
        # Display the best match to the user and let them confirm if it's a match or not
        # Return True if confirmed, False otherwise
        super().__init__()
        self.setWindowTitle("Confirm Match")
        self.setMinimumSize(800, 400)

        layout = QVBoxLayout()

        # Display the best match text
        match_label = QLabel(f"Best Match: {best_match}, score: {score}")
        layout.addWidget(match_label)

        # Fetch and display the images
        image1 = fetchImage(qaid, server_url)
        image2 = fetchImage(best_match, server_url)
        if image1 and image2:
            image1_label = QLabel()
            image2_label = QLabel()

            # Display the images in the labels
            setPixmapFromImage(image1_label, image1)
            setPixmapFromImage(image2_label, image2)

            # Add the image labels to the layout
            layout.addWidget(image1_label)
            layout.addWidget(image2_label)

            note = get_comments([best_match], server_url)[0]
            note = json.loads(note)
            comment_label = QLabel(f'Name: {note["id"]}, '
                                   f'age: {note["age"]}, '
                                   f'date: {note["date"]}, '
                                   f'location: {note["location"]}, '
                                   f'comments: {note["comments"]}'
                                   )
            layout.addWidget(comment_label)
        else:
            raise Exception("Could not fetch images for confirm dialog")

        # Create buttons for confirmation
        confirm_button = QPushButton("Confirm")
        cancel_button = QPushButton("Reject")
        layout.addWidget(confirm_button)
        layout.addWidget(cancel_button)

        # Connect button signals
        confirm_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        self.setLayout(layout)
