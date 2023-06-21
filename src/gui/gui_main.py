import time

from PyQt5.QtCore import QUrl, QDate
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, \
    QDialogButtonBox, QDialog, QDateEdit

import docker_util
from add_sightings import AddSightingsDialog
from change_seal_details import ChangeSealDetailsDialog
from other_util import show_message
from export_to_excel import export_to_excel
from view_sightings import ViewSightingsDialog


class SealRecognitionApp(QWidget):
    server_url: str


    def __init__(self, port):
        super().__init__()
        self.setWindowTitle("Seal Pattern Recognition")
        self.resize(500, 500)

        font = self.font()
        font.setPointSize(18)
        self.setFont(font)

        self.server_url = f"http://localhost:{port}"

        self.openWildbookButton = QPushButton("Open Wildbook")
        self.openWildbookButton.clicked.connect(self.openWildbook)

        self.upload_button = QPushButton("Add sightings")
        self.upload_button.clicked.connect(self.addSightings)

        self.sightingsButton = QPushButton("View Sightings")
        self.sightingsButton.clicked.connect(self.viewSightings)

        self.changeDetailsButton = QPushButton("Change Seal Details")
        self.changeDetailsButton.clicked.connect(self.changeSealDetails)

        self.exportButton = QPushButton("Export to Excel")
        self.exportButton.clicked.connect(lambda: export_to_excel(self.server_url))

        layout = QVBoxLayout()
        layout.addWidget(self.openWildbookButton)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.sightingsButton)
        layout.addWidget(self.changeDetailsButton)
        layout.addWidget(self.exportButton)
        self.setLayout(layout)

    def viewSightings(self):
        dialog = ViewSightingsDialog(self.server_url)
        dialog.exec_()

    def changeSealDetails(self):
        dialog = ChangeSealDetailsDialog(self.server_url)
        dialog.exec_()

    def openWildbook(self):
        # Open the website in the default web browser
        website_url = QUrl(self.server_url)
        QDesktopServices.openUrl(website_url)

    # ask for date and location, then pass them into the add sightings pipeline
    def addSightings(self):
        dialog = QDialog()
        dialog.setWindowTitle("Date and Location")
        dialog.resize(300, 100)

        layout = QVBoxLayout()

        date_label = QLabel("Date:")
        layout.addWidget(date_label)

        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        layout.addWidget(date_edit)

        location_label = QLabel("Location:")
        layout.addWidget(location_label)

        location_edit = QLineEdit()
        location_edit.setPlaceholderText("Location")
        layout.addWidget(location_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        def acceptAndUpload():
            dialog.close()
            AddSightingsDialog(date_edit.date().toString("yyyy-MM-dd"), location_edit.text(), self.server_url)

        button_box.accepted.connect(acceptAndUpload)
        button_box.rejected.connect(dialog.reject)
        dialog.exec_()

    @staticmethod
    def showResult(message):
        # Display a message box with the result
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Message")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.exec_()

    def closeEvent(self, event):
        # docker_util.stop_wbia_container()
        self.close()
        super().closeEvent(event)


if __name__ == "__main__":
    # docker_util assumes the name of the Wildbook container is 'wildbook-ia'
    default_port = 8081
    if not docker_util.ensure_docker_wbia(default_port):
        show_message('Docker error', 'ERROR: Please make sure Docker Desktop is running and try again')
        exit()
    app = QApplication([])
    seal_recognition_app = SealRecognitionApp(default_port)
    seal_recognition_app.show()
    try:
        app.exec_()
    except Exception as e:
        time = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
        print(str(e))
        with open(f'crash_log_{time}.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')
        show_message('Error', 'An error occurred. The app will now close. You can find a crash log in the '
                                    'directory where the app is located. ')
