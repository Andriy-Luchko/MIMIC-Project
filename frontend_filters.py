import sqlite3

def get_unique_column_values(db_connection, table_name, column_name):
    """
    Helper function to fetch distinct values from a specified column in a specified table.
    Returns a list of formatted strings like:
    ['<table_name> - <column_name> - <value>', ...]
    """
    db_cursor = db_connection.cursor()

    # Construct the SQL query to fetch distinct values from the specified column of the table
    query = f"SELECT DISTINCT {column_name} FROM {table_name}"

    try: # Execute the query
        db_cursor.execute(query)
        column_data = db_cursor.fetchall()

        # Format the data for each value
        formatted_values = [
            f"{table_name} - {column_name} - {value[0]}"  # value[0] contains the column value
            for value in column_data
        ]
        return formatted_values
    except sqlite3.OperationalError:
        print("Table doesn't exist")
        
    return []


def fetch_unique_values(db_connection):
    """
    Calls get_unique_column_values for every table and column.
    """
    # Define the tables and their corresponding columns
    table_column_map = {
        "admissions": ["admission_type"],
        "d_icd_diagnoses": ["icd_code", "icd_version", "long_title"],
        "d_icd_procedures": ["icd_code", "icd_version", "long_title"],
        "d_labitems": ["itemid", "label"],
        "emar": ["medication"],
        "microbiologyevents": ["test_name", "org_name", "ab_name"],
        "prescriptions": ["drug", "formulary_drug_cd", "gsn"],
        "services": ["curr_service"],
        "transfers": ["careunit"],
        "edstays": ["race", "gender", "disposition"],
        "chartevents_d_items": ["itemid", "label", "abbreviation", "category"],
        "datetimeevents_d_items": ["itemid", "label", "abbreviation", "category"],
        "ingredientevents_d_items": ["itemid", "label", "abbreviation", "category"],
        "inputevents_d_items": ["itemid", "label", "abbreviation", "category"],
        "procedureevents_d_items": ["itemid", "label", "abbreviation", "category"],
        "outputevents_d_items": ["itemid", "label", "abbreviation", "category"],
    }

    all_values = []

    # Loop through each table and column, call the helper function
    for table, columns in table_column_map.items():
        for column in columns:
            column_values = get_unique_column_values(db_connection, table, column)
            # Unpack the values into the format: table_name - column_name - value
            for value in column_values:
                all_values.append(value)  # value is already in the correct format
    return all_values

def get_range_filters():
    range_filters = ["patients - anchor_age - range", 
                     "triage - temperature - range",
                     "triage - heartrate - range",
                     "triage - resprate - range",
                     "triage - o2sat - range",
                     "triage - sbp - range",
                     "triage - dbp - range",
                     "triage - acuity - range",
                     "vitalsign - temperature - range",
                     "vitalsign - heartrate - range",
                     "vitalsign - resprate - range",
                     "vitalsign - o2sat - range",
                     "vitalsign - sbp - range",
                     "vitalsign - dbp - range",
                     "patient_blood_pressure - systolic - range",
                     "patient_blood_pressure - diastolic - range",
                     "patient_blood_pressure_lying - systolic - range",
                     "patient_blood_pressure_lying - diastolic - range",
                     "patient_blood_pressure_sitting - systolic - range",
                     "patient_blood_pressure_sitting - diastolic - range",
                     "patient_blood_pressure_standing - systolic - range",
                     "patient_blood_pressure_standing - diastolic - range",
                     "patient_blood_pressure_standing_1min - systolic - range",
                     "patient_blood_pressure_standing_1min - diastolic - range",
                     "patient_blood_pressure_standing3mins - systolic - range",
                     "patient_blood_pressure_standing3mins - diastolic - range",
                     "patient_bmi - bmi_value - range",
                     "patient_eGFR - eGFR - range",
                     "patient_height - height_inches - range",
                     "patient_weight - weight_lbs - range",]
    return range_filters
