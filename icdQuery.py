import sqlite3

def build_select_and_joins(column_pairs):
    # Start the query with 'FROM patients'
    query = "SELECT "
    
    # List to hold the joins
    join_clauses = []
    
    # A dictionary to map table names to the correct join conditions
    left_join_conditions = {
        'admissions': 'patients.subject_id = admissions.subject_id', 
        'chartevents': 'admissions.hadm_id = chartevents.hadm_id',
        'diagnosis': 'admissions.hadm_id = diagnosis.hadm_id',
        'diagnoses_icd': 'admissions.hadm_id = diagnoses_icd.hadm_id',
        'discharge': 'admissions.hadm_id = discharge.hadm_id',
        'd_icd_diagnoses': 'diagnoses_icd.icd_code = d_icd_diagnoses.icd_code', # must join diagnoses_icd
        'd_icd_procedures': 'procedureevents.icd_code = d_icd_procedures.icd_code', # must join procedureevents
        'drgcodes': 'admissions.hadm_id = drgcodes.hadm_id',
        'edstays': 'admissions.hadm_id = edstays.hadm_id',
        'emar': 'admissions.hadm_id = emar.hadm_id',
        'emar_detail': 'emar.emar_id = emar_detail.emar_id',
        'hcpcsevents': 'admissions.hadm_id = hcpcsevents.hadm_id',
        'icustays': 'admissions.hadm_id = icustays.hadm_id',
        'ingredientevents': 'admissions.hadm_id = ingredientevents.hadm_id',
        'inputevents': 'admissions.hadm_id = inputevents.hadm_id',
        'labevents': 'admissions.hadm_id = labevents.hadm_id',
        'microbiologyevents': 'admissions.hadm_id = microbiologyevents.hadm_id',
        'omr': 'admissions.hadm_id = omr.hadm_id',
        'pharmacy': 'admissions.hadm_id = pharmacy.hadm_id',
        'poe': 'admissions.hadm_id = poe.hadm_id',
        'prescriptions': 'admissions.hadm_id = prescriptions.hadm_id',
        'procedures_icd': 'admissions.hadm_id = procedures_icd.hadm_id',
        'provider': 'admissions.hadm_id = provider.hadm_id',
        'radiology': 'admissions.hadm_id = radiology.hadm_id',
        'services': 'admissions.hadm_id = services.hadm_id',
        'transfers': 'admissions.hadm_id = transfers.hadm_id',
        'vitalsign': 'admissions.hadm_id = vitalsign.hadm_id',
        'procedureevents': 'admissions.hadm_id = procedureevents.hadm_id',
        'diagnoses_icd': 'admissions.hadm_id = diagnoses_icd.hadm_id',
    }
    
    # If any of these are included, we need to have chartevents joined
    full_join_conditions = {
        'd_labitems': 'chartevents.itemid = d_labitems.itemid',
        'd_items': 'chartevents.itemid = d_items.itemid',
        'd_hcpcs': 'chartevents.itemid = d_hcpcs.code',
    }

    # Add the selected columns to the SELECT clause
    query += ", ".join([f'{table}.{column}' for table, column in column_pairs])
    
    # Get a set of all the tables used
    tables_used = set([table for table, column in column_pairs])
    
    if "patients" in tables_used:
        tables_used.remove("patients")
    
    # Ensure admissions is joined if any tables are used
    if tables_used:
        join_clauses.append(f"JOIN admissions ON {left_join_conditions['admissions']}")
        if "admissions" in tables_used:
            tables_used.remove("admissions")
    
    # Keep track of whether chartevents, diagnoses_icd, and procedureevents have been joined
    chartevents_joined = False
    diagnoses_icd_joined = False
    procedureevents_joined = False
    
    # Handle full joins for tables dependent on chartevents
    for table in tables_used:
        if table in full_join_conditions:
            if not chartevents_joined:
                join_clauses.append(f"JOIN chartevents ON {left_join_conditions['chartevents']}")
                chartevents_joined = True
            join_clauses.append(f"JOIN {table} ON {full_join_conditions[table]}")
    
    # Handle left joins for other tables, skipping 'd_icd_diagnoses' and 'd_icd_procedures'
    for table in tables_used:
        if table == "diagnoses_icd":
            diagnoses_icd_joined = True
        if table == "procedureevents":
            procedureevents_joined = True
            
        if chartevents_joined and table == "chartevents":
            continue
        
        if table in ['d_icd_diagnoses', 'd_icd_procedures']:
            continue
        
        if table in left_join_conditions and table not in full_join_conditions:
            join_clauses.append(f"JOIN {table} ON {left_join_conditions[table]}")
    
    # Check and join diagnoses_icd if needed
    if 'd_icd_diagnoses' in tables_used and not diagnoses_icd_joined:
        join_clauses.append(f"JOIN diagnoses_icd ON {left_join_conditions['diagnoses_icd']}")
        diagnoses_icd_joined = True
    
    # Check and join procedureevents if needed
    if 'd_icd_procedures' in tables_used and not procedureevents_joined:
        join_clauses.append(f"JOIN procedureevents ON {left_join_conditions['procedureevents']}")
        procedureevents_joined = True
    
    # Join d_icd_diagnoses and d_icd_procedures
    if 'd_icd_diagnoses' in tables_used:
        join_clauses.append(f"JOIN d_icd_diagnoses ON {left_join_conditions['d_icd_diagnoses']}")
    
    if 'd_icd_procedures' in tables_used:
        join_clauses.append(f"JOIN d_icd_procedures ON {left_join_conditions['d_icd_procedures']}")
    
    # Combine the SELECT and JOIN parts
    query += " FROM patients " + " ".join(join_clauses)
    
    return query

