from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QPainter, QPen, QPolygon
from PyQt5.QtCore import Qt, QPoint, QRect
from draggableItem import DraggableItem

class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: lightgray; border: 1px solid black;")  # Set the background of the Canvas to light gray
        self.setMinimumHeight(400)
        self.items = []
        self.delete_mode = False
        self.connection_mode = False
        self.selected_item = None 

        self.layout = QVBoxLayout(self)
        self.button_row = QHBoxLayout()

        self.add_or_button = QPushButton("➕ Add OR Clause")
        self.add_or_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px 30px; background-color: #4CAF50; color: white; border-radius: 10px;"
        )
        self.add_or_button.clicked.connect(self.add_or_item)

        self.add_and_button = QPushButton("➕ Add AND Clause")
        self.add_and_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px 30px; background-color: #008CBA; color: white; border-radius: 10px;"
        )
        self.add_and_button.clicked.connect(self.add_and_item)

        self.connect_button = QPushButton("🔗 Connect")
        self.connect_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px 30px; background-color: #FF9800; color: white; border-radius: 10px;"
        )
        self.connect_button.clicked.connect(self.toggle_connection_mode)

        self.delete_button = QPushButton("🗑️ Delete Item")
        self.delete_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px 30px; background-color: #F44336; color: white; border-radius: 10px;"
        )
        self.delete_button.clicked.connect(self.toggle_delete_mode)
        
        self.button_row.addStretch()
        self.button_row.addWidget(self.add_or_button)
        self.button_row.addWidget(self.add_and_button)
        self.button_row.addWidget(self.connect_button)
        self.button_row.addWidget(self.delete_button)
        self.button_row.addStretch()

        self.layout.addLayout(self.button_row)

        # Create the custom CanvasArea for drawing
        self.canvas_area = CanvasArea(self)
        self.canvas_area.setStyleSheet("background-color: white; border: 2px solid #555;")  # Ensure canvas area background is white
        self.canvas_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Make it expand
        self.layout.addWidget(self.canvas_area, stretch=1)  # Add with stretch factor to take up available space
    
        
    def toggle_delete_mode(self):
        """Toggle delete mode when the button is pressed"""
        self.delete_mode = not self.delete_mode
        if self.delete_mode:
            print("Delete mode activated")
        else:
            print("Delete mode deactivated")

    def add_or_item(self):
        new_label = DraggableItem("OR", self, self.canvas_area)
        position = self.find_available_position(new_label)
        new_label.move(position)
        new_label.show()
        self.items.append(new_label)
        self.canvas_area.update()  # Ensure repaint

    def add_and_item(self):
        new_label = DraggableItem("AND", self, self.canvas_area)
        position = self.find_available_position(new_label)
        new_label.move(position)
        new_label.show()
        self.items.append(new_label)
        self.canvas_area.update()

    def toggle_connection_mode(self):
        self.connection_mode = not self.connection_mode
        if not self.connection_mode:
            self.selected_item = None  # Reset selection if exiting mode
        print(self.connection_mode)

    def handle_connection(self, item):
        """ Handles the connection between two items when in connection mode. """
        if self.selected_item is None:
            self.selected_item = item  # Select first item
        elif self.selected_item != item:
            self.selected_item.connect_to(item)  # Connect first item to second
            self.selected_item = None  # Reset selection after connecting

        self.canvas_area.update()  # Force repainting of connections
        
    def find_available_position(self, new_item):
        """Find an available position that doesn't intersect with existing items."""
        spacing = 20  # Minimum spacing between items
        start_x, start_y = 50, 50  # Initial placement coordinates

        while True:
            new_rect = QRect(start_x, start_y, new_item.width(), new_item.height())
            overlapping = any(new_rect.intersects(item.geometry()) for item in self.items)

            if not overlapping and new_rect.right() <= self.canvas_area.width() and new_rect.bottom() <= self.canvas_area.height():
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
    
    def add_filter_item(self, label):
        new_label = DraggableItem(label, self, self.canvas_area)  # Label as AND
        position = self.find_available_position(new_label)
        new_label.move(position)
        new_label.show()
        self.items.append(new_label)
        
    def delete_item(self, item):
        """Delete the item from the canvas."""
        # Check if the item is in the list before trying to remove it
        if item in self.items:
            print(f"Deleting item: {item}")  # Debugging: confirm deletion
            self.items.remove(item)  # Remove it from the parent items list
            
            item.close()  # Close the widget
            item.deleteLater()  # Clean up the widget
            
            self.canvas_area.update()  # Force a repaint after deletion
        else:
            print("Item not found in the list.")  # Debugging: item was not found


class CanvasArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white; border: 2px solid #555;")  # Ensure canvas area background is white
        self.setVisible(True)  # Ensure the widget is visible
        self.raise_()
        self.update()  # Force a repaint

    def paintEvent(self, event):
        """ Explicitly draw the background color and any other items. """
        painter = QPainter(self)
        
        # Clear the background with white color
        painter.fillRect(self.rect(), Qt.white)  # Fill with white background
        painter.setPen(QPen(Qt.black, 2))

        # Now draw the connections or items
        for item in self.parent().items:
            print(f"Painting item: {item}")  # Debugging: confirm which items are being drawn
            if item.parent_item:
                # Get the center positions of both items
                start = item.parent_item.rect().center()
                end = item.rect().center()

                # Map these positions to the canvas area
                start = self.mapFromParent(item.parent_item.mapToParent(start))
                end = self.mapFromParent(item.mapToParent(end))

                # Optional: Adjust the offset to ensure the arrow connects at the right spot
                start.setY(start.y() + 70)
                end.setY(end.y() + 70)
                
                start.setX(start.x() + 20)
                end.setX(end.x() + 20)

                # Draw the line between the two items
                painter.drawLine(start, end)

                # Draw arrowhead
                self.draw_arrowhead(painter, start, end)

        painter.end()
        
    def removeItem(self, item):
        """Remove the item from the canvas area."""
        if item in self.parent().items:
            self.parent().items.remove(item)
            item.deleteLater()  # Clean up the widget
            self.update()  # Force a repaint

    def draw_arrowhead(self, painter, start, end):
        """Draws an arrowhead at the end of the line from start to end."""
        arrow_size = 20

        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = (dx**2 + dy**2) ** 0.5

        if length == 0:
            return

        unit_dx = dx / length
        unit_dy = dy / length

        arrow_p1 = QPoint(
            end.x() - int(arrow_size * (unit_dx - unit_dy)),
            end.y() - int(arrow_size * (unit_dy + unit_dx))
        )
        arrow_p2 = QPoint(
            end.x() - int(arrow_size * (unit_dx + unit_dy)),
            end.y() - int(arrow_size * (unit_dy - unit_dx))
        )

        arrowhead = QPolygon([end, arrow_p1, arrow_p2])
        painter.setBrush(Qt.black)
        painter.drawPolygon(arrowhead)