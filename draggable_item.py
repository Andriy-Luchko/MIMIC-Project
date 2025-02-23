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
        self.low_input = QLineEdit(self)
        self.high_input = QLineEdit(self)

        self.low_input.setPlaceholderText("Low")
        self.high_input.setPlaceholderText("High")

        self.low_input.setStyleSheet("background-color: white; border: 1px solid black; padding: 2px;")
        self.high_input.setStyleSheet("background-color: white; border: 1px solid black; padding: 2px;")

        input_width = 50
        input_height = 20
        self.low_input.setFixedSize(input_width, input_height)
        self.high_input.setFixedSize(input_width, input_height)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addSpacerItem(spacer)

        layout.addWidget(self.low_input)
        layout.addWidget(self.high_input)

        self.adjust_size_for_inputs(input_width, input_height)

    def adjust_size_for_inputs(self, input_width, input_height):
        """ Adjust the size of the DraggableItem to fit the inputs and text. """
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.horizontalAdvance(self.text()) + 15
        text_height = font_metrics.height() + 10

        total_width = text_width + 2 * input_width + 20
        total_height = max(text_height, input_height) + 10

        self.setFixedSize(total_width, total_height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.canvas.mark_root_mode:
                self.canvas.mark_query_root(self)
            elif self.canvas.connection_mode:  
                self.canvas.handle_connection(self)
            elif self.canvas.delete_mode:
                for child in self.children_items:
                    child.parent_item = None
                self.canvas.delete_item(self)
            else:
                self.dragging = True
                self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            self.move(new_pos)
            self.canvas.canvas_area.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.canvas.canvas_area.update()

    def connect_to(self, other_item):
        """ Creates a parent-child relationship between self and other_item. """
        if other_item not in self.children_items:
            self.children_items.append(other_item)
            other_item.parent_item = self
            self.canvas.canvas_area.update()

    def adjust_size_based_on_text(self, text):
        """ Adjust the size of the label based on the text length. """
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.horizontalAdvance(text) + 15
        text_height = font_metrics.height() + 10
        self.setFixedSize(text_width, text_height)