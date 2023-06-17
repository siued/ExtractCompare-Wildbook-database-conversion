import json
import time
from tkinter import Tk
from tkinter.simpledialog import askstring

from PyQt5.QtCore import QUrl, QSize, QDate, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, \
    QFileDialog, QDialogButtonBox, QCheckBox, QDialog, QToolBar, QAction, \
    QComboBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QDateEdit, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QIcon, QDesktopServices
import requests
import docker_util
from add_sightings_dialog import AddSightingsDialog


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
        self.upload_button.clicked.connect(self.addSightings)
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
        self.refresh_button.clicked.connect(self.updateSightingsTable)
        layout.addWidget(self.refresh_button)

        self.sightingsTable = QTableWidget()
        headers = ["Name", "Date", "Location", " Comments", "Photo",  "With pup"]
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

    def updateSightingsTable(self):
        name = self.name_input.text()
        sightings = self.getSightings(name)
        self.sightingsTable.setRowCount(len(sightings))
        for i, sighting in enumerate(sightings):
            self.sightingsTable.setItem(i, 0, QTableWidgetItem(sighting["name"]))
            self.sightingsTable.setItem(i, 1, QTableWidgetItem(sighting["date"]))
            self.sightingsTable.setItem(i, 2, QTableWidgetItem(sighting["location"]))
            self.sightingsTable.setItem(i, 3, QTableWidgetItem(sighting["comments"]))
            self.sightingsTable.setItem(i, 4, QTableWidgetItem(sighting["with_photo"]))
            self.sightingsTable.setItem(i, 5, QTableWidgetItem(sighting["with_pup"]))
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
                    sighting_list.append({"date": note["date"], "location": note["location"], "comments": note["comments"], "with_photo": 'Yes', "with_pup": note["with_pup"], 'name': note['id']})

        with open('sightings.json') as f:
            sightings = json.load(f)

        for sighting in sightings:
            if sighting["orig_ID"] == name or sighting["id"] == name:
                sighting_list.append({"date": sighting["date"], "location": sighting["location"], "comments": sighting["comments"], "with_photo": 'No', "with_pup": sighting["with_pup"], 'name': sighting['id']})

        sighting_list.sort(key=lambda x: x["date"], reverse=True)

        return sighting_list

    def openWildbook(self):
        # Open the website in the default web browser
        website_url = QUrl(self.server_input.text())
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
            server_url = self.server_input.text()
            AddSightingsDialog(date_edit.date().toString("yyyy-MM-dd"), location_edit.text(), server_url)

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
