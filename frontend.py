import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from createDatabaseButton import create_database_button


class MainWindow(QMainWindow):
    def __init__(self, width, height):
        super().__init__()
        self.setWindowTitle("MIMIC Query App")
        self.setGeometry(0, 0, width, height)

        # Central widget setup
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Add the database setup button
        self.setup_button = create_database_button(self)
        main_layout.addWidget(self.setup_button)

        # Set the layout to the central widget
        self.central_widget.setLayout(main_layout)


def main():
    app = QApplication(sys.argv)
    screen_rect = app.desktop().screenGeometry()
    window = MainWindow(screen_rect.width(), screen_rect.height())
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
