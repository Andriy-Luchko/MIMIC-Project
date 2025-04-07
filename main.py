import sys
import sqlite3
import yaml
import os
import pandas as pd
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                           QLabel, QFileDialog, QPushButton, QMessageBox,
                           QStackedWidget, QHBoxLayout, QCheckBox, QScrollArea,
                           QProgressBar, QGroupBox, QGridLayout, QFrame, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from create_database_button import create_database_button
from filter_search_bar import FilterSearchBar
from return_column_search_bar import ReturnColumnSearchBar
from canvas import Canvas
from mei_cleanup import mei_lifecycle
from to_spss_data import one_hot_encode_csv

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

class EncoderWorker(QObject):
    """Worker class to run one-hot encoding in a separate thread"""
    progress_updated = pyqtSignal(int)
    encoding_finished = pyqtSignal(str)
    encoding_error = pyqtSignal(str)
    
    def __init__(self, file_path, columns_to_encode, output_path=None, chunksize=10000):
        super().__init__()
        self.file_path = file_path
        self.columns_to_encode = columns_to_encode
        self.output_path = output_path
        self.chunksize = chunksize
    
    def run_encoding(self):
        """Run the encoding process in a separate thread"""
        try:
            output_path = one_hot_encode_csv(
                self.file_path,
                self.columns_to_encode,
                self.output_path,
                self.chunksize,
                self.progress_updated.emit
            )
            self.encoding_finished.emit(output_path)
        except Exception as e:
            self.encoding_error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self, width, height):
        super().__init__()
        self.setWindowTitle("MIMIC Query App")
        self.setGeometry(0, 0, width, height)

        # Initialize variables
        self.db_connection = None
        self.search_widgets = []
        self.setup_button = None  
        self.csv_file_path = None
        self.csv_columns = []
        self.column_checkboxes = {}
        self.encoding_thread = None
        self.encoding_worker = None

        # Central widget setup
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Create stacked widget to hold different pages
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        self.page1 = QWidget()
        self.page2 = QWidget()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.addWidget(self.page2)
        
        # Setup layouts for pages
        self.page1_layout = QVBoxLayout()
        self.page2_layout = QVBoxLayout()
        self.page1.setLayout(self.page1_layout)
        self.page2.setLayout(self.page2_layout)

        # Create navigation buttons
        self.nav_layout = QHBoxLayout()
        self.page1_button = QPushButton("Database Query")
        self.page2_button = QPushButton("CSV Encoder")
        
        self.page1_button.clicked.connect(self.go_to_page1)
        self.page2_button.clicked.connect(self.go_to_page2)
        
        self.nav_layout.addWidget(self.page1_button)
        self.nav_layout.addWidget(self.page2_button)
        
        # Add navigation and stacked widget to main layout
        self.main_layout.addLayout(self.nav_layout)
        self.main_layout.addWidget(self.stacked_widget)

        # Load configuration
        self.config = load_config()
        self.db_path = self.config.get("database_path", "")
        self.output_path = self.config.get("output_path", "")

        # Initialize UI for both pages
        self.setup_page1_ui()
        self.setup_page2_ui()

        # If database exists, show the main UI
        if self.db_path and os.path.exists(self.db_path):
            self.connect_database(self.db_path)
            
        # Start on page 1
        self.stacked_widget.setCurrentIndex(0)
        self.update_navigation_buttons()

    def go_to_page1(self):
        """Switch to page 1"""
        self.stacked_widget.setCurrentIndex(0)
        self.update_navigation_buttons()
        
    def go_to_page2(self):
        """Switch to page 2"""
        self.stacked_widget.setCurrentIndex(1)
        self.update_navigation_buttons()
        
    def update_navigation_buttons(self):
        """Update the navigation buttons based on current page"""
        current_index = self.stacked_widget.currentIndex()
        
        # Disable the button for the current page
        self.page1_button.setEnabled(current_index != 0)
        self.page2_button.setEnabled(current_index != 1)

    def setup_page1_ui(self):
        """Setup the initial UI with database setup buttons on page 1"""
        self.setup_button = create_database_button(self)
        self.setup_button.database_created.connect(self.on_database_created)
        self.setup_button.setFixedWidth(400)

        self.specify_db_button = QPushButton("Specify Database Path")
        self.specify_db_button.clicked.connect(self.specify_database)
        self.specify_db_button.setFixedWidth(400)

        self.specify_output_button = QPushButton("Specify Output Path")
        self.specify_output_button.clicked.connect(self.specify_output_path)
        self.specify_output_button.setFixedWidth(400)

        # Layout for buttons
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.setup_button, alignment=Qt.AlignCenter)
        button_layout.addWidget(self.specify_db_button, alignment=Qt.AlignCenter)
        button_layout.addWidget(self.specify_output_button, alignment=Qt.AlignCenter)

        # Add button layout to page 1
        self.page1_layout.addLayout(button_layout)

        if self.db_path and os.path.exists(self.db_path):
            self.setup_button.setVisible(False)

    def setup_page2_ui(self):
        """Setup the UI for page 2 - CSV One-Hot Encoder"""
        # Create main container
        encoder_container = QWidget()
        encoder_layout = QVBoxLayout()
        encoder_container.setLayout(encoder_layout)
        
        # File selection section
        file_section = QGroupBox("CSV File Selection")
        file_layout = QVBoxLayout()
        
        # File path display
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        self.file_path_display.setPlaceholderText("No CSV file selected")
        
        # File selection button
        select_file_button = QPushButton("Select CSV File")
        select_file_button.clicked.connect(self.select_csv_file)
        
        file_layout.addWidget(self.file_path_display)
        file_layout.addWidget(select_file_button, alignment=Qt.AlignLeft)
        file_section.setLayout(file_layout)
        
        # Column selection section
        self.column_section = QGroupBox("Select Columns to Encode")
        self.column_section.setEnabled(False)  # Disabled until file is loaded
        self.column_section.setFixedHeight(300)
        
        # Create scrollable area for column checkboxes
        self.column_scroll = QScrollArea()
        self.column_scroll.setWidgetResizable(True)
        self.column_scroll.setFrameShape(QFrame.NoFrame)
        
        # Container for checkboxes
        self.column_container = QWidget()
        self.column_layout = QGridLayout()
        self.column_container.setLayout(self.column_layout)
        self.column_scroll.setWidget(self.column_container)
        
        # Buttons for column selection
        column_button_layout = QHBoxLayout()
        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all_columns)
        
        deselect_all_button = QPushButton("Deselect All")
        deselect_all_button.clicked.connect(self.deselect_all_columns)
        
        column_button_layout.addWidget(select_all_button)
        column_button_layout.addWidget(deselect_all_button)
        column_button_layout.addStretch()
        
        column_section_layout = QVBoxLayout()
        column_section_layout.addLayout(column_button_layout)
        column_section_layout.addWidget(self.column_scroll)
        self.column_section.setLayout(column_section_layout)
        
        # Encoding section
        encoding_section = QGroupBox("Encoding Options")
        encoding_layout = QVBoxLayout()
        
        # Chunk size input
        chunk_layout = QHBoxLayout()
        chunk_layout.addWidget(QLabel("Chunk Size:"))
        self.chunk_size_input = QLineEdit("10000")
        self.chunk_size_input.setFixedWidth(100)
        chunk_layout.addWidget(self.chunk_size_input)
        chunk_layout.addStretch()
        
        # Output path section
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Path:"))
        self.output_path_display = QLineEdit()
        self.output_path_display.setReadOnly(True)
        self.output_path_display.setPlaceholderText("(Default: same directory as input)")
        
        output_button = QPushButton("Browse...")
        output_button.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(self.output_path_display)
        output_layout.addWidget(output_button)
        
        # Progress bar
        self.encoding_progress = QProgressBar()
        self.encoding_progress.setRange(0, 100)
        self.encoding_progress.setValue(0)
        
        # Start encoding button
        self.start_encoding_button = QPushButton("Start Encoding")
        self.start_encoding_button.clicked.connect(self.start_encoding)
        self.start_encoding_button.setEnabled(False)
        
        # Add all widgets to encoding section
        encoding_layout.addLayout(chunk_layout)
        encoding_layout.addLayout(output_layout)
        encoding_layout.addWidget(self.encoding_progress)
        encoding_layout.addWidget(self.start_encoding_button)
        encoding_section.setLayout(encoding_layout)
        
        # Status label
        self.status_label = QLabel("")
        
        # Add all sections to main layout
        encoder_layout.addWidget(file_section)
        encoder_layout.addWidget(self.column_section)
        encoder_layout.addWidget(encoding_section)
        encoder_layout.addWidget(self.status_label)
        
        # Add to page 2
        self.page2_layout.addWidget(encoder_container)
    
    def select_csv_file(self):
        """Open a file dialog to select a CSV file and load its columns"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                # Update file path
                self.csv_file_path = file_path
                self.file_path_display.setText(file_path)
                
                # Reset previous column data
                self.csv_columns = []
                self.column_checkboxes = {}
                
                # Clear the layout
                for i in reversed(range(self.column_layout.count())): 
                    self.column_layout.itemAt(i).widget().setParent(None)
                
                # Read first chunk to get column names
                self.status_label.setText("Reading CSV headers...")
                chunk = next(pd.read_csv(file_path, chunksize=5))
                self.csv_columns = list(chunk.columns)
                
                # Create checkboxes for each column
                for i, column in enumerate(self.csv_columns):
                    checkbox = QCheckBox(column)
                    self.column_checkboxes[column] = checkbox
                    row, col = divmod(i, 3)  # Arrange in 3 columns
                    self.column_layout.addWidget(checkbox, row, col)
                
                # Enable column selection
                self.column_section.setEnabled(True)
                self.start_encoding_button.setEnabled(True)
                self.status_label.setText(f"Loaded {len(self.csv_columns)} columns from {os.path.basename(file_path)}")
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "CSV Load Error",
                    f"Could not load CSV file: {str(e)}"
                )
                self.status_label.setText("Error loading CSV file")
    
    def select_all_columns(self):
        """Select all column checkboxes"""
        for checkbox in self.column_checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all_columns(self):
        """Deselect all column checkboxes"""
        for checkbox in self.column_checkboxes.values():
            checkbox.setChecked(False)
    
    def select_output_file(self):
        """Open a file dialog to select output file location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.output_path_display.setText(file_path)
    
    def start_encoding(self):
        """Start the one-hot encoding process"""
        # Get selected columns
        columns_to_encode = [col for col, checkbox in self.column_checkboxes.items() 
                            if checkbox.isChecked()]
        
        if not columns_to_encode:
            QMessageBox.warning(
                self,
                "No Columns Selected",
                "Please select at least one column to encode."
            )
            return
        
        # Get chunk size
        try:
            chunk_size = int(self.chunk_size_input.text())
            if chunk_size <= 0:
                raise ValueError("Chunk size must be positive")
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Chunk Size",
                "Please enter a valid positive number for chunk size."
            )
            return
        
        # Get output path
        output_path = self.output_path_display.text() or None
        
        # Disable controls during encoding
        self.start_encoding_button.setEnabled(False)
        self.encoding_progress.setValue(0)
        self.status_label.setText("Encoding in progress...")
        
        # Create worker and thread
        self.encoding_worker = EncoderWorker(
            self.csv_file_path,
            columns_to_encode,
            output_path,
            chunk_size
        )
        
        # Connect signals
        self.encoding_worker.progress_updated.connect(self.update_encoding_progress)
        self.encoding_worker.encoding_finished.connect(self.encoding_complete)
        self.encoding_worker.encoding_error.connect(self.encoding_error)
        
        # Create and start thread
        self.encoding_thread = threading.Thread(
            target=self.encoding_worker.run_encoding
        )
        self.encoding_thread.daemon = True
        self.encoding_thread.start()
    
    def update_encoding_progress(self, progress):
        """Update the progress bar with current progress"""
        self.encoding_progress.setValue(progress)
    
    def encoding_complete(self, output_path):
        """Handle completion of encoding process"""
        self.status_label.setText(f"Encoding complete! Output saved to: {output_path}")
        self.start_encoding_button.setEnabled(True)
        self.encoding_progress.setValue(100)
        
        QMessageBox.information(
            self,
            "Encoding Complete",
            f"One-hot encoding successfully completed.\nOutput saved to: {output_path}"
        )
    
    def encoding_error(self, error_message):
        """Handle encoding errors"""
        self.status_label.setText(f"Error: {error_message}")
        self.start_encoding_button.setEnabled(True)
        
        QMessageBox.critical(
            self,
            "Encoding Error",
            f"An error occurred during encoding:\n{error_message}"
        )

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
        """Setup the main UI with search bars and canvas on page 1"""
        # Clear previous widgets if any
        self.clear_main_ui()
        
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
        
        # Add widgets to page 1 layout
        for widget in self.search_widgets:
            self.page1_layout.addWidget(widget)
    
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