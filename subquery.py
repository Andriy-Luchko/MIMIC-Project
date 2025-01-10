class Subquery:
    """
    A class for building SQL subqueries by joining tables and applying filters.

    Attributes:
        table_column_pairs (list): A list of tuples, where each tuple contains a table name and a column name
                                   (e.g., [("patients", "patient_id"), ("admissions", "admission_id")]).
        filters (list): A list of filter conditions to apply to the query. Each filter can be an instance of either
                        the `EqualityFilter` or `RangeFilter` class.
        filter_combination (str): The logical operator ('AND' or 'OR') used to combine filters in the WHERE clause.
                                  Defaults to 'AND'.
        tables (set): A set of all tables involved in the subquery. This is populated by recursively joining tables.
        name_to_table_map (dict): A mapping of table names to `Table` objects, which contain the join conditions
                                  and parent-child relationships for each table.
    """

    def __init__(self, table_column_pairs, filters, filter_combination="AND"):
        """
        Initializes the Subquery object with the provided table column pairs, filters, and filter combination.

        Args:
            table_column_pairs (list): A list of tuples with (table_name, column_name), where each tuple represents
                                        a column in a specific table to be selected in the query.
            filters (list): A list of filters to be applied to the query. Filters are represented as filter tuples,
                            where each tuple contains the necessary components to create the filter (e.g., column
                            name and value).
            filter_combination (str): The logical combination for applying filters. Default is 'AND'. This will
                                       be used to combine multiple filter conditions in the WHERE clause.
        """
        self.table_column_pairs = table_column_pairs
        self.filters = filters
        self.filter_combination = filter_combination
        self.name_to_table_map = self.create_name_to_table_map()

    def recursive_join(self, table_name, from_tables, where_conditions, visited_tables):
        """
        Recursively joins tables by traversing parent-child relationships and adding join conditions.

        Args:
            table_name (str): The current table to be joined.
            from_tables (list): A list of tables that have already been included in the FROM clause.
            where_conditions (list): A list of WHERE conditions to be added to the query.
            visited_tables (set): A set of tables that have already been visited to prevent cycles in joins.
        """
        if table_name in visited_tables:
            return
        visited_tables.add(table_name)

        current_table = self.name_to_table_map.get(table_name)
        if not current_table:
            return

        from_tables.append(table_name)
        for parent_table, join_condition in zip(
            current_table.parent_tables, current_table.join_conditions
        ):
            where_conditions.append(
                f"{parent_table}.{join_condition[0]} = {table_name}.{join_condition[1]}"
            )
            self.recursive_join(
                parent_table, from_tables, where_conditions, visited_tables
            )

    def get_select_columns(self):
        """
        Constructs the SELECT clause of the SQL query based on the table_column_pairs.

        Returns:
            str: A string representing the SELECT clause with the fully-qualified column names.
        """
        columns = [f"{table}.{column}" for table, column in self.table_column_pairs]
        return ",\n".join(columns)

    def build_query(self):
        """
        Builds the complete SQL query by combining the SELECT columns, JOIN conditions, and WHERE conditions.

        Returns:
            str: The complete SQL query as a string.
        """
        from_tables = [self.root_table]
        where_conditions = []
        visited_tables = set([self.root_table])

        for table_name, _ in self.table_column_pairs:
            self.recursive_join(
                table_name, from_tables, where_conditions, visited_tables
            )

        for filter in self.filters:
            self.recursive_join(
                filter.table_name, from_tables, where_conditions, visited_tables
            )

        filter_conditions = [filter.to_sql() for filter in self.filters]
        final_filter = f"({f'\n{self.filter_combination}\n'.join(filter_conditions)})"
        where_conditions.append(final_filter)

        query = (
            f"SELECT\n{self.get_select_columns()}\nFROM "
            + ", ".join(from_tables)
            + "\n"
        )
        if where_conditions:
            query += f"WHERE\n" + f"\nAND\n".join(where_conditions)
        return query

    # The starting table for the subquery, representing patients.
    root_table = "patients"

    # A list of table names to join starting from the "patients" table, each containing data related to a subject ID.
    patient_subject_id_joins = [
        "admissions",
        "edstays",
        "patient_blood_pressure",
        "patient_blood_pressure_lying",
        "patient_blood_pressure_sitting",
        "patient_blood_pressure_standing",
        "patient_blood_pressure_standing_1min",
        "patient_blood_pressure_standing3mins",
        "patient_bmi",
        "patient_eGFR",
        "patient_height",
        "patient_weight",
        "labevents",
        "microbiologyevents",
        "radiology",
        "transfers",
    ]

    # A list of table names to join starting from the "admissions" table, each containing data related to a hospital admission.
    admissions_hadm_id_joins = [
        "diagnoses_icd",
        "discharge",
        "drgcodes",
        "emar",
        "hcpcsevents",
        "icustays",
        "pharmacy",
        "poe",
        "procedures_icd",
        "services",
        "prescriptions",
    ]

    # A list of table names to join starting from the "edstays" table, each containing data related to an emergency department stay.
    edstays_ed_stay_id_joins = ["diagnosis", "medrecon", "pyxis", "triage", "vitalsign"]

    # A list of table names to join starting from the "icustays" table, each containing data related to an ICU stay.
    icustays_icu_stay_id_joins = [
        "outputevents",
        "datetimeevents",
        "chartevents",
        "ingredientevents",
        "procedureevents",
        "inputevents",
    ]

    @classmethod
    def create_name_to_table_map(cls):
        """
        Creates a mapping from table names to Table objects for use in joins.

        Returns:
            dict: A dictionary mapping table names to Table objects.
        """
        name_to_table_map = {}

        # Root table
        name_to_table_map[cls.root_table] = Table(table_name=cls.root_table)

        # Adding tables with joins
        for table_name in cls.patient_subject_id_joins:
            name_to_table_map[table_name] = Table(
                table_name=table_name,
                parent_tables=["patients"],
                join_conditions=[("subject_id", "subject_id")],
            )

        for table_name in cls.admissions_hadm_id_joins:
            name_to_table_map[table_name] = Table(
                table_name=table_name,
                parent_tables=["admissions"],
                join_conditions=[("hadm_id", "hadm_id")],
            )

        for table_name in cls.edstays_ed_stay_id_joins:
            name_to_table_map[table_name] = Table(
                table_name=table_name,
                parent_tables=["edstays"],
                join_conditions=[("ed_stay_id", "ed_stay_id")],
            )

        for table_name in cls.icustays_icu_stay_id_joins:
            name_to_table_map[table_name] = Table(
                table_name=table_name,
                parent_tables=["icustays"],
                join_conditions=[("icu_stay_id", "icu_stay_id")],
            )

        # Tables with multiple parents and join conditions
        name_to_table_map["d_hcpcs"] = Table(
            table_name="d_hcpcs",
            parent_tables=["hcpcsevents"],
            join_conditions=[("hcpcs_cd", "code")],
        )

        name_to_table_map["d_icd_diagnoses"] = Table(
            table_name="d_icd_diagnoses",
            parent_tables=["diagnoses_icd", "diagnosis"],
            join_conditions=[("icd_code", "icd_code"), ("icd_code", "icd_code")],
        )

        name_to_table_map["d_icd_procedures"] = Table(
            table_name="d_icd_procedures",
            parent_tables=["procedures_icd"],
            join_conditions=[("icd_code", "icd_code")],
        )

        name_to_table_map["emar_detail"] = Table(
            table_name="emar_detail",
            parent_tables=["emar"],
            join_conditions=[("emar_id", "emar_id")],
        )

        name_to_table_map["poe_detail"] = Table(
            table_name="poe_detail",
            parent_tables=["poe"],
            join_conditions=[("poe_id", "poe_id")],
        )

        name_to_table_map["d_items"] = Table(
            table_name="d_items",
            parent_tables=[
                "chartevents",
                "datetimeevents",
                "ingredientevents",
                "inputevents",
                "procedureevents",
                "outputevents",
            ],
            join_conditions=[
                ("itemid", "itemid"),
                ("itemid", "itemid"),
                ("itemid", "itemid"),
                ("itemid", "itemid"),
                ("itemid", "itemid"),
                ("itemid", "itemid"),
            ],
        )

        name_to_table_map["lab_items"] = Table(
            table_name="lab_items",
            parent_tables=["poe"],
            join_conditions=[("poe_id", "poe_id")],
        )

        return name_to_table_map


