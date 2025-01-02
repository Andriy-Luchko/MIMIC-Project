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
    hospital_expire_flag INTEGER
);

CREATE TABLE IF NOT EXISTS d_hcpcs (
    code TEXT,
    category INTEGER,
    long_description TEXT,
    short_description TEXT
);

CREATE TABLE IF NOT EXISTS d_icd_diagnoses (
    icd_code TEXT,
    icd_version INTEGER,
    long_title TEXT
);

CREATE TABLE IF NOT EXISTS d_icd_procedures (
    icd_code TEXT,
    icd_version INTEGER,
    long_title TEXT
);

CREATE TABLE IF NOT EXISTS d_labitems (
    itemid INTEGER,
    label TEXT,
    fluid TEXT,
    category TEXT
);

CREATE TABLE IF NOT EXISTS diagnoses_icd (
    subject_id INTEGER,
    hadm_id INTEGER,
    seq_num INTEGER,
    icd_code TEXT,
    icd_version INTEGER
);

CREATE TABLE IF NOT EXISTS drgcodes (
    subject_id INTEGER,
    hadm_id INTEGER,
    drg_type TEXT,
    drg_code INTEGER,
    description TEXT,
    drg_severity INTEGER,
    drg_mortality INTEGER
);

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
    non_formulary_visual_verification TEXT
);

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
    storetime DATETIME
);

CREATE TABLE IF NOT EXISTS hcpcsevents (
    subject_id INTEGER,
    hadm_id INTEGER,
    chartdate DATETIME,
    hcpcs_cd TEXT,
    seq_num INTEGER,
    short_description TEXT
);

CREATE TABLE IF NOT EXISTS labevents (
    labevent_id INTEGER,
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

CREATE TABLE IF NOT EXISTS microbiologyevents (
    microevent_id INTEGER,
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

CREATE TABLE IF NOT EXISTS omr (
    subject_id INTEGER,
    chartdate DATETIME,
    seq_num INTEGER,
    result_name TEXT,
    result_value TEXT
);

CREATE TABLE IF NOT EXISTS patients (
    subject_id INTEGER,
    gender TEXT,
    anchor_age INTEGER,
    anchor_year INTEGER,
    anchor_year_group TEXT,
    dod DATETIME
);

CREATE TABLE IF NOT EXISTS pharmacy (
    subject_id INTEGER,
    hadm_id INTEGER,
    pharmacy_id INTEGER,
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

CREATE TABLE IF NOT EXISTS poe_detail (
    poe_id TEXT,
    poe_seq INTEGER,
    subject_id INTEGER,
    field_name TEXT,
    field_value TEXT
);

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

CREATE TABLE IF NOT EXISTS procedures_icd (
    subject_id INTEGER,
    hadm_id INTEGER,
    seq_num INTEGER,
    chartdate DATETIME,
    icd_code TEXT,
    icd_version INTEGER
);

CREATE TABLE IF NOT EXISTS provider (
    provider_id TEXT
);

CREATE TABLE IF NOT EXISTS services (
    subject_id INTEGER,
    hadm_id TEXT,
    transfertime DATETIME,
    prev_service TEXT,
    curr_service TEXT
);

CREATE TABLE IF NOT EXISTS transfers (
    subject_id INTEGER,
    hadm_id TEXT,
    transfer_id INTEGER,
    eventtype TEXT,
    careunit TEXT,
    intime DATETIME,
    outtime DATETIME
);

CREATE TABLE IF NOT EXISTS caregiver (
    caregiver_id INTEGER
);

CREATE TABLE IF NOT EXISTS chartevents (
    subject_id INTEGER,
    hadm_id TEXT,
    stay_id INTEGER,
    caregiver_id INTEGER,
    charttime DATETIME,
    storetime DATETIME,
    itemid TEXT,
    value TEXT,
    valuenum REAL,
    valueuom TEXT,
    warning INTEGER
);

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

CREATE TABLE IF NOT EXISTS datetimeevents (
    subject_id INTEGER,
    hadm_id TEXT,
    stay_id INTEGER,
    caregiver_id TEXT,
    charttime DATETIME,
    storetime DATETIME,
    itemid TEXT,
    value TEXT,
    valueuom TEXT,
    warning TEXT
);

CREATE TABLE IF NOT EXISTS icustays (
    subject_id INTEGER,
    hadm_id TEXT,
    stay_id INTEGER,
    first_careunit TEXT,
    last_careunit TEXT,
    intime DATETIME,
    outtime DATETIME,
    los REAL
);

CREATE TABLE IF NOT EXISTS ingredientevents (
    subject_id INTEGER,
    hadm_id TEXT,
    stay_id INTEGER,
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

CREATE TABLE IF NOT EXISTS inputevents (
    subject_id INTEGER,
    hadm_id TEXT,
    stay_id INTEGER,
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

CREATE TABLE IF NOT EXISTS outputevents (
    subject_id INTEGER,
    hadm_id TEXT,
    stay_id INTEGER,
    caregiver_id TEXT,
    charttime DATETIME,
    storetime DATETIME,
    itemid TEXT,
    value REAL,
    valueuom TEXT
);

CREATE TABLE IF NOT EXISTS procedureevents (
    subject_id INTEGER,
    hadm_id TEXT,
    stay_id INTEGER,
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

CREATE TABLE IF NOT EXISTS diagnosis (
    subject_id INTEGER,
    stay_id INTEGER,
    seq_num INTEGER,
    icd_code TEXT,
    icd_version INTEGER,
    icd_title TEXT
);

CREATE TABLE IF NOT EXISTS edstays (
    subject_id INTEGER,
    hadm_id TEXT,
    stay_id INTEGER,
    intime DATETIME,
    outtime DATETIME,
    gender TEXT,
    race TEXT,
    arrival_transport TEXT,
    disposition TEXT
);

CREATE TABLE IF NOT EXISTS medrecon (
    subject_id INTEGER,
    stay_id INTEGER,
    charttime DATETIME,
    name TEXT,
    gsn TEXT,
    ndc TEXT,
    etc_rn TEXT,
    etccode TEXT,
    etcdescription TEXT
);

CREATE TABLE IF NOT EXISTS pyxis (
    subject_id INTEGER,
    stay_id INTEGER,
    charttime DATETIME,
    med_rn TEXT,
    name TEXT,
    gsn_rn TEXT,
    gsn TEXT
);

CREATE TABLE IF NOT EXISTS triage (
    subject_id INTEGER,
    stay_id INTEGER,
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

CREATE TABLE IF NOT EXISTS vitalsign (
    subject_id INTEGER,
    stay_id INTEGER,
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

CREATE TABLE IF NOT EXISTS discharge (
    note_id TEXT,
    subject_id INTEGER,
    hadm_id INTEGER,
    note_type TEXT,
    note_seq INTEGER,
    charttime DATETIME,
    storetime DATETIME,
    text TEXT
);

CREATE TABLE IF NOT EXISTS radiology (
    note_id TEXT,
    subject_id INTEGER,
    hadm_id INTEGER,
    note_type TEXT,
    note_seq INTEGER,
    charttime DATETIME,
    storetime DATETIME,
    text TEXT
);
