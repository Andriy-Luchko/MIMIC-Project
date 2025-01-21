from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QRect

class DraggableItem(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setText(text)
        self.setStyleSheet("background-color: white; border: 1px solid black; padding: 5px; color: black;")
        self.setFixedSize(100, 50)
        self.dragging = False
        self.offset = QPoint()
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            parent_rect = self.parent().rect()

            # Ensure the position stays within the canvas
            new_x = max(0, min(new_pos.x(), parent_rect.width() - self.width()))
            new_y = max(0, min(new_pos.y(), parent_rect.height() - self.height()))

            # Glide along intersecting objects
            adjusted_x, adjusted_y = self.adjust_position(new_x, new_y)
            self.move(adjusted_x, adjusted_y)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def adjust_position(self, x, y):
        """ Adjusts position to glide along other items smoothly. """
        for item in self.parent().children():
            if isinstance(item, DraggableItem) and item is not self:
                item_rect = item.geometry()
                new_rect = QRect(x, y, self.width(), self.height())

                if item_rect.intersects(new_rect):
                    # Determine overlap amounts
                    dx_right = item_rect.right() - new_rect.left()
                    dx_left = new_rect.right() - item_rect.left()
                    dy_bottom = item_rect.bottom() - new_rect.top()
                    dy_top = new_rect.bottom() - item_rect.top()

                    # Determine the least overlapping direction and glide along it
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

                    # Ensure the adjusted position stays within canvas bounds
                    x = max(0, min(x, self.parent().width() - self.width()))
                    y = max(0, min(y, self.parent().height() - self.height()))

        return x, y