def fetch_patient_data(database_path, icd_codes_versions, column_pairs, chunk_size=1000):
    """
    Connects to the SQLite database and fetches patient data for the given ICD codes and versions,
    dynamically selecting columns based on the provided (table, column) pairs using the query builder.

    Args:
        database_path (str): Path to the SQLite database file.
        icd_codes_versions (list of tuples): List of tuples containing ICD codes and their versions.
        column_pairs (list of tuples): List of tuples containing (table_name, column_name) to select dynamically.
        chunk_size (int): Number of rows to fetch per chunk.

    Yields:
        list: Query results as a list of rows.
    """
    # Separate ICD codes by version
    icd_version_9 = [f"'{code}'" for code, version in icd_codes_versions if version == 9]
    icd_version_10 = [f"'{code}'" for code, version in icd_codes_versions if version == 10]

    # Dynamically construct the SELECT clause and JOIN conditions using the build_select_and_joins function
    select_and_joins = build_select_and_joins(column_pairs)

    # Construct the WHERE clause for ICD codes
    where_clause = f"""
    WHERE 
        (diagnoses_icd.icd_version = 9 AND diagnoses_icd.icd_code IN ({','.join(icd_version_9)}))
        OR 
        (diagnoses_icd.icd_version = 10 AND diagnoses_icd.icd_code IN ({','.join(icd_version_10)}))
    """

    # Combine the query with the WHERE clause
    query = f"{select_and_joins} {where_clause};"

    # Print query to double-check
    print(query)
    return []
    # Connect to the database and execute the query
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute(query)

        while True:
            # Fetch the next chunk of results
            chunk = cursor.fetchmany(chunk_size)
            if not chunk:  # Exit loop if no more rows
                break
            yield chunk

        conn.close()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":

    database_path = "MIMIC_Database.db"
    
    column_pairs = [
    ('admissions', 'hadm_id'),
    ('patients', 'subject_id'),
    ('chartevents', 'charttime'),
    ('d_items', 'label'),
    ('diagnoses_icd', 'icd_code'),
    ('chartevents', 'value'),
    ('chartevents', 'valuenum'),
    ('chartevents', 'valueuom'),
    ('admissions', 'admittime'),
    ('admissions', 'dischtime'),
    ('admissions', 'race'),
    ('admissions', 'marital_status'),
    ('patients', 'gender'),
    ('patients', 'anchor_age'),
    ('patients', 'dod')
    ]
    
    # ICD codes and versions
    icd_codes_versions = [
        ("J13", 10),
        ("J12.8", 10),
        ("J16.8", 10),
        ("480", 9),
        ("481", 9),
        ("482", 9),
        ("486", 9)
    ]

    # Fetch and print the data - using a generator function
    for chunk in fetch_patient_data(database_path, icd_codes_versions, column_pairs):
        for row in chunk:
            print(row)
