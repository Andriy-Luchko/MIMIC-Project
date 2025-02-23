import os
from PyQt5.QtWidgets import QPushButton, QFileDialog, QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
from csv_to_database import create_database

class DatabaseCreationThread(QThread):
    # Signal to indicate the task is done and return the database path
    task_done = pyqtSignal(str)  # Emit the path to the created database

    def __init__(self, path_to_data):
        super().__init__()
        self.path_to_data = path_to_data

    def run(self):
        # Perform the database creation task
        db_path = create_database(self.path_to_data)  # Ensure this function returns the database path
        self.task_done.emit(db_path)  # Signal that the task is done and pass the database path

class DatabaseButton(QPushButton):
    # Signal to notify when the database is created and return its path
    database_created = pyqtSignal(str)  # Emit the path to the created database

    def __init__(self, parent=None):
        super().__init__("Select Folder to Setup Database", parent)
        self.parent = parent  # Store a reference to the parent (MainWindow)
        self.clicked.connect(self.open_directory_dialog)

    def open_directory_dialog(self):
        directory_path = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        if directory_path:
            self.create_loading_dialog(directory_path)

    def create_loading_dialog(self, path_to_data):
        # Create a loading dialog
        self.loading_dialog = QDialog(self)
        self.loading_dialog.setWindowTitle("Creating Database")
        self.loading_dialog.setModal(True)  # Make the dialog modal

        # Set up layout for the loading dialog
        layout = QVBoxLayout()
        message_label = QLabel("Creating database... Please wait.")
        layout.addWidget(message_label)

        self.loading_dialog.setLayout(layout)

        # Start the database creation process in a separate thread
        self.db_thread = DatabaseCreationThread(path_to_data)
        self.db_thread.task_done.connect(self.on_database_created)  # Connect to the task_done signal
        self.db_thread.start()

        # Show the loading dialog
        self.loading_dialog.exec_()

    def on_database_created(self, db_path):
        # Close the loading dialog
        self.loading_dialog.accept()
        # Notify the parent (MainWindow) that the database has been created and pass the path
        self.database_created.emit(db_path)


def create_database_button(parent=None):
    return DatabaseButton(parent)