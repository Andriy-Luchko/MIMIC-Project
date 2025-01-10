import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from createDatabaseButton import create_database_button
from filterSearchBar import FilterSearchBar
from returnColumnSearchBar import ReturnColumnSearchBar
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self, width, height):
        super().__init__()
        self.setWindowTitle("MIMIC Query App")
        self.setGeometry(0, 0, width, height)

        # Central widget setup
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create and set up the database connection (this is where your db connection should come from)
        self.db_connection = sqlite3.connect("MINI_MIMIC_Database.db")

        # Main layout
        main_layout = QVBoxLayout()

        # Add the filter search bar to the layout
        self.filter_search_bar = FilterSearchBar(self)
        main_layout.addWidget(self.filter_search_bar)

        # Add the return column search bar to the layout
        self.return_column_search_bar = ReturnColumnSearchBar(self.db_connection)
        main_layout.addWidget(self.return_column_search_bar)

        # Add the setup button to the layout
        self.setup_button = create_database_button(self)
        main_layout.addWidget(self.setup_button)

        # Set the layout to the central widget
        self.central_widget.setLayout(main_layout)

    def closeEvent(self, event):
        # Ensure to close the database connection when the app is closed
        self.db_connection.close()


def main():
    app = QApplication(sys.argv)
    screen_rect = app.desktop().screenGeometry()
    window = MainWindow(screen_rect.width(), screen_rect.height())
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
