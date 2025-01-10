from PyQt5.QtWidgets import (
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QListView,
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
        self.layout = QVBoxLayout(self)

        # Search bar (QLineEdit)
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText(placeholder_text)
        self.layout.addWidget(self.search_bar)

        # Use QListView to display search results
        self.list_view = QListView(self)
        self.layout.addWidget(self.list_view)

        # Set the list view to hide initially
        self.list_view.setVisible(False)

        # Create a model for search results
        self.model = ColumnListModel(self.table_column_pairs)
        self.list_view.setModel(self.model)

        # Create a model for selected columns
        self.selected_model = ColumnListModel(self.selected_columns)
        self.selected_list_view = QListView(self)
        self.selected_list_view.setModel(self.selected_model)

        # Create a layout for selected columns
        self.selected_layout = QVBoxLayout()
        self.selected_layout.addWidget(self.selected_list_view)

        # Add the selected columns list below the search bar
        self.layout.addLayout(self.selected_layout)

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

        # Refresh the model after loading data
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
                # Hide the list view if no matches
                self.list_view.setVisible(False)
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