class Table:
    """
    A class representing a database table, including its name, parent tables, and join conditions.

    Attributes:
        name (str): The name of the table.
        parent_tables (list of str): A list of parent table names that this table joins with.
        join_conditions (list of tuples): A list of join conditions represented as tuples,
                                        where each tuple contains two strings: the column
                                        from the parent table and the corresponding column
                                        from the current table.

    Methods:
        __init__(self, table_name, parent_tables=None, join_conditions=None):
            Initializes a new Table object with the given table name, parent tables, and join conditions.
    """

    def __init__(self, table_name, parent_tables=None, join_conditions=None):
        """
        Initializes a new Table object.

        Args:
            table_name (str): The name of the table.
            parent_tables (list of str, optional): A list of parent table names that this table is related to.
                                                   Defaults to an empty list if not provided.
            join_conditions (list of tuples, optional): A list of tuples representing the join conditions.
                                                       Each tuple should contain two strings:
                                                       the parent table's column and the corresponding
                                                       column in the current table.

        """
        self.name = table_name
        self.parent_tables = parent_tables
        self.join_conditions = join_conditions


class Filter:
    """
    A base class representing a filter applied to a column in a table. This class is extended
    by other filter types to implement specific filtering behavior.

    Attributes:
        table_name (str): The name of the table containing the column to filter.
        column_name (str): The name of the column to filter.

    Methods:
        __init__(self, table_name, column_name):
            Initializes a new Filter object with the specified table and column names.

        filter_tuple_to_sql(filter_tuple):
            Converts a filter tuple into an SQL condition string based on the filter type.
    """

    def __init__(self, table_name, column_name):
        self.table_name = table_name
        self.column_name = column_name

    @staticmethod
    def filter_tuple_to_sql(filter_tuple):
        """
        Converts a filter tuple into an SQL condition string based on the filter type.

        Args:
            filter_tuple (tuple): A tuple representing the filter, where the length of the tuple
                                   determines the filter type. A tuple with 3 elements is treated as
                                   an equality filter (table_name, column_name, value), and a tuple with 4 elements is treated as a
                                   range filter (table_name, column_name, min_value, max_value).

        Returns:
            str: An SQL condition string corresponding to the filter.

        Raises:
            ValueError: If the filter tuple has an invalid length (neither 3 nor 4 elements).
        """
        if len(filter_tuple) == 3:
            return EqualityFilter(*filter_tuple).to_sql()
        elif len(filter_tuple) == 4:
            return RangeFilter(*filter_tuple).to_sql()
        else:
            raise ValueError("Invalid filter format")


