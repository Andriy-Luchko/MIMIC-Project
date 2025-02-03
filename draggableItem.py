from PyQt5.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QFontMetrics

class DraggableItem(QLabel):
    def __init__(self, text, canvas, parent=None, is_range=False):
        super().__init__(text, parent)
        self.is_range = is_range
        self.setText(text)
        self.setStyleSheet("background-color: white; border: 1px solid black; padding: 0px; color: black;")

        self.adjust_size_based_on_text(text)
        self.dragging = False
        self.offset = QPoint()
        self.parent_item = None  # Item pointing to us
        self.children_items = []  # Items we point to
        self.canvas = canvas

        if self.is_range:
            self.setup_range_inputs()

        self.show()

    def setup_range_inputs(self):
        """ Setup QLineEdit widgets for low and high values if the item is a range item. """
        # Create QLineEdit widgets for low and high values
        self.low_input = QLineEdit(self)
        self.high_input = QLineEdit(self)

        self.low_input.setPlaceholderText("Low")
        self.high_input.setPlaceholderText("High")

        # Set styles for the inputs
        self.low_input.setStyleSheet("background-color: white; border: 1px solid black; padding: 2px;")
        self.high_input.setStyleSheet("background-color: white; border: 1px solid black; padding: 2px;")

        # Set fixed size for the inputs
        input_width = 50
        input_height = 20
        self.low_input.setFixedSize(input_width, input_height)
        self.high_input.setFixedSize(input_width, input_height)

        # Create a layout to hold the inputs
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Add margins to the layout
        layout.setSpacing(5)  # Add spacing between the inputs

        # Add a spacer to push the inputs to the right
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addSpacerItem(spacer)

        # Add the inputs to the layout
        layout.addWidget(self.low_input)
        layout.addWidget(self.high_input)

        # Adjust the size of the DraggableItem to accommodate the inputs
        self.adjust_size_for_inputs(input_width, input_height)

    def adjust_size_for_inputs(self, input_width, input_height):
        """ Adjust the size of the DraggableItem to fit the inputs and text. """
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.horizontalAdvance(self.text()) + 10  # Add padding
        text_height = font_metrics.height() + 10  # Add padding

        # Calculate the total width and height needed
        total_width = text_width + 2 * input_width + 20  # Add spacing and margins
        total_height = max(text_height, input_height) + 10  # Ensure enough height

        self.setFixedSize(total_width, total_height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.canvas.connection_mode:  
                self.canvas.handle_connection(self)
            elif self.canvas.delete_mode:  # Check if delete mode is active
                for child in self.children_items:
                    child.parent_item = None
                self.canvas.delete_item(self)  # Delete the item
            else:
                self.dragging = True
                self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            self.move(new_pos)
            self.canvas.canvas_area.update()  # Update connections

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.canvas.canvas_area.update()  # Update when movement stops

    def connect_to(self, other_item):
        """ Creates a parent-child relationship between self and other_item. """
        if other_item not in self.children_items:
            self.children_items.append(other_item)
            other_item.parent_item = self
            self.canvas.canvas_area.update()  # Ensure the canvas updates

    def adjust_size_based_on_text(self, text):
        """ Adjust the size of the label based on the text length """
        font_metrics = QFontMetrics(self.font())  
        text_width = font_metrics.horizontalAdvance(text) + 10  # Add padding
        text_height = font_metrics.height() + 10  # Add padding
        self.setFixedSize(text_width, text_height)  

    def adjust_position(self, x, y):
        """ Adjusts position to glide along other items smoothly. """
        for item in self.parent().children():
            if isinstance(item, DraggableItem) and item is not self:
                item_rect = item.geometry()
                new_rect = QRect(x, y, self.width(), self.height())

                if item_rect.intersects(new_rect):
                    dx_right = item_rect.right() - new_rect.left()
                    dx_left = new_rect.right() - item_rect.left()
                    dy_bottom = item_rect.bottom() - new_rect.top()
                    dy_top = new_rect.bottom() - item_rect.top()

                    overlap_values = {
                        "right": abs(dx_right),
                        "left": abs(dx_left),
                        "bottom": abs(dy_bottom),
                        "top": abs(dy_top)
                    }
                    min_overlap_side = min(overlap_values, key=overlap_values.get)

                    if min_overlap_side == "right":
                        x = item_rect.right() + 1
                    elif min_overlap_side == "left":
                        x = item_rect.left() - self.width() - 1
                    elif min_overlap_side == "bottom":
                        y = item_rect.bottom() + 1
                    elif min_overlap_side == "top":
                        y = item_rect.top() - self.height() - 1

                    x = max(0, min(x, self.parent().width() - self.width()))
                    y = max(0, min(y, self.parent().height() - self.height()))

        return x, y