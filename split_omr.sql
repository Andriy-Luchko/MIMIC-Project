-- Insert data into patient_weight table, considering both 'Weight (Lbs)' and 'Weight'
INSERT INTO patient_weight (subject_id, chartdate, seq_num, weight_lbs)
SELECT subject_id, chartdate, seq_num, 
       CAST(result_value AS REAL)
FROM OMR
WHERE result_name IN ('Weight (Lbs)', 'Weight');

-- Insert data into patient_bmi table, considering both 'BMI (kg/m2)' and 'BMI'
INSERT INTO patient_bmi (subject_id, chartdate, seq_num, bmi_value)
SELECT subject_id, chartdate, seq_num, 
       CAST(result_value AS REAL)
FROM OMR
WHERE result_name IN ('BMI (kg/m2)', 'BMI');

-- Insert data into patient_height table, considering both 'Height (Inches)' and 'Height'
INSERT INTO patient_height (subject_id, chartdate, seq_num, height_inches)
SELECT subject_id, chartdate, seq_num, 
       CAST(result_value AS REAL)
FROM OMR
WHERE result_name IN ('Height (Inches)', 'Height');

INSERT INTO patient_eGFR
SELECT subject_id, chartdate, seq_num, CAST(result_value AS REAL)
FROM omr
WHERE result_name = 'eGFR';


-- Generic Blood Pressure
INSERT INTO patient_blood_pressure (subject_id, chartdate, seq_num, systolic, diastolic)
SELECT subject_id, chartdate, seq_num,
       CAST(SUBSTR(result_value, 1, INSTR(result_value, '/') - 1) AS INTEGER),
       CAST(SUBSTR(result_value, INSTR(result_value, '/') + 1) AS INTEGER)
FROM omr
WHERE result_name = 'Blood Pressure';

-- Sitting
INSERT INTO patient_blood_pressure_sitting (subject_id, chartdate, seq_num, systolic, diastolic)
SELECT subject_id, chartdate, seq_num,
       CAST(SUBSTR(result_value, 1, INSTR(result_value, '/') - 1) AS INTEGER),
       CAST(SUBSTR(result_value, INSTR(result_value, '/') + 1) AS INTEGER)
FROM omr
WHERE result_name = 'Blood Pressure Sitting';

-- Standing 1 min
INSERT INTO patient_blood_pressure_standing_1min (subject_id, chartdate, seq_num, systolic, diastolic)
SELECT subject_id, chartdate, seq_num,
       CAST(SUBSTR(result_value, 1, INSTR(result_value, '/') - 1) AS INTEGER),
       CAST(SUBSTR(result_value, INSTR(result_value, '/') + 1) AS INTEGER)
FROM omr
WHERE result_name = 'Blood Pressure Standing (1 min)';

-- Standing 3 mins
INSERT INTO patient_blood_pressure_standing_3mins (subject_id, chartdate, seq_num, systolic, diastolic)
SELECT subject_id, chartdate, seq_num,
       CAST(SUBSTR(result_value, 1, INSTR(result_value, '/') - 1) AS INTEGER),
       CAST(SUBSTR(result_value, INSTR(result_value, '/') + 1) AS INTEGER)
FROM omr
WHERE result_name = 'Blood Pressure Standing (3 mins)';

-- Standing (unspecified time)
INSERT INTO patient_blood_pressure_standing (subject_id, chartdate, seq_num, systolic, diastolic)
SELECT subject_id, chartdate, seq_num,
       CAST(SUBSTR(result_value, 1, INSTR(result_value, '/') - 1) AS INTEGER),
       CAST(SUBSTR(result_value, INSTR(result_value, '/') + 1) AS INTEGER)
FROM omr
WHERE result_name = 'Blood Pressure Standing';

-- Lying
INSERT INTO patient_blood_pressure_lying (subject_id, chartdate, seq_num, systolic, diastolic)
SELECT subject_id, chartdate, seq_num,
       CAST(SUBSTR(result_value, 1, INSTR(result_value, '/') - 1) AS INTEGER),
       CAST(SUBSTR(result_value, INSTR(result_value, '/') + 1) AS INTEGER)
FROM omr
WHERE result_name = 'Blood Pressure Lying';