from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QPoint, QRect
from draggableItem import DraggableItem


class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.setMinimumHeight(400)
        self.items = []

        # Create main layout
        self.layout = QVBoxLayout(self)

        # Row for the Add OR and Add AND buttons (prevents overlapping)
        self.button_row = QHBoxLayout()

        # Add OR button
        self.add_or_button = QPushButton("➕ Add OR Clause")
        self.add_or_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px 30px; background-color: #4CAF50; color: white; border-radius: 10px;"
        )
        self.add_or_button.clicked.connect(self.add_or_item)

        # Add AND button
        self.add_and_button = QPushButton("➕ Add AND Clause")
        self.add_and_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px 30px; background-color: #008CBA; color: white; border-radius: 10px;"
        )
        self.add_and_button.clicked.connect(self.add_and_item)

        # Center buttons in the layout
        self.button_row.addStretch()  # Push buttons to center
        self.button_row.addWidget(self.add_or_button)
        self.button_row.addWidget(self.add_and_button)
        self.button_row.addStretch()

        # Add button row to layout
        self.layout.addLayout(self.button_row)

        # Create the canvas area where items will be added
        self.canvas_area = QWidget(self)
        self.canvas_area.setStyleSheet("background-color: white; border: 2px #555;")
        self.layout.addWidget(self.canvas_area)

    def add_or_item(self):
        new_label = DraggableItem("OR", self.canvas_area)  # Label as OR
        position = self.find_available_position(new_label)
        new_label.move(position)
        new_label.show()
        self.items.append(new_label)

    def add_and_item(self):
        new_label = DraggableItem("AND", self.canvas_area)  # Label as AND
        position = self.find_available_position(new_label)
        new_label.move(position)
        new_label.show()
        self.items.append(new_label)
        
    def add_filter_item(self, label):
        new_label = DraggableItem(label, self.canvas_area)  # Label as AND
        position = self.find_available_position(new_label)
        new_label.move(position)
        new_label.show()
        self.items.append(new_label)
        
    def find_available_position(self, new_item):
        """Find an available position that doesn't intersect with existing items."""
        spacing = 20  # Minimum spacing between items
        start_x, start_y = 50, 50  # Initial placement coordinates

        while True:
            new_rect = QRect(start_x, start_y, new_item.width(), new_item.height())
            overlapping = any(new_rect.intersects(item.geometry()) for item in self.items)

            if not overlapping:
                return QPoint(start_x, start_y)

            # Try next position horizontally, wrap to next row if out of bounds
            start_x += new_item.width() + spacing
            if start_x + new_item.width() > self.canvas_area.width():
                start_x = 50
                start_y += new_item.height() + spacing

            # Prevent infinite looping
            if start_y + new_item.height() > self.canvas_area.height():
                break

        # If no space is found, return default position
        return QPoint(50, 50)