class EqualityFilter(Filter):
    """
    A class representing an equality filter applied to a column in a table.

    Attributes:
        table_name (str): The name of the table containing the column to filter.
        column_name (str): The name of the column to filter.
        value (str): The value to compare the column against.

    Methods:
        __init__(self, table_name, column_name, value):
            Initializes a new EqualityFilter object with the specified table, column, and value.

        to_sql(self):
            Converts the equality filter into an SQL condition string.
    """

    def __init__(self, table_name, column_name, value):
        """
        Initializes a new RangeFilter object.

        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column.
            min_value (float): The minimum value for the range.
            max_value (float): The maximum value for the range.
        """
        super().__init__(table_name, column_name)
        self.value = value

    def to_sql(self):
        """
        Converts the equality filter into an SQL condition string.

        Returns:
            str: An SQL condition string for the equality filter.
        """
        return f"{self.table_name}.{self.column_name} = '{self.value}'"


class RangeFilter(Filter):
    """
    A class representing a range filter applied to a column in a table.

    Attributes:
        table_name (str): The name of the table containing the column to filter.
        column_name (str): The name of the column to filter.
        min_value (float): The minimum value for the range.
        max_value (float): The maximum value for the range.

    Methods:
        __init__(self, table_name, column_name, min_value, max_value):
            Initializes a new RangeFilter object with the specified table, column, and range.

        to_sql(self):
            Converts the range filter into an SQL condition string.
    """

    def __init__(self, table_name, column_name, min_value, max_value):
        """
        Initializes a new RangeFilter object.

        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column.
            min_value (float): The minimum value for the range.
            max_value (float): The maximum value for the range.
        """
        super().__init__(table_name, column_name)
        self.min_value = min_value
        self.max_value = max_value

    def to_sql(self):
        """
        Converts the range filter into an SQL condition string.

        Returns:
            str: An SQL condition string for the range filter.
        """
        return f"{self.table_name}.{self.column_name} BETWEEN {self.min_value} AND {self.max_value}"


class ReadmissionFilter(Filter):
    """
    A class representing a filter on readmissions

    Attributes:
        time_between_admissions (str): Time between the admissions.
        first_admission_filters (Filter[]): The filters of the first admission.
        second_admission_icd (Filter[]): The icd of the second admission.

    Methods:
        __init__(self, time_between_admissions, first_admission_filters, second_admission_icd):
            Initializes a new ReadmissionFilter object with the specified time between admissions and diagnosis of each admission

    """

    def __init__(self, table_name, time_between_admissions):
        self.time_between_admissions = time_between_admissions
        self.table_name = table_name

    def to_sql(self):
        return f"""admissions.hadm_id IN
(
	SELECT * FROM (
		SELECT a.hadm_id
		FROM admissions a
		JOIN admissions a2
		WHERE CAST((julianday(a2.admittime) - julianday(a.admittime)) AS REAL) < {self.time_between_admissions}
		AND CAST((julianday(a2.admittime) - julianday(a.admittime)) AS REAL) > 0
		AND a.hadm_id != a2.hadm_id
		AND a.subject_id = a2.subject_id
	UNION
		SELECT a.hadm_id
		FROM admissions a
		JOIN admissions a2
		WHERE CAST((julianday(a.admittime) - julianday(a2.admittime)) AS REAL) < {self.time_between_admissions}
		AND CAST((julianday(a.admittime) - julianday(a2.admittime)) AS REAL) > 0
		AND a.hadm_id != a2.hadm_id
		AND a.subject_id = a2.subject_id
	)
)
"""
