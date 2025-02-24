import sys
import sqlite3
import yaml
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                           QLabel, QFileDialog, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from create_database_button import create_database_button
from filter_search_bar import FilterSearchBar
from return_column_search_bar import ReturnColumnSearchBar
from canvas import Canvas
from mei_cleanup import mei_lifecycle

def get_config_path():
    """Get the path for the config.yaml file inside the PyInstaller dist folder."""
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
        base_path = sys._MEIPASS  # PyInstaller temp directory
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))  # Normal script execution

    return os.path.join(base_path, "config.yaml")

def load_config():
    """Load configuration from config.yaml inside the PyInstaller dist folder."""
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            return yaml.safe_load(file) or {}
    return {}

def save_config(config):
    """Save configuration to config.yaml inside the PyInstaller dist folder."""
    config_path = get_config_path()
    with open(config_path, "w") as file:
        yaml.dump(config, file)

class MainWindow(QMainWindow):
    def __init__(self, width, height):
        super().__init__()
        self.setWindowTitle("MIMIC Query App")
        self.setGeometry(0, 0, width, height)

        # Initialize variables
        self.db_connection = None
        self.search_widgets = []
        self.setup_button = None  

        # Central widget setup
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Load configuration
        self.config = load_config()
        self.db_path = self.config.get("database_path", "")
        self.output_path = self.config.get("output_path", "")

        # Initialize UI
        self.setup_initial_ui()

        # If database exists, show the main UI
        if self.db_path and os.path.exists(self.db_path):
            self.connect_database(self.db_path)

    def setup_initial_ui(self):
        """Setup the initial UI with database setup buttons"""
        self.setup_button = create_database_button(self)
        self.setup_button.database_created.connect(self.on_database_created)
        self.setup_button.setFixedWidth(400)

        self.specify_db_button = QPushButton("Specify Database Path")
        self.specify_db_button.clicked.connect(self.specify_database)
        self.specify_db_button.setFixedWidth(400)

        self.specify_output_button = QPushButton("Specify Output Path")  # New button
        self.specify_output_button.clicked.connect(self.specify_output_path)
        self.specify_output_button.setFixedWidth(400)

        # Layout for buttons
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.setup_button, alignment=Qt.AlignCenter)
        button_layout.addWidget(self.specify_db_button, alignment=Qt.AlignCenter)
        button_layout.addWidget(self.specify_output_button, alignment=Qt.AlignCenter)  # Add new button

        self.main_layout.addLayout(button_layout)

        if self.db_path and os.path.exists(self.db_path):
            self.setup_button.setVisible(False)

    def specify_output_path(self):
        """Open dialog to select output directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            ""
        )
        if directory:
            self.output_path = directory
            self.config["output_path"] = directory
            save_config(self.config)
    
    def on_database_created(self, db_path):
        """Handle database creation signal"""
        self.db_path = db_path
        self.config["database_path"] = db_path
        save_config(self.config)  # Save the new database path to config
        self.connect_database(db_path)  # Connect to the new database
        self.setup_button.setVisible(False)  # Hide the button after database creation
    
    def setup_main_ui(self):
        """Setup the main UI with search bars and canvas"""
        # Create search bars and canvas
        self.return_column_search_bar = ReturnColumnSearchBar(self.db_connection)
        self.return_column_search_bar.setFixedHeight(250)
        
        self.filter_search_bar = FilterSearchBar(self.db_connection)
        self.filter_search_bar.setFixedHeight(250)
        
        self.draggable_canvas = Canvas(self)
        self.filter_search_bar.canvas = self.draggable_canvas
        
        # Store widgets for easy removal
        self.search_widgets = [
            self.return_column_search_bar,
            self.filter_search_bar,
            self.draggable_canvas
        ]
        
        # Add widgets to layout
        for widget in self.search_widgets:
            self.main_layout.addWidget(widget)
    
    def clear_main_ui(self):
        """Clear the main UI components"""
        if hasattr(self, 'search_widgets'):
            for widget in self.search_widgets:
                widget.setParent(None)
                widget.deleteLater()
            self.search_widgets = []
    
    def specify_database(self):
        """Open file dialog to specify database path"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Database File",
            "",
            "SQLite Database Files (*.db);;All Files (*)"
        )
        
        if file_path:
            self.connect_database(file_path)
            self.setup_button.setVisible(False)  # Hide the button after specifying a new database
    
    def connect_database(self, db_path):
        """Connect to the database and update UI"""
        try:
            # Close existing connection if any
            if self.db_connection:
                self.db_connection.close()
            
            # Try to connect to the database
            self.db_connection = sqlite3.connect(db_path)
            
            # Update config
            self.db_path = db_path
            self.config["database_path"] = db_path
            save_config(self.config)
            
            # Update UI
            self.clear_main_ui()
            self.setup_main_ui()
            
        except sqlite3.Error as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not connect to database: {str(e)}"
            )
    
    def closeEvent(self, event):
        """Handle application closing"""
        if self.db_connection:
            self.db_connection.close()
        event.accept()

def main():
    mei_lifecycle()
    app = QApplication(sys.argv)
    screen_rect = app.desktop().screenGeometry()
    window = MainWindow(screen_rect.width(), screen_rect.height())
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()