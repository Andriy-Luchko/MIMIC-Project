from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QPainter, QPen, QPolygon
from PyQt5.QtCore import Qt, QPoint, QRect
from draggableItem import DraggableItem
from subquery import Subquery, EqualityFilter, RangeFilter, ReadmissionFilter
from query import Query

class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.setMinimumHeight(400)
        self.items = []
        self.delete_mode = False
        self.connection_mode = False
        self.mark_root_mode = False
        self.selected_item = None 
        self.query_root = None

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

        self.mark_root_button = QPushButton("⭐ Mark Query Root")
        self.mark_root_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px 30px; background-color: #9C27B0; color: white; border-radius: 10px;"
        )
        self.mark_root_button.clicked.connect(self.toggle_mark_root_mode)

        # New button for printing the query
        self.print_query_button = QPushButton("🖨️ Print Query")
        self.print_query_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px 30px; background-color: #607D8B; color: white; border-radius: 10px;"
        )
        self.print_query_button.clicked.connect(self.print_query)
        
        self.button_row.addStretch()
        self.button_row.addWidget(self.add_or_button)
        self.button_row.addWidget(self.add_and_button)
        self.button_row.addWidget(self.connect_button)
        self.button_row.addWidget(self.delete_button)
        self.button_row.addWidget(self.mark_root_button)
        self.button_row.addWidget(self.print_query_button)  # Add the new button
        self.button_row.addStretch()

        self.layout.addLayout(self.button_row)

        self.canvas_area = CanvasArea(self)
        self.canvas_area.setStyleSheet("background-color: white; border: 2px solid #555;")
        self.canvas_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.canvas_area, stretch=1)

        self.setCursor(Qt.ArrowCursor)

    def toggle_delete_mode(self):
        self.delete_mode = not self.delete_mode
        if self.delete_mode:
            self.setCursor(Qt.ForbiddenCursor)
            self.connection_mode = False
            self.mark_root_mode = False
        else:
            self.setCursor(Qt.ArrowCursor)

    def toggle_connection_mode(self):
        self.connection_mode = not self.connection_mode
        if self.connection_mode:
            self.setCursor(Qt.CrossCursor)
            self.delete_mode = False
            self.mark_root_mode = False
        else:
            self.setCursor(Qt.ArrowCursor)
            self.selected_item = None

    def toggle_mark_root_mode(self):
        self.mark_root_mode = not self.mark_root_mode
        if self.mark_root_mode:
            self.setCursor(Qt.PointingHandCursor)
            self.delete_mode = False
            self.connection_mode = False
        else:
            self.setCursor(Qt.ArrowCursor)

    def add_or_item(self):
        new_label = DraggableItem("OR", self, self.canvas_area)
        position = self.find_available_position(new_label)
        new_label.move(position)
        new_label.show()
        self.items.append(new_label)
        self.canvas_area.update()

    def add_and_item(self):
        new_label = DraggableItem("AND", self, self.canvas_area)
        position = self.find_available_position(new_label)
        new_label.move(position)
        new_label.show()
        self.items.append(new_label)
        self.canvas_area.update()

    def add_filter_item(self, label):
        is_range = label.endswith("range")
        new_label = DraggableItem(label, self, self.canvas_area, is_range=is_range)
        position = self.find_available_position(new_label)
        new_label.move(position)
        new_label.show()
        self.items.append(new_label)

    def handle_connection(self, item):
        if self.selected_item is None:
            self.selected_item = item
        elif self.selected_item != item:
            self.selected_item.connect_to(item)
            self.selected_item = None

        self.canvas_area.update()

    def mark_query_root(self, item):
        if self.query_root and self.query_root in self.items:  # Check if query_root exists
            self.query_root.setStyleSheet("background-color: white; border: 1px solid black; padding: 5px; color: black;")
        
        self.query_root = item
        self.query_root.setStyleSheet("background-color: white; border: 3px solid #FFD700; padding: 5px; color: black;")
        print(f"Query root set to: {item.text()}")

    def find_available_position(self, new_item):
        spacing = 20
        start_x, start_y = 50, 50

        while True:
            new_rect = QRect(start_x, start_y, new_item.width(), new_item.height())
            overlapping = any(new_rect.intersects(item.geometry()) for item in self.items)

            if not overlapping and new_rect.right() <= self.canvas_area.width() and new_rect.bottom() <= self.canvas_area.height():
                return QPoint(start_x, start_y)

            start_x += new_item.width() + spacing
            if start_x + new_item.width() > self.canvas_area.width():
                start_x = 50
                start_y += new_item.height() + spacing

            if start_y + new_item.height() > self.canvas_area.height():
                break

        return QPoint(50, 50)
    
    def delete_item(self, item):
        if item in self.items:
            print(f"Deleting item: {item}")
            self.items.remove(item)
            item.close()
            item.deleteLater()

            # Clear query_root if the deleted item was the query root
            if item == self.query_root:
                self.query_root = None

            self.canvas_area.update()

    def print_query(self):
        """
        Parses the query structure starting from the root query, builds the SQL query,
        and prints it to the console.
        """
        if not self.query_root:
            print("No query root has been set.")
            return

        # Build the query structure starting from the root
        query = self._build_query_from_item(self.query_root)
        if query:
            print("Generated SQL Query:")
            print(query.build_query())
        else:
            print("Failed to build the query.")

    def _build_query_from_item(self, item):
        """
        Recursively builds the query structure starting from the given item.

        Args:
            item (DraggableItem): The current item to process.

        Returns:
            Query or Subquery: The constructed query or subquery.
        """
        if item.text() in ["OR", "AND"]:
            # This is a logical operator (UNION or INTERSECT)
            queries = []
            for child in item.children_items:
                child_query = self._build_query_from_item(child)
                if child_query:
                    queries.append(child_query)

            if not queries:
                return None

            # Determine the operation (UNION or INTERSECT) based on the item's text
            operation = "UNION" if item.text() == "OR" else "INTERSECT"
            return Query(queries=queries, union_or_intersect=operation)

        elif item.text().endswith("range"):
            # This is a range filter
            print(item.text())
            low_value = item.low_input.text()
            high_value = item.high_input.text()
            if not low_value or not high_value:
                print(f"Invalid range values for item: {item.text()}")
                return None

            table_name, column_name = item.text().replace("range", "").split("_")
            return Subquery(
                table_column_pairs=[(table_name, column_name)],
                filters=[RangeFilter(table_name, column_name, low_value, high_value)],
            )

        elif item.text() == "ReadmissionFilter":
            # This is a readmission filter
            time_between_admissions = item.low_input.text()  # Assuming low_input stores the time
            if not time_between_admissions:
                print("Invalid time value for readmission filter.")
                return None

            return Subquery(
                table_column_pairs=[("admissions", "hadm_id")],
                filters=[ReadmissionFilter("admissions", time_between_admissions)],
            )

        else:
            # This is a regular filter (equality or other)
            table_name, column_name, value = item.text().split(" - ")
            if not value:
                print(f"Invalid value for item: {item.text()}")
                return None

            return Subquery(
                table_column_pairs=[(table_name, column_name)],
                filters=[EqualityFilter(table_name, column_name, value)],
            )


class CanvasArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white; border: 2px solid #555;")
        self.setVisible(True)
        self.raise_()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        painter.setPen(QPen(Qt.black, 2))

        for item in self.parent().items:
            if item.parent_item:
                start = item.parent_item.rect().center()
                end = item.rect().center()

                start = self.mapFromParent(item.parent_item.mapToParent(start))
                end = self.mapFromParent(item.mapToParent(end))

                start.setY(start.y() + 70)
                end.setY(end.y() + 70)
                start.setX(start.x() + 20)
                end.setX(end.x() + 20)

                painter.drawLine(start, end)
                self.draw_arrowhead(painter, start, end)

        painter.end()
        
    def draw_arrowhead(self, painter, start, end):
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