-- ICU Tables
ALTER TABLE chartevents RENAME COLUMN stay_id TO icu_stay_id;
ALTER TABLE datetimeevents RENAME COLUMN stay_id TO icu_stay_id;
ALTER TABLE icustays RENAME COLUMN stay_id TO icu_stay_id;
ALTER TABLE ingredientevents RENAME COLUMN stay_id TO icu_stay_id;
ALTER TABLE inputevents RENAME COLUMN stay_id TO icu_stay_id;
ALTER TABLE outputevents RENAME COLUMN stay_id TO icu_stay_id;
ALTER TABLE procedureevents RENAME COLUMN stay_id TO icu_stay_id;

-- ED Tables
ALTER TABLE diagnosis RENAME COLUMN stay_id TO ed_stay_id;
ALTER TABLE edstays RENAME COLUMN stay_id TO ed_stay_id;
ALTER TABLE medrecon RENAME COLUMN stay_id TO ed_stay_id;
ALTER TABLE pyxis RENAME COLUMN stay_id TO ed_stay_id;
ALTER TABLE triage RENAME COLUMN stay_id TO ed_stay_id;
ALTER TABLE vitalsign RENAME COLUMN stay_id TO ed_stay_id;