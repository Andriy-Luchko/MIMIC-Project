import sqlite3
import pandas as pd
import os
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
def get_csv_path_and_table_names() -> List[tuple]:
    '''
    Finds every csv file inside this directory and strips to its basename with no extension
    Returns a list of pairs of csv file name and the stripped name
    '''
    # Get current directory and find every csv file
    directory_to_search = os.getcwd()
    csv_files_paths = []
    for root, _, files in os.walk(directory_to_search):
        for file in files:
            if file.endswith('.csv'):
                csv_files_paths.append(os.path.join(root, file))

    # For every csv file strip the path and extension to get the table name
    return [(csv_file_path, get_file_name_from_path(csv_file_path)) for csv_file_path in csv_files_paths]

def drop_all_tables(connection):
    # Get a list of CSV file paths and corresponding table names
    csv_paths_and_table_names = get_csv_path_and_table_names()

    # For each table name, execute a DROP TABLE query
    for _, table_name in csv_paths_and_table_names:
        drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
        
        # Execute the drop query using the passed connection
        connection.execute(drop_table_query)
        print(f"Dropped table {table_name} if it existed.")


def create_all_tables(connection):
    csv_paths_and_table_names = get_csv_path_and_table_names()

    table_name_to_schema = {
        "admissions":"""
        CREATE TABLE IF NOT EXISTS admissions (
            subject_id INTEGER,
            hadm_id INTEGER,
            admittime DATETIME,
            dischtime DATETIME,
            deathtime DATETIME,
            admission_type TEXT,
            admit_provider_id TEXT,
            admission_location TEXT,
            discharge_location TEXT,
            insurance TEXT,
            language TEXT,
            marital_status TEXT,
            race TEXT,
            edregtime DATETIME,
            edouttime DATETIME,
            hospital_expire_flag INTEGER,
            PRIMARY KEY (subject_id, hadm_id)
        );
        """,
        "d_hcpcs": """
        CREATE TABLE IF NOT EXISTS d_hcpcs (
            code TEXT PRIMARY KEY,
            category INTEGER,
            long_description TEXT,
            short_description TEXT
        );
        """,
        "d_icd_diagnoses": """
        CREATE TABLE IF NOT EXISTS d_icd_diagnoses (
            icd_code TEXT PRIMARY KEY,
            icd_version INTEGER,
            long_title TEXT
        );
        """,
        "d_icd_procedures": """
        CREATE TABLE IF NOT EXISTS d_icd_procedures (
            icd_code TEXT PRIMARY KEY,
            icd_version INTEGER,
            long_title TEXT
        );
        """,
        "d_labitems": """
        CREATE TABLE IF NOT EXISTS d_labitems (
            itemid INTEGER PRIMARY KEY,
            label TEXT,
            fluid TEXT,
            category TEXT
        );
        """,
        "diagnoses_icd": """ 
        CREATE TABLE IF NOT EXISTS diagnoses_icd (
            subject_id INTEGER,
            hadm_id INTEGER,
            seq_num INTEGER,
            icd_code TEXT,
            icd_version INTEGER,
            PRIMARY KEY (subject_id, hadm_id, seq_num)
            );
        ""","drgcodes": """
    CREATE TABLE IF NOT EXISTS drgcodes (
        subject_id INTEGER,
        hadm_id INTEGER,
        drg_type TEXT,
        drg_code INTEGER,
        description TEXT,
        drg_severity INTEGER,
        drg_mortality INTEGER,
        PRIMARY KEY (subject_id, hadm_id, drg_code)
    );
""",
"emar_detail": """
    CREATE TABLE IF NOT EXISTS emar_detail (
        subject_id INTEGER,
        emar_id TEXT,
        emar_seq INTEGER,
        parent_field_ordinal REAL,
        administration_type TEXT,
        pharmacy_id INTEGER,
        barcode_type TEXT,
        reason_for_no_barcode TEXT,
        complete_dose_not_given TEXT,
        dose_due INTEGER,
        dose_due_unit TEXT,
        dose_given INTEGER,
        dose_given_unit TEXT,
        will_remainder_of_dose_be_given TEXT,
        product_amount_given INTEGER,
        product_unit TEXT,
        product_code TEXT,
        product_description TEXT,
        product_description_other TEXT,
        prior_infusion_rate TEXT,
        infusion_rate TEXT,
        infusion_rate_adjustment TEXT,
        infusion_rate_adjustment_amount INTEGER,
        infusion_rate_unit TEXT,
        route TEXT,
        infusion_complete TEXT,
        completion_interval TEXT,
        new_iv_bag_hung TEXT,
        continued_infusion_in_other_location TEXT,
        restart_interval TEXT,
        side TEXT,
        site TEXT,
        non_formulary_visual_verification TEXT,
        PRIMARY KEY (subject_id, emar_id, emar_seq)
    );
"""
,
"emar": """
    CREATE TABLE IF NOT EXISTS emar (
        subject_id INTEGER,
        hadm_id INTEGER,
        emar_id TEXT,
        emar_seq INTEGER,
        poe_id TEXT,
        pharmacy_id INTEGER,
        enter_provider_id INTEGER,
        charttime DATETIME,
        medication TEXT,
        event_txt TEXT,
        scheduletime DATETIME,
        storetime DATETIME,
        PRIMARY KEY (subject_id, emar_id, emar_seq)
    );
"""
,
"hcpcsevents": """
    CREATE TABLE IF NOT EXISTS hcpcevents (
        subject_id INTEGER,
        hadm_id INTEGER,
        chartdate DATETIME,
        hcpcs_cd TEXT,
        seq_num INTEGER,
        short_description TEXT,
        PRIMARY KEY (subject_id, hadm_id, seq_num)
    );
"""
,
"labevents": """
    CREATE TABLE IF NOT EXISTS labevents (
        labevent_id INTEGER PRIMARY KEY,
        subject_id INTEGER,
        hadm_id INTEGER,
        specimen_id INTEGER,
        itemid INTEGER,
        order_provider_id TEXT,
        charttime DATETIME,
        storetime DATETIME,
        value TEXT,
        valuenum REAL,
        valueuom TEXT,
        ref_range_lower REAL,
        ref_range_upper REAL,
        flag TEXT,
        priority TEXT,
        comments TEXT
    );
"""
,
"microbiologyevents": """
    CREATE TABLE IF NOT EXISTS microbiologyevents (
        microevent_id INTEGER PRIMARY KEY,
        subject_id INTEGER,
        hadm_id INTEGER,
        micro_specimen_id INTEGER,
        order_provider_id TEXT,
        chartdate DATETIME,
        charttime DATETIME,
        spec_itemid INTEGER,
        spec_type_desc TEXT,
        test_seq INTEGER,
        storedate DATETIME,
        storetime DATETIME,
        test_itemid INTEGER,
        test_name TEXT,
        org_itemid INTEGER,
        org_name TEXT,
        isolate_num INTEGER,
        quantity INTEGER,
        ab_itemid INTEGER,
        ab_name TEXT,
        dilution_text TEXT,
        dilution_comparison TEXT,
        dilution_value TEXT,
        interpretation TEXT,
        comments TEXT
    );
"""
,
"omr": """
    CREATE TABLE IF NOT EXISTS omr (
        subject_id INTEGER,
        chartdate DATETIME,
        seq_num INTEGER,
        result_name TEXT,
        result_value TEXT
    );
"""
,
"patients": """
    CREATE TABLE IF NOT EXISTS patients (
        subject_id INTEGER PRIMARY KEY,
        gender TEXT,
        anchor_age INTEGER,
        anchor_year INTEGER,
        anchor_year_group TEXT,
        dod DATETIME
    );
""",
"pharmacy": """
    CREATE TABLE IF NOT EXISTS pharmacy (
        subject_id INTEGER,
        hadm_id INTEGER,
        pharmacy_id INTEGER PRIMARY KEY,
        poe_id TEXT,
        starttime DATETIME,
        stoptime DATETIME,
        medication TEXT,
        proc_type TEXT,
        status TEXT,
        entertime DATETIME,
        verifiedtime DATETIME,
        route TEXT,
        frequency TEXT,
        disp_sched TEXT,
        infusion_type TEXT,
        sliding_scale TEXT,
        lockout_interval INTEGER,
        basal_rate REAL,
        one_hr_max REAL,
        doses_per_24_hrs INTEGER,
        duration INTEGER,
        duration_interval TEXT,
        expiration_value INTEGER,
        expiration_unit TEXT,
        expirationdate TEXT,
        dispensation TEXT,
        fill_quantity TEXT
    );
"""
,
"poe_detail": """
    CREATE TABLE IF NOT EXISTS poe_detail (
        poe_id TEXT,
        poe_seq INTEGER,
        subject_id INTEGER,
        field_name TEXT,
        field_value TEXT
    );
"""
,
"poe": """
    CREATE TABLE IF NOT EXISTS poe (
        poe_id TEXT,
        poe_seq INTEGER,
        subject_id INTEGER,
        hadm_id INTEGER,
        ordertime DATETIME,
        order_type TEXT,
        order_subtype TEXT,
        transaction_type TEXT,
        discontinue_of_poe_id TEXT,
        discontinued_by_poe_id TEXT,
        order_provider_id TEXT,
        order_status TEXT
    );
"""
,
"prescriptions": """
    CREATE TABLE IF NOT EXISTS prescriptions (
        subject_id INTEGER,
        hadm_id INTEGER,
        pharmacy_id INTEGER,
        poe_id TEXT,
        poe_seq INTEGER,
        order_provider_id TEXT,
        starttime DATETIME,
        stoptime DATETIME,
        drug_type TEXT,
        drug TEXT,
        formulary_drug_cd TEXT,
        gsn TEXT,
        ndc TEXT,
        prod_strength TEXT,
        form_rx TEXT,
        dose_val_rx INTEGER,
        dose_unit_rx TEXT,
        form_val_disp INTEGER,
        form_unit_disp TEXT,
        doses_per_24_hrs INTEGER,
        route TEXT
    );
"""
,
"procedures_icd": """
    CREATE TABLE IF NOT EXISTS procedures_icd (
        subject_id INTEGER,
        hadm_id INTEGER,
        seq_num INTEGER,
        chartdate DATETIME,
        icd_code TEXT,
        icd_version INTEGER
    );
"""
,
"provider": """
    CREATE TABLE IF NOT EXISTS provider (
        provider_id TEXT PRIMARY KEY
    );
"""
,
"services": """
    CREATE TABLE IF NOT EXISTS services (
        subject_id INTEGER,
        hadm_id TEXT,
        transfertime DATETIME,
        prev_service TEXT,
        curr_service TEXT
    );
"""
,
"transfers": """
    CREATE TABLE IF NOT EXISTS transfers (
        subject_id INTEGER,
        hadm_id TEXT,
        transfer_id INTEGER PRIMARY KEY,
        eventtype TEXT,
        careunit TEXT,
        intime DATETIME,
        outtime DATETIME
    );
"""
,
"caregiver": """
    CREATE TABLE IF NOT EXISTS caregiver (
        caregiver_id INTEGER PRIMARY KEY
    );
"""
,
"chartevents": """
    CREATE TABLE IF NOT EXISTS chartevents (
        subject_id INTEGER,
        hadm_id TEXT,
        stay_id TEXT,
        caregiver_id INTEGER,
        charttime DATETIME,
        storetime DATETIME,
        itemid TEXT,
        value TEXT,
        valuenum REAL,
        valueuom TEXT,
        warning INTEGER
    );
"""
,
"d_items": """
    CREATE TABLE IF NOT EXISTS d_items (
        itemid TEXT,
        label TEXT,
        abbreviation TEXT,
        linksto TEXT,
        category TEXT,
        unitname TEXT,
        param_type TEXT,
        lownormalvalue REAL,
        highnormalvalue REAL
    );
"""
,
"datetimeevents": """
    CREATE TABLE IF NOT EXISTS datetimeevents (
        subject_id INTEGER,
        hadm_id TEXT,
        stay_id TEXT,
        caregiver_id TEXT,
        charttime DATETIME,
        storetime DATETIME,
        itemid TEXT,
        value TEXT,
        valueuom TEXT,
        warning TEXT
    );
"""
,
"icustays": """
    CREATE TABLE IF NOT EXISTS icustays (
        subject_id INTEGER,
        hadm_id TEXT,
        stay_id TEXT,
        first_careunit TEXT,
        last_careunit TEXT,
        intime DATETIME,
        outtime DATETIME,
        los REAL
    );
"""
,
"ingredientevents": """
    CREATE TABLE IF NOT EXISTS ingredientevents (
        subject_id INTEGER,
        hadm_id TEXT,
        stay_id TEXT,
        caregiver_id TEXT,
        starttime DATETIME,
        endtime DATETIME,
        storetime DATETIME,
        itemid TEXT,
        amount REAL,
        amountuom TEXT,
        rate REAL,
        rateuom TEXT,
        orderid TEXT,
        linkorderid TEXT,
        statusdescription TEXT,
        originalamount REAL,
        originalrate REAL
    );
"""
,
"inputevents": """
    CREATE TABLE IF NOT EXISTS inputevents (
        subject_id INTEGER,
        hadm_id TEXT,
        stay_id TEXT,
        caregiver_id TEXT,
        starttime DATETIME,
        endtime DATETIME,
        storetime DATETIME,
        itemid TEXT,
        amount REAL,
        amountuom TEXT,
        rate REAL,
        rateuom TEXT,
        orderid TEXT,
        linkorderid TEXT,
        ordercategoryname TEXT,
        secondaryordercategoryname TEXT,
        ordercomponenttypedescription TEXT,
        ordercategorydescription TEXT,
        patientweight REAL,
        totalamount REAL,
        totalamountuom TEXT,
        isopenbag INTEGER,
        continueinnextdept INTEGER,
        statusdescription TEXT,
        originalamount REAL,
        originalrate REAL
    );
"""
,
"outputevents": """
    CREATE TABLE IF NOT EXISTS outputevents (
        subject_id INTEGER,
        hadm_id TEXT,
        stay_id TEXT,
        caregiver_id TEXT,
        charttime DATETIME,
        storetime DATETIME,
        itemid TEXT,
        value REAL,
        valueuom TEXT
    );
"""
,
"procedureevents": """
    CREATE TABLE IF NOT EXISTS procedureevents (
        subject_id INTEGER,
        hadm_id TEXT,
        stay_id TEXT,
        caregiver_id TEXT,
        starttime DATETIME,
        endtime DATETIME,
        storetime DATETIME,
        itemid TEXT,
        value REAL,
        valueuom TEXT,
        location TEXT,
        locationcategory TEXT,
        orderid TEXT,
        linkorderid TEXT,
        ordercategoryname TEXT,
        ordercategorydescription TEXT,
        patientweight REAL,
        isopenbag INTEGER,
        continueinnextdept INTEGER,
        statusdescription TEXT,
        originalamount REAL,
        originalrate REAL
    );
"""
,
"diagnosis": """
    CREATE TABLE IF NOT EXISTS diagnosis (
        subject_id INTEGER,
        stay_id TEXT,
        seq_num INTEGER,
        icd_code TEXT,
        icd_version INTEGER,
        icd_title TEXT
    );
"""
,
"edstays": """
    CREATE TABLE IF NOT EXISTS edstays (
        subject_id INTEGER,
        hadm_id TEXT,
        stay_id TEXT,
        intime DATETIME,
        outtime DATETIME,
        gender TEXT,
        race TEXT,
        arrival_transport TEXT,
        disposition TEXT
    );
"""
,
"medrecon": """
    CREATE TABLE IF NOT EXISTS medrecon (
        subject_id INTEGER,
        stay_id TEXT,
        charttime DATETIME,
        name TEXT,
        gsn TEXT,
        ndc TEXT,
        etc_rn TEXT,
        etccode TEXT,
        etcdescription TEXT
    );
"""
,
"pyxis": """
    CREATE TABLE IF NOT EXISTS pyxis (
        subject_id INTEGER,
        stay_id TEXT,
        charttime DATETIME,
        med_rn TEXT,
        name TEXT,
        gsn_rn TEXT,
        gsn TEXT
    );
"""
,
"triage": """
    CREATE TABLE IF NOT EXISTS triage (
        subject_id INTEGER,
        stay_id TEXT,
        temperature REAL,
        heartrate REAL,
        resprate REAL,
        o2sat REAL,
        sbp REAL,
        dbp REAL,
        pain INTEGER,
        acuity REAL,
        chiefcomplaint TEXT
    );
"""
,
"vitalsign": """
    CREATE TABLE IF NOT EXISTS vitalsign (
        subject_id INTEGER,
        stay_subject_id INTEGER,
        charttime DATETIME,
        temperature REAL,
        heartrate REAL,
        resprate REAL,
        o2sat REAL,
        sbp REAL,
        dbp REAL,
        rhythm TEXT,
        pain INTEGER
    );
"""
,       
}
    # For each table name, create the table schema
    for _, table_name in csv_paths_and_table_names:

        if table_name not in table_name_to_schema:
            print(f"Definition for {table_name} not found")
            continue

        connection.execute(table_name_to_schema[table_name])
        print(f"Created table {table_name}.")

def insert_all_data(connection):
    # This function inserts data from CSV files into the corresponding tables with chunking
    csv_paths_and_table_names = get_csv_path_and_table_names()
    chunksize = 100000  # Size of each chunk
    
    for csv_file_path, table_name in csv_paths_and_table_names:
        # Use pd.read_csv to read the CSV in chunks
        for i, chunk in enumerate(pd.read_csv(csv_file_path, chunksize=chunksize, low_memory=False)):
            # Insert each chunk into the corresponding table
            chunk.to_sql(table_name, connection, if_exists="append", index=False)
            print(f"{i} Inserted a chunk of data into {table_name} - rows complete: ({(i + 1) * chunksize})")
        
        print(f"Inserted all data into {table_name}.")



def main():
    database_path = "./MIMIC_Database.db"

    with sqlite3.connect(database_path) as connection:
        if 0:
            drop_all_tables(connection)
        if 0:
            create_all_tables(connection)
        if 1:
            insert_all_data(connection)
        print("All tables processed successfully!")

if __name__ == "__main__":
    main()


