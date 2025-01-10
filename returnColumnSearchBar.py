from PyQt5.QtWidgets import (
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QListView,
    QLabel,
)
from PyQt5.QtCore import Qt, QAbstractListModel, QVariant


class ColumnListModel(QAbstractListModel):
    def __init__(self, columns):
        super().__init__()
        self.columns = columns

    def rowCount(self, parent=None):
        return len(self.columns)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return QVariant(self.columns[index.row()])
        return QVariant()


class ReturnColumnSearchBar(QWidget):
    def __init__(self, db_connection, placeholder_text="Search..."):
        super().__init__()

        self.db_connection = db_connection
        self.table_column_pairs = []  # To store "table_name - column_name" items
        self.original_columns = []  # Store original list of columns for resetting
        self.selected_columns = []  # List of selected columns to display

        # Set up the UI components
        self.main_layout = QHBoxLayout(self)  # Main horizontal layout
        self.layout_left = QVBoxLayout()  # Layout for search bar and results
        self.layout_right = QVBoxLayout()  # Layout for selected columns

        # Set the left layout to have no margins or spacing
        self.layout_left.setContentsMargins(0, 0, 0, 0)
        self.layout_left.setSpacing(0)

        # Title for Return Column Search Bar
        self.return_column_title = QLabel("Return Column Search", self)
        self.return_column_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout_left.addWidget(
            self.return_column_title
        )  # Add title above the search bar

        # Search bar (QLineEdit)
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText(placeholder_text)
        self.layout_left.addWidget(self.search_bar)

        # Use QListView to display search results
        self.list_view = QListView(self)
        self.layout_left.addWidget(self.list_view)

        # Make sure the list view doesn't have extra margins or space above it
        self.list_view.setSpacing(0)
        self.list_view.setContentsMargins(0, 0, 0, 0)

        # Set the list view to show by default, even if empty
        self.list_view.setVisible(True)

        # Set the list view to a fixed height (adjust as needed)
        self.list_view.setFixedHeight(187)

        # Create a model for search results
        self.model = ColumnListModel(self.table_column_pairs)
        self.list_view.setModel(self.model)

        # Create a model for selected columns
        self.selected_model = ColumnListModel(self.selected_columns)
        self.selected_list_view = QListView(self)
        self.selected_list_view.setModel(self.selected_model)

        # Title for Current Return Columns
        self.current_return_columns_title = QLabel("Current Return Columns", self)
        self.current_return_columns_title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )
        self.layout_right.addWidget(
            self.current_return_columns_title
        )  # Add title above the selected columns list

        # Add the selected columns list to the right layout
        self.layout_right.addWidget(self.selected_list_view)

        # Set fixed height for the selected columns list (adjust as needed)
        self.selected_list_view.setFixedHeight(200)

        # Add both left and right layouts to the main horizontal layout
        self.main_layout.addLayout(self.layout_left)  # Search bar and results
        self.main_layout.addLayout(self.layout_right)  # Selected columns

        # Load tables and columns from the database
        self.load_tables_and_columns()

        # Connect the textChanged signal to the update function
        self.search_bar.textChanged.connect(self.update_list_view)

        # Connect the itemClicked signal to handle adding selected columns
        self.list_view.clicked.connect(self.add_to_selected_columns)

        # Connect the itemClicked signal of selected columns to handle removal
        self.selected_list_view.clicked.connect(self.remove_from_selected_columns)

    def load_tables_and_columns(self):
        # Query the database to get all tables and their columns using sqlite3
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # For each table, get the columns and format them as "table_name - column_name"
        self.original_columns = []  # Clear the original list
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for column in columns:
                column_name = column[1]
                self.original_columns.append(f"{table_name} - {column_name}")

        # Initialize the filtered list (starts as a copy of the original columns)
        self.table_column_pairs = self.original_columns[:]

        # Ensure the list view is always visible, even when empty
        self.list_view.setVisible(True)

        # Refresh the model after loading data and ensure the list is populated
        self.model = ColumnListModel(self.table_column_pairs)
        self.list_view.setModel(self.model)
        self.model.layoutChanged.emit()

    def update_list_view(self):
        # Get the current search text
        search_text = self.search_bar.text().lower()

        if search_text:
            # Filter the list based on the search text (search on table name or column name)
            filtered_items = [
                item for item in self.original_columns if search_text in item.lower()
            ]

            if filtered_items:
                # Show the list view and update its items with filtered results
                self.table_column_pairs = filtered_items
                self.model = ColumnListModel(self.table_column_pairs)
                self.list_view.setModel(self.model)
                self.model.layoutChanged.emit()
                self.list_view.setVisible(True)
            else:
                # Show the list view even if no matches
                self.table_column_pairs = []
                self.model = ColumnListModel(self.table_column_pairs)
                self.list_view.setModel(self.model)
                self.model.layoutChanged.emit()
                self.list_view.setVisible(True)
        else:
            # When search bar is empty, reset to show all items
            self.table_column_pairs = self.original_columns[:]
            self.model = ColumnListModel(self.table_column_pairs)
            self.list_view.setModel(self.model)
            self.model.layoutChanged.emit()
            self.list_view.setVisible(True)

    def add_to_selected_columns(self, index):
        # Get the clicked item (table_name - column_name)
        selected_item = self.model.data(index, Qt.DisplayRole)

        if selected_item and selected_item not in self.selected_columns:
            # Add to the selected columns list
            self.selected_columns.append(selected_item)

            # Update the selected columns model
            self.selected_model = ColumnListModel(self.selected_columns)
            self.selected_list_view.setModel(self.selected_model)
            self.selected_model.layoutChanged.emit()

    def remove_from_selected_columns(self, index):
        # Get the clicked item (table_name - column_name) to be removed
        selected_item = self.selected_model.data(index, Qt.DisplayRole)

        if selected_item in self.selected_columns:
            # Remove the item from the selected columns list
            self.selected_columns.remove(selected_item)

            # Update the selected columns model
            self.selected_model = ColumnListModel(self.selected_columns)
            self.selected_list_view.setModel(self.selected_model)
            self.selected_model.layoutChanged.emit()
