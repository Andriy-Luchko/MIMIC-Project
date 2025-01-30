from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QFontMetrics

class DraggableItem(QLabel):
    def __init__(self, text, canvas, parent=None):
        super().__init__(text, parent)
        self.setText(text)
        self.setStyleSheet("background-color: white; border: 1px solid black; padding: 5px; color: black;")

        self.adjust_size_based_on_text(text)
        self.dragging = False
        self.offset = QPoint()
        self.parent_item = None  # Item pointing to us
        self.children_items = []  # Items we point to
        self.canvas = canvas
        self.show()

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
        text_width = font_metrics.horizontalAdvance(text) + 5 
        text_height = font_metrics.height()  
        self.setFixedSize(text_width + 10, text_height + 10)  

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
