from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QAbstractItemView, \
    QTableWidgetItem

from wildbook_util import get_sightings_from_name


class ViewSightingsDialog(QDialog):
    server_url: str

    def __init__(self, server_url):
        super().__init__()

        font = self.font()
        font.setPointSize(18)
        self.setFont(font)

        self.server_url = server_url
        self.setWindowTitle("Sightings")
        self.resize(800, 800)
        layout = QVBoxLayout()

        label = QLabel("Enter name to view sightings:")
        layout.addWidget(label)

        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.updateSightingsTable)
        layout.addWidget(self.refresh_button)

        self.sightingsTable = QTableWidget()
        headers = ["Name", "Old Name", "Date", "Location", "Age", "Photo",  "With pup", "Comments"]
        self.sightingsTable.setColumnCount(len(headers))
        self.sightingsTable.setRowCount(0)

        self.sightingsTable.setHorizontalHeaderLabels(headers)
        self.sightingsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sightingsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sightingsTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.sightingsTable.setMaximumWidth(self.width())

        layout.addWidget(self.sightingsTable)
        self.setLayout(layout)

    def updateSightingsTable(self):
        print("Updating sightings table")
        name = self.name_input.text()
        sightings = get_sightings_from_name(name, self.server_url)
        self.sightingsTable.setRowCount(len(sightings))
        for i, sighting in enumerate(sightings):
            self.sightingsTable.setItem(i, 0, QTableWidgetItem(sighting["name"]))
            self.sightingsTable.setItem(i, 1, QTableWidgetItem(sighting["old_name"]))
            self.sightingsTable.setItem(i, 2, QTableWidgetItem(sighting["date"]))
            self.sightingsTable.setItem(i, 3, QTableWidgetItem(sighting["location"]))
            self.sightingsTable.setItem(i, 4, QTableWidgetItem(sighting["age"]))
            self.sightingsTable.setItem(i, 5, QTableWidgetItem(sighting["with_photo"]))
            self.sightingsTable.setItem(i, 6, QTableWidgetItem(sighting["with_pup"]))
            self.sightingsTable.setItem(i, 7, QTableWidgetItem(sighting["comments"]))
        self.sightingsTable.resizeColumnsToContents()
        self.sightingsTable.resizeRowsToContents()
