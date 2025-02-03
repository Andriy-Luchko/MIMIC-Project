from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QLabel, QWidget, QListView
from PyQt5.QtCore import Qt, QAbstractListModel, QVariant
from frontendFilterHelpers import fetch_unique_values, get_range_filters


class FilterListModel(QAbstractListModel):
    def __init__(self, items):
        super().__init__()
        self.items = items

    def rowCount(self, parent=None):
        return len(self.items)

    def data(self, index, role):
        if role == Qt.DisplayRole and index.row() < len(self.items):
            return QVariant(self.items[index.row()])
        return QVariant()


class FilterSearchBar(QWidget):
    def __init__(self, db_connection, placeholder_text="Search..."):
        super().__init__()

        # Set up the layout for the widget
        layout = QVBoxLayout(self)

        # Create the label for the filter bar
        self.filter_label = QLabel("Filter Bar", self)
        self.filter_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.filter_label)

        # Create the search bar (QLineEdit)
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText(placeholder_text)
        layout.addWidget(self.search_bar)

        # Create the list view to show the dropdown results
        self.list_view = QListView(self)
        self.list_view.setVisible(True)  # Always show the list view
        self.list_view.setFixedHeight(200)  # Set a fixed height for the list view
        layout.addWidget(self.list_view)

        # Fetch unique values from the database for filtering 
        self.items = fetch_unique_values(db_connection)
        self.items.extend(get_range_filters())
        self.model = FilterListModel(self.items)
        self.list_view.setModel(self.model)

        # Connect the textChanged signal to update the list view based on search text
        self.search_bar.textChanged.connect(self.update_list_view)

        # Connect the itemClicked signal to handle item selection
        self.list_view.clicked.connect(self.on_item_clicked)

    def update_list_view(self):
        # Get the current search text
        search_text = self.search_bar.text().lower()

        # If there's text in the search bar, filter the items
        if search_text:
            filtered_items = [
                item for item in self.items if search_text in item.lower()
            ]
        else:
            filtered_items = self.items  # Show all items if the search bar is empty

        # Limit the number of items displayed in the list (e.g., show a maximum of 25 items)
        max_items_to_show = 25
        filtered_items = filtered_items[:max_items_to_show]

        # Update the list view with the filtered items
        self.model = FilterListModel(filtered_items)
        self.list_view.setModel(self.model)
        self.model.layoutChanged.emit()  # Notify the view that the model has changed

    def on_item_clicked(self, index):
        """Handle the item click and add it to the canvas."""
        selected_item = self.model.data(index, Qt.DisplayRole)
        
        # Ensure the selected item is a string
        selected_item_str = selected_item.value() if isinstance(selected_item, QVariant) else str(selected_item)
        
        # Assuming canvas already has add_filter_item method to add a filter item
        self.canvas.add_filter_item(selected_item_str)  # Add filter item to canvas
        
