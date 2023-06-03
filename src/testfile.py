import json
import requests
import docker
import time

# this is a testing file where I run code which only needs to be run once or just tested once and does not need to be
# documented

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar
import time

# Create the main application instance
app = QApplication([])

# Create the main widget
main_widget = QWidget()

# Create a layout for the main widget
main_layout = QVBoxLayout(main_widget)

# Create a loading bar
loading_bar = QProgressBar()
loading_bar.setRange(0, 0)  # Set the range to make it an indeterminate progress bar

# Add the loading bar to the layout
main_layout.addWidget(loading_bar)

# Show the main widget
main_widget.show()

# Function that performs a time-consuming task
def performTask():
    # Simulate a time-consuming task
    for i in range(5):
        time.sleep(1)
        QApplication.processEvents()



# Call the function that performs the task
performTask()

# Run the application's main event loop
app.exec_()
