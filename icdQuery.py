import sqlite3

def fetch_patient_data(database_path, icd_codes_versions, chunk_size = 1000):
    """
    Connects to the SQLite database and fetches patient data for the given ICD codes and versions.

    Args:
        database_path (str): Path to the SQLite database file.
        icd_codes_versions (list of tuples): List of tuples containing ICD codes and their versions.

    Returns:
        list: Query results as a list of rows.
    """
    # Separate ICD codes by version
    icd_version_9 = [f"'{code}'" for code, version in icd_codes_versions if version == 9]
    icd_version_10 = [f"'{code}'" for code, version in icd_codes_versions if version == 10]

    # SQL query with directly formatted IN clauses
    query = f"""
    SELECT 
        a.hadm_id, 
        c.charttime, 
        c.itemid, 
        di.label,
        c.value, 
        c.valuenum, 
        c.valueuom,
        a.subject_id, 
        a.admittime, 
        a.dischtime, 
        julianday(a.dischtime) - julianday(a.admittime) AS length_of_stay, 
        a.race, 
        a.marital_status, 
        p.gender, 
        p.anchor_age, 
        p.dod 
    FROM 
        admissions a
    JOIN 
        patients p 
    ON 
        a.subject_id = p.subject_id
    JOIN 
        diagnoses_icd d 
    ON 
        a.hadm_id = d.hadm_id
    JOIN 
        chartevents c 
    ON 
        a.hadm_id = c.hadm_id
    JOIN 
        d_items di 
    ON 
        c.itemid = di.itemid
    WHERE 
        (d.icd_version = 9 AND d.icd_code IN ({','.join(icd_version_9)}))
        OR 
        (d.icd_version = 10 AND d.icd_code IN ({','.join(icd_version_10)}));
    """

    # Print query to double check
    print(query)
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
    for chunk in fetch_patient_data(database_path, icd_codes_versions):
        for row in chunk:
            print(row)
