import requests
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QDialog

from wildbook_util import get_gids_by_name, rename_seal


class ChangeSealDetailsDialog(QDialog):
    server_url: str

    def __init__(self, server_url):
        super().__init__()
        self.server_url = server_url
        self.setWindowTitle("Change Seal Details")

        layout = QVBoxLayout()

        old_name_label = QLabel("Old name:")
        old_name_textbox = QLineEdit()
        layout.addWidget(old_name_label)
        layout.addWidget(old_name_textbox)

        new_name_label = QLabel("New name:")
        new_name_textbox = QLineEdit()
        layout.addWidget(new_name_label)
        layout.addWidget(new_name_textbox)

        gender_label = QLabel("Gender:")
        gender_dropdown = QComboBox()
        gender_dropdown.addItems(['female', 'male', 'unknown'])
        layout.addWidget(gender_label)
        layout.addWidget(gender_dropdown)

        button = QPushButton("Submit")

        def submit():
            gid_list, nid = get_gids_by_name(self.server_url, old_name_textbox.text())

            if not nid:
                print("Name not found, no details changed")
            else:
                # change the gender for the given name
                url = f"{self.server_url}/api/name/sex"
                sex = 0 if gender_dropdown.currentText() == 'female' else 1 if gender_dropdown.currentText() == 'male' else 2
                res = requests.put(url, json={'name_rowid_list': [nid], 'name_sex_list': [sex]})
                assert res.status_code == 200
                print('Gender changed successfully for ' + old_name_textbox.text())

                if new_name_textbox.text():
                    # change the name for the given name
                    rename_seal(old_name_textbox.text(), new_name_textbox.text(), self.server_url)
                    print('Name changed successfully for ' + old_name_textbox.text())

            self.close()

        button.clicked.connect(submit)
        layout.addWidget(button)

        self.setLayout(layout)