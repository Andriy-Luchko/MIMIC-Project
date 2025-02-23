import os
import csv
import json
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QPainter, QPen, QPolygon
from PyQt5.QtCore import Qt, QPoint, QRect
from draggable_item import DraggableItem
from json_to_sql import json_to_sql

class Canvas(QWidget):
    def __init__(self, frontend, parent=None):
        self.frontend = frontend
        super().__init__(parent)
        self.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.setMinimumHeight(400)
        self.items = []
        self.delete_mode = False
        self.connection_mode = False
        self.mark_root_mode = False
        self.selected_item = None 
        self.query_root = None
        self.diagnosed_in = "hospital"  # Default value

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

        # New toggle button for diagnosis location
        self.diagnosis_toggle = QPushButton("🏥 Hospital")  # Start with Hospital
        self.diagnosis_toggle.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px 30px; background-color: #2196F3; color: white; border-radius: 10px;"
        )
        self.diagnosis_toggle.clicked.connect(self.toggle_diagnosis_location)

        self.print_query_button = QPushButton("🖨️ Print Query")
        self.print_query_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px 30px; background-color: #607D8B; color: white; border-radius: 10px;"
        )
        self.print_query_button.clicked.connect(self.print_query)
        
        self.run_query_button = QPushButton("🚀 Run Query")
        self.run_query_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 15px 30px; background-color: #009688; color: white; border-radius: 10px;"
        )
        self.run_query_button.clicked.connect(self.run_query)

        self.button_row.addStretch()
        self.button_row.addWidget(self.add_or_button)
        self.button_row.addWidget(self.add_and_button)
        self.button_row.addWidget(self.connect_button)
        self.button_row.addWidget(self.delete_button)
        self.button_row.addWidget(self.mark_root_button)
        self.button_row.addWidget(self.diagnosis_toggle)  # Add the new toggle button
        self.button_row.addWidget(self.print_query_button)
        self.button_row.addWidget(self.run_query_button)
        self.button_row.addStretch()

        self.layout.addLayout(self.button_row)

        self.canvas_area = CanvasArea(self)
        self.canvas_area.setStyleSheet("background-color: white; border: 2px solid #555;")
        self.canvas_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.canvas_area, stretch=1)

        self.setCursor(Qt.ArrowCursor)

    def toggle_diagnosis_location(self):
        """Toggle between hospital and ER diagnosis locations"""
        if self.diagnosed_in == "hospital":
            self.diagnosed_in = "ed"
            self.diagnosis_toggle.setText("🚑 ER")
        else:
            self.diagnosed_in = "hospital"
            self.diagnosis_toggle.setText("🏥 Hospital")

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
        query = self._get_curr_sql_query()
        if query:
            print("Generated SQL Query:")
            print(query)
        else:
            print("Failed to build the query.")

    def run_query(self):
        """
        Executes the query starting from the root query, writes the results to a CSV file in chunks,
        and handles file naming conflicts by incrementing the file number.
        """
        query = self._get_curr_sql_query()
        if not query:
            print("Failed to build the query.")
            return

        # Generate the SQL query
        print("Executing SQL Query:")
        print(query)

        # Execute the query using the database connection
        try:
            cursor = self.frontend.db_connection.cursor()
            cursor.execute(query)
            column_names = [desc[0] for desc in cursor.description]  # Get column names
        except Exception as e:
            print(f"Error executing query: {e}")
            return

        # Write results to a CSV file in chunks
        base_filename = "output"
        file_extension = ".csv"
        file_number = 1

        # Find the next available filename
        while True:
            filename = f"{base_filename}{file_number}{file_extension}"
            if not os.path.exists(filename):
                break
            file_number += 1

        # Write the results to the CSV file in chunks
        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(column_names)  # Write column headers

                # Fetch and write rows in chunks
                chunk_size = 1000  # Number of rows to fetch and write at a time
                while True:
                    rows = cursor.fetchmany(chunk_size)
                    if not rows:
                        break
                    writer.writerows(rows)  # Write the chunk of rows
                    print(f"Wrote {len(rows)} rows to {filename}")

            print(f"Query results written to {filename}")
        except Exception as e:
            print(f"Error writing to CSV file: {e}")
        finally:
            cursor.close()  # Ensure the cursor is closed
            
    def _build_query_from_item(self, item):
        """
        Recursively builds the query structure starting from the given item.

        Args:
            item (DraggableItem): The current item to process.

        Returns:
            dict: A query object in the format expected by the backend.
        """
        if item.text() in ["OR", "AND"]:
            # This is a logical operator (OR or AND)
            filters = []
            subqueries = []

            for child in item.children_items:
                if child.text().endswith("range") or " - " in child.text() or child.text() == "ReadmissionFilter":
                    # This is a filter
                    child_filter = self._build_filter_from_item(child)
                    if child_filter:
                        filters.append(child_filter)
                else:
                    # This is a subquery (another logical operator)
                    child_query = self._build_query_from_item(child)
                    if child_query:
                        subqueries.append(child_query)

            # Return a query object with both filters and subqueries
            return {
                "operator": item.text(),  # "OR" or "AND"
                "filters": filters,
                "subqueries": subqueries
            }

        else:
            # This is a filter (range, equality, or readmission)
            return self._build_filter_from_item(item)

    def _get_curr_sql_query(self):
        if not self.query_root:
            print("No query root has been set.")
            return

        # Retrieve the selected tables and columns from the ReturnColumnSearchBar
        select_tables = self.frontend.return_column_search_bar.get_selected_tables_and_columns()

        # Build the query structure starting from the root
        query_structure = self._build_query_from_item(self.query_root)

        # If the query structure is a filter, wrap it in a query object with default operator "AND"
        if "filter_type" in query_structure:
            query_structure = {
                "operator": "AND",  # Default operator
                "filters": [query_structure],  # Wrap the filter in a list
                "subqueries": []  # Empty subqueries list
            }

        # Construct the full query object with diagnosed_in setting
        query_object = {
            "diagnosed_in": self.diagnosed_in,  # Use the current diagnosis location setting
            "select_tables": select_tables,
            "query": query_structure
        }

        # Print the query object for debugging
        print(json.dumps(query_object, indent=4))

        # Convert the query object to SQL
        return json_to_sql(query_object)
    
    def _build_filter_from_item(self, item):
        """
        Builds a filter object from the given item.

        Args:
            item (DraggableItem): The current item to process.

        Returns:
            dict: A filter object in the format expected by the backend.
        """
        if item.text().endswith("range"):
            # This is a range filter
            low_value = item.low_input.text()
            high_value = item.high_input.text()
            if not low_value or not high_value:
                print(f"Invalid range values for item: {item.text()}")
                return None

            table_name, column_name, _ = item.text().replace("range", "").split(" - ")
            return {
                "filter_type": "range",
                "table": table_name,
                "column": column_name,
                "min": low_value,
                "max": high_value
            }

        elif item.text() == "ReadmissionFilter":
            # This is a readmission filter
            time_between_admissions = item.low_input.text()  # Assuming low_input stores the time
            if not time_between_admissions:
                print("Invalid time value for readmission filter.")
                return None

            return {
                "filter_type": "value",
                "table": "admissions",
                "column": "time_between_admissions",
                "value": time_between_admissions
            }

        else:
            # This is a regular filter (equality or other)
            table_name, column_name, value = item.text().split(" - ")
            if not value:
                print(f"Invalid value for item: {item.text()}")
                return None

            return {
                "filter_type": "value",
                "table": table_name,
                "column": column_name,
                "value": value
            }


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