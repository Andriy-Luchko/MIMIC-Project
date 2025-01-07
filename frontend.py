import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QListWidget,
    QPushButton, QLabel, QHBoxLayout, QDialog, QWidget, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from icdQuery import fetch_patient_data
from csvToDatabase import create_database  # Assuming this function is in the csvToDatabase.py file


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
        
class MIMICApp(QMainWindow):
    def __init__(self, database_path):
        super().__init__()
        self.database_path = database_path
        self.setWindowTitle("ICD Code Selector with Autocomplete")
        self.setGeometry(100, 100, 1200, 900)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Search bar for ICD codes
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Type part of ICD code or long title to search...")
        self.search_bar.textChanged.connect(self.search_icd_codes)
        main_layout.addWidget(QLabel("Search ICD Codes:"))
        main_layout.addWidget(self.search_bar)

        # Search results for ICD codes
        self.search_results = QListWidget()
        self.search_results.itemDoubleClicked.connect(self.add_selected_icd)
        main_layout.addWidget(QLabel("Search Results (Double-click to select):"))
        main_layout.addWidget(self.search_results)

        # Selected ICD codes
        self.selected_icd_list = QListWidget()
        main_layout.addWidget(QLabel("Selected ICD Codes:"))
        main_layout.addWidget(self.selected_icd_list)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Remove button
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_icd)
        buttons_layout.addWidget(self.remove_button)

        # Run query button
        self.run_query_button = QPushButton("Run Query")
        self.run_query_button.clicked.connect(self.run_query)
        buttons_layout.addWidget(self.run_query_button)

        main_layout.addLayout(buttons_layout)

        # Setup database button
        self.setup_button = QPushButton("Setup Database")
        self.setup_button.clicked.connect(self.open_directory_dialog)
        main_layout.addWidget(self.setup_button)

        # Search bar for columns
        self.column_search_bar = QLineEdit()
        self.column_search_bar.setPlaceholderText("Search for columns (tablename:columnname)...")
        self.column_search_bar.textChanged.connect(self.search_columns)
        main_layout.addWidget(QLabel("Search for Columns:"))
        main_layout.addWidget(self.column_search_bar)

        # Search results for columns
        self.column_search_results = QListWidget()
        self.column_search_results.itemDoubleClicked.connect(self.add_selected_column)
        main_layout.addWidget(QLabel("Select Columns (Double-click to add):"))
        main_layout.addWidget(self.column_search_results)

        # Selected columns
        self.selected_columns_list = QListWidget()
        main_layout.addWidget(QLabel("Selected Columns:"))
        main_layout.addWidget(self.selected_columns_list)

        self.central_widget.setLayout(main_layout)

        # Fetch available tables and columns
        self.tables_columns = self.get_table_columns()
        print(self.tables_columns)
        # Get additional columns
        self.tables_columns.update(self.get_derived_table_columns())

    def get_table_columns(self):
        """Fetch available columns for each table from the database."""
        table_columns = {}

        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            # Get the table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                # Get the column names for each table
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = [f"{table_name}:{column[1]}" for column in cursor.fetchall()]
                table_columns[table_name] = columns

            conn.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

        return table_columns
    
    def get_derived_table_columns(self):
        derived = {'derived': ["derived:death_flag"]}
        return derived

    def search_icd_codes(self, query):
        query = query.strip()
        if not query:
            self.search_results.clear()
            return

        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT icd_code, icd_version, long_title 
                FROM d_icd_diagnoses 
                WHERE icd_code LIKE ? OR long_title LIKE ?
                """,
                (f"%{query}%", f"%{query}%")
            )
            results = cursor.fetchall()
            conn.close()

            self.search_results.clear()
            for icd_code, icd_version, long_title in results:
                self.search_results.addItem(f"{icd_code} (Version {icd_version}): {long_title}")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    def search_columns(self, query):
        """Search for columns across tables based on the input query."""
        query = query.strip()
        if not query:
            self.column_search_results.clear()
            return

        matching_columns = []
        for table, columns in self.tables_columns.items():
            matching_columns.extend([col for col in columns if query.lower() in col.lower()])

        self.column_search_results.clear()
        self.column_search_results.addItems(matching_columns)

    def add_selected_icd(self, item):
        self.selected_icd_list.addItem(item.text())

    def remove_selected_icd(self):
        selected_items = self.selected_icd_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.selected_icd_list.takeItem(self.selected_icd_list.row(item))

    def add_selected_column(self, item):
        self.selected_columns_list.addItem(item.text())

    def run_query(self):
        icd_codes_versions = []
        for i in range(self.selected_icd_list.count()):
            item_text = self.selected_icd_list.item(i).text()
            icd_code, rest = item_text.split(" (Version ")
            icd_version = int(rest.split("):")[0])
            icd_codes_versions.append((icd_code, icd_version))

        if not icd_codes_versions:
            QMessageBox.warning(self, "No Codes Selected", "Please add at least one ICD code before running the query.")
            return

        # Gather selected columns
        selected_columns = [self.selected_columns_list.item(i).text() for i in range(self.selected_columns_list.count())]

        if not selected_columns:
            QMessageBox.warning(self, "No Columns Selected", "Please select at least one column to include in the query.")
            return
        print("selected columns")
        selected_columns = [item.split(":") for item in selected_columns]
        selected_columns = [(item[0], item[1]) for item in selected_columns]
        print(selected_columns)
        # Execute the query
        for chunk in fetch_patient_data(self.database_path, icd_codes_versions, selected_columns):
            for row in chunk:
                print(row)

        QMessageBox.information(self, "Query Executed", "Query executed successfully!")

    def open_directory_dialog(self):
        directory_path = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        if directory_path:
            self.create_loading_dialog(directory_path)

    def create_loading_dialog(self, path_to_data):
        # Create a loading dialog
        loading_dialog = QDialog(self)
        loading_dialog.setWindowTitle("Creating Database")
        loading_dialog.setModal(True)  # Make the dialog modal (blocks interaction with the main window)

        # Set up layout for the loading dialog
        layout = QVBoxLayout()
        message_label = QLabel("Creating database... Please wait.")
        layout.addWidget(message_label)
        
        # You can also add a progress bar or a spinning wheel, but for simplicity, it's just a message
        loading_dialog.setLayout(layout)

        # Start the database creation process in a separate thread
        self.db_thread = DatabaseCreationThread(path_to_data)
        self.db_thread.task_done.connect(loading_dialog.accept)  # Close the dialog when done
        self.db_thread.start()

        # Show the loading dialog
        loading_dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MIMICApp("MINI_MIMIC_Database.db")
    window.show()
    sys.exit(app.exec_())
