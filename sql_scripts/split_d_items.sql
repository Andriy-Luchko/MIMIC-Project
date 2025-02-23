-- Create new tables for each linksto value
CREATE TABLE chartevents_d_items (
    itemid INTEGER,
    label TEXT,
    abbreviation TEXT,
    category TEXT,
    unitname TEXT,
    param_type TEXT,
    lownormalvalue REAL,
    highnormalvalue REAL
);

CREATE TABLE datetimeevents_d_items (
    itemid INTEGER,
    label TEXT,
    abbreviation TEXT,
    category TEXT,
    unitname TEXT,
    param_type TEXT,
    lownormalvalue REAL,
    highnormalvalue REAL
);

CREATE TABLE ingredientevents_d_items (
    itemid INTEGER,
    label TEXT,
    abbreviation TEXT,
    category TEXT,
    unitname TEXT,
    param_type TEXT,
    lownormalvalue REAL,
    highnormalvalue REAL
);

CREATE TABLE inputevents_d_items (
    itemid INTEGER,
    label TEXT,
    abbreviation TEXT,
    category TEXT,
    unitname TEXT,
    param_type TEXT,
    lownormalvalue REAL,
    highnormalvalue REAL
);

CREATE TABLE procedureevents_d_items (
    itemid INTEGER,
    label TEXT,
    abbreviation TEXT,
    category TEXT,
    unitname TEXT,
    param_type TEXT,
    lownormalvalue REAL,
    highnormalvalue REAL
);

CREATE TABLE outputevents_d_items (
    itemid INTEGER,
    label TEXT,
    abbreviation TEXT,
    category TEXT,
    unitname TEXT,
    param_type TEXT,
    lownormalvalue REAL,
    highnormalvalue REAL
);

-- Insert data into respective tables
INSERT INTO chartevents_d_items
SELECT 
    itemid,
    label,
    abbreviation,
    category,
    unitname,
    param_type,
    lownormalvalue,
    highnormalvalue
FROM d_items
WHERE linksto = 'chartevents';

INSERT INTO datetimeevents_d_items
SELECT 
    itemid,
    label,
    abbreviation,
    category,
    unitname,
    param_type,
    lownormalvalue,
    highnormalvalue
FROM d_items
WHERE linksto = 'datetimeevents';

INSERT INTO ingredientevents_d_items
SELECT 
    itemid,
    label,
    abbreviation,
    category,
    unitname,
    param_type,
    lownormalvalue,
    highnormalvalue
FROM d_items
WHERE linksto = 'ingredientevents';

INSERT INTO inputevents_d_items
SELECT 
    itemid,
    label,
    abbreviation,
    category,
    unitname,
    param_type,
    lownormalvalue,
    highnormalvalue
FROM d_items
WHERE linksto = 'inputevents';

INSERT INTO procedureevents_d_items
SELECT 
    itemid,
    label,
    abbreviation,
    category,
    unitname,
    param_type,
    lownormalvalue,
    highnormalvalue
FROM d_items
WHERE linksto = 'procedureevent';

INSERT INTO outputevents_d_items
SELECT 
    itemid,
    label,
    abbreviation,
    category,
    unitname,
    param_type,
    lownormalvalue,
    highnormalvalue
FROM d_items
WHERE linksto = 'outputevents';