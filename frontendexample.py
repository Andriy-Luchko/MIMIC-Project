import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QListWidget,
    QPushButton, QLabel, QHBoxLayout, QDialog, QDialogButtonBox, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from icdQuery import fetch_patient_data

class ICDSearchApp(QMainWindow):
    def __init__(self, database_path):
        super().__init__()
        self.database_path = database_path
        self.setWindowTitle("ICD Code Selector with Autocomplete")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Type part of ICD code or long title to search...")
        self.search_bar.textChanged.connect(self.search_icd_codes)
        main_layout.addWidget(QLabel("Search ICD Codes:"))
        main_layout.addWidget(self.search_bar)

        # Search results
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
        self.central_widget.setLayout(main_layout)

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

    def add_selected_icd(self, item):
        self.selected_icd_list.addItem(item.text())

    def remove_selected_icd(self):
        selected_items = self.selected_icd_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.selected_icd_list.takeItem(self.selected_icd_list.row(item))

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

        # Replace this print statement with the actual database query
        print("Executing query with:", icd_codes_versions)
        for chunk in fetch_patient_data(DATABASE_PATH, icd_codes_versions):
            for row in chunk:
                print(row)
        QMessageBox.information(self, "Query Executed", "Query executed successfully!")

if __name__ == "__main__":
    DATABASE_PATH = "MIMIC_Database.db" 

    app = QApplication(sys.argv)
    window = ICDSearchApp(DATABASE_PATH)
    window.show()
    sys.exit(app.exec_())
