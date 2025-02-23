import os
from PyQt5.QtWidgets import QPushButton, QFileDialog, QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
from csv_to_database import create_database

class DatabaseCreationThread(QThread):
    # Signal to indicate the task is done
    task_done = pyqtSignal()

    def __init__(self, path_to_data):
        super().__init__()
        self.path_to_data = path_to_data

    def run(self):
        # Perform the database creation task
        create_database(self.path_to_data)
        self.task_done.emit()  # Signal that the task is done

class DatabaseButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("Select Folder to Setup Database", parent)

        # Check if the database file exists and manage button visibility
        if os.path.exists("MINI_MIMIC_Database.db"):
            self.setVisible(False)  # Hide the button if the file exists
        else:
            self.clicked.connect(self.open_directory_dialog)

    def open_directory_dialog(self):
        directory_path = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        if directory_path:
            self.create_loading_dialog(directory_path)

    def create_loading_dialog(self, path_to_data):
        # Create a loading dialog
        self.loading_dialog = QDialog(self)
        self.loading_dialog.setWindowTitle("Creating Database")
        self.loading_dialog.setModal(
            True
        )  # Make the dialog modal (blocks interaction with the main window)

        # Set up layout for the loading dialog
        layout = QVBoxLayout()
        message_label = QLabel("Creating database... Please wait.")
        layout.addWidget(message_label)

        self.loading_dialog.setLayout(layout)

        # Start the database creation process in a separate thread
        self.db_thread = DatabaseCreationThread(path_to_data)
        self.db_thread.task_done.connect(
            self.on_database_created
        )  # Hide the button and close the dialog when done
        self.db_thread.start()

        # Show the loading dialog
        self.loading_dialog.exec_()

    def on_database_created(self):
        # Hide the button after database creation
        self.setVisible(False)
        # Close the loading dialog
        self.loading_dialog.accept()


def create_database_button(parent=None):
    return DatabaseButton(parent)
