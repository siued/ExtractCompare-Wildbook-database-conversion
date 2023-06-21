from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QDialog

from wildbook_util import change_gender, get_gids_by_name, rename_seal


class ChangeSealDetailsDialog(QDialog):
    server_url: str

    def __init__(self, server_url):
        super().__init__()

        font = self.font()
        font.setPointSize(18)
        self.setFont(font)

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

        name_button = QPushButton("Change Name")

        def submit_name():
            gid_list, nid = get_gids_by_name(self.server_url, old_name_textbox.text())

            if not nid:
                print("Name not found, no details changed")
            elif new_name_textbox.text() != '':
                # change the name for the given name
                rename_seal(old_name_textbox.text(), new_name_textbox.text(), self.server_url)
                print(f'Name changed successfully from {old_name_textbox.text()} to {new_name_textbox.text()}')

            self.close()

        name_button.clicked.connect(submit_name)
        layout.addWidget(name_button)

        gender_label = QLabel("Gender:")
        gender_dropdown = QComboBox()
        gender_dropdown.addItems(['female', 'male', 'unknown'])
        layout.addWidget(gender_label)
        layout.addWidget(gender_dropdown)

        gender_button = QPushButton("Change gender")

        def submit_gender():
            gid_list, nid = get_gids_by_name(self.server_url, old_name_textbox.text())

            if not nid:
                print("Name not found, no details changed")
            else:
                # change the gender for the given name
                change_gender(nid, self.server_url, gender_dropdown.currentText())
                print(f'Gender changed to {gender_dropdown.currentText()} for {old_name_textbox.text()}')

            self.close()

        gender_button.clicked.connect(submit_gender)
        layout.addWidget(gender_button)

        self.setLayout(layout)
