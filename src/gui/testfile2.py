from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem

class SealSightingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seal Sighting Details")
        self.resize(800, 800)

        self.sightings = []

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Comments", "With Pup", "Age", "Gender"])
        self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.AnyKeyPressed)

        # Initialize the table with 10 rows
        self.table.setRowCount(10)
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = QTableWidgetItem()
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        add_rows_button = QPushButton("Add 10 Rows")
        add_rows_button.clicked.connect(self.addRows)
        button_layout.addWidget(add_rows_button)

        done_button = QPushButton("Done")
        done_button.clicked.connect(self.accept)
        button_layout.addWidget(done_button)

        layout.addLayout(button_layout)

    def addRows(self):
        current_row_count = self.table.rowCount()
        new_row_count = current_row_count + 10
        self.table.setRowCount(new_row_count)
        for row in range(current_row_count, new_row_count):
            for col in range(self.table.columnCount()):
                item = QTableWidgetItem()
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

    def getSightings(self):
        sightings = []
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            comments_item = self.table.item(row, 1)
            with_pup_item = self.table.item(row, 2)
            age_item = self.table.item(row, 3)
            gender_item = self.table.item(row, 4)

            name = name_item.text() if name_item else ""
            comments = comments_item.text() if comments_item else ""
            with_pup = with_pup_item.text() if with_pup_item else ""
            age = age_item.text() if age_item else ""
            gender = gender_item.text() if gender_item else ""

            sighting_details = {
                "Name": name,
                "Comments": comments,
                "With Pup": with_pup,
                "Age": age,
                "Gender": gender
            }

            sightings.append(sighting_details)

        return sightings

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dialog = SealSightingDialog()
    if dialog.exec_() == QDialog.Accepted:
        sightings = dialog.getSightings()
        print("Sightings:")
        for sighting in sightings:
            print(sighting)

    sys.exit(app.exec_())
