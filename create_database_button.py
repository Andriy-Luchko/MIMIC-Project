import os
from PyQt5.QtWidgets import QPushButton, QFileDialog, QDialog, QLabel, QVBoxLayout, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal
from csv_to_database import create_database

class DatabaseCreationThread(QThread):
    task_done = pyqtSignal(str)  # Emit the path to the created database
    progress_updated = pyqtSignal(int)  # Emit progress updates

    def __init__(self, path_to_data):
        super().__init__()
        self.path_to_data = path_to_data

    def run(self):
        db_path = create_database(self.path_to_data, self.progress_updated)  # Pass the progress signal
        self.task_done.emit(db_path)

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

        # Add a progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)

        self.loading_dialog.setLayout(layout)

        # Start the database creation process in a separate thread
        self.db_thread = DatabaseCreationThread(path_to_data)
        self.db_thread.task_done.connect(self.on_database_created)  # Connect to the task_done signal
        self.db_thread.progress_updated.connect(self.update_progress)  # Connect to the progress_updated signal
        self.db_thread.start()

        # Show the loading dialog
        self.loading_dialog.exec_()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_database_created(self, db_path):
        # Close the loading dialog
        self.loading_dialog.accept()
        # Notify the parent (MainWindow) that the database has been created and pass the path
        self.database_created.emit(db_path)


def create_database_button(parent=None):
    return DatabaseButton(parent)