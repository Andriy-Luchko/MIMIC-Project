import os
import sqlite3
import pandas as pd
from typing import List
from functools import cache

@cache
def get_file_name_from_path(csv_file_path: str) -> str:
    '''
    Gets the file name from the file's path by removing the path and extension
    '''
    # Extract the file name from the full path
    file_name = os.path.basename(csv_file_path)
    
    # Remove the file extension
    table_name, _ = os.path.splitext(file_name)
    
    return table_name

@cache
def get_csv_path_and_table_names(directory_to_search) -> List[tuple]:
    '''
    Finds every csv file inside this directory and strips to its basename with no extension
    Returns a list of pairs of csv file name and the stripped name
    '''
    # Get current directory and find every csv file
    csv_files_paths = []
    for root, _, files in os.walk(directory_to_search):
        for file in files:
            if file.endswith('.csv'):
                csv_files_paths.append(os.path.join(root, file))

    # For every csv file strip the path and extension to get the table name
    return [(csv_file_path, get_file_name_from_path(csv_file_path)) for csv_file_path in csv_files_paths]

def execute_script(connection, sql_script):
    """
    Executes a given SQL script on the provided database connection.

    Args:
        connection (sqlite3.Connection): A connection to the SQLite database.
        sql_script (str): The SQL script to execute.
    """
    try:
        cursor = connection.cursor()
        cursor.executescript(sql_script)
        connection.commit()
        print("SQL script executed successfully.")
    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    
def drop_all_tables(connection):
    """
    Reads the SQL commands from drop_tables.sql and executes them to drop all tables.

    Args:
        connection (sqlite3.Connection): A connection to the SQLite database.
    """
    sql_file_path = "./sql_scripts/drop_tables.sql"
    try:
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
        print("Executing DROP TABLE script.")
        execute_script(connection, sql_script)
        print("Tables dropped successfully.")
    except FileNotFoundError:
        print(f"Error: The file {sql_file_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_all_tables(connection):
    """
    Reads the SQL commands from create_tables.sql and executes them to create all tables.

    Args:
        connection (sqlite3.Connection): A connection to the SQLite database.
    """
    sql_file_path = "./sql_scripts/create_tables.sql"
    try:
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
        print("Executing CREATE TABLE script.")
        execute_script(connection, sql_script)
        print("Tables created successfully.")
    except FileNotFoundError:
        print(f"Error: The file {sql_file_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    

def insert_all_data(connection, path_to_data):
    # This function inserts data from CSV files into the corresponding tables with chunking
    csv_paths_and_table_names = get_csv_path_and_table_names(path_to_data)
    chunksize = 100000  # Size of each chunk
    
    # in case they rename their files or have an extra csv inside the directory - we want to make sure we are only making the tables we want
    work_set = set(['pyxis', 'vitalsign', 'medrecon', 'triage', 'edstays', 'diagnosis', 'poe_detail', 'provider', 'pharmacy', 'emar', 'microbiologyevents', 'labevents', 'admissions', 'd_labitems', 'prescriptions', 'procedures_icd', 'poe', 'd_hcpcs', 'omr', 'transfers', 'diagnoses_icd', 'services', 'hcpcsevents', 'drgcodes', 'patients', 'd_icd_diagnoses', 'd_icd_procedures', 'emar_detail', 'd_items', 'procedureevents', 'inputevents', 'datetimeevents', 'ingredientevents', 'chartevents', 'caregiver', 'outputevents', 'icustays', 'radiology', 'discharge'])
    
    for csv_file_path, table_name in csv_paths_and_table_names:
        if table_name not in work_set:
            continue
        # Use pd.read_csv to read the CSV in chunks
        for i, chunk in enumerate(pd.read_csv(csv_file_path, chunksize=chunksize, low_memory=False)):
            # Insert each chunk into the corresponding table
            chunk.to_sql(table_name, connection, if_exists="append", index=False)
            print(f"{i} Inserted a chunk of data into {table_name} - rows complete: ({(i + 1) * chunksize})")
            break
        
        print(f"Inserted all data into {table_name}.")

def create_database(path_to_data):
    database_path = "./MINI_MIMIC_Database.db"

    with sqlite3.connect(database_path) as connection:
        drop_all_tables(connection)
        create_all_tables(connection)
        insert_all_data(connection, path_to_data)
        split_omr(connection)
        rename_stay_id_columns(connection)
        print("All tables processed successfully!")
        print(f"Database made at {database_path}")
        print(f"Data taken from {path_to_data}")

def split_omr(connection):
    """
    Reads the SQL commands from split_omr.sql and executes them to split the OMR table data into separate tables.

    Args:
        connection (sqlite3.Connection): A connection to the SQLite database.
    """
    sql_file_path = "./sql_scripts/split_omr.sql"
    try:
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
        print("Executing SPLIT OMR script.")
        execute_script(connection, sql_script)
        print("OMR table split successfully.")
    except FileNotFoundError:
        print(f"Error: The file {sql_file_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def rename_stay_id_columns(connection):
    """
    Reads the SQL commands from rename_stay_id.sql and executes them to rename stay_id columns.

    Args:
        connection (sqlite3.Connection): A connection to the SQLite database.
    """
    sql_file_path = "./sql_scripts/rename_stay_id.sql"
    try:
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
        print("Executing RENAME STAY_ID script.")
        execute_script(connection, sql_script)
        print("Stay ID columns renamed successfully.")
    except FileNotFoundError:
        print(f"Error: The file {sql_file_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
def main():
    database_path = "./MINI_MIMIC_Database.db"

    with sqlite3.connect(database_path) as connection:
        if 0:
            drop_all_tables(connection)
        if 0:
            create_all_tables(connection)
        if 0:
            insert_all_data(connection, os.getcwd())
        if 0:
            split_omr(connection)
        if 1:
            rename_stay_id_columns(connection)
            
        print("All tables processed successfully!")

if __name__ == "__main__":
    main()


