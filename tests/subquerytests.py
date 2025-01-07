import unittest
from subquery import Subquery

class TestSubquery(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_create_name_to_table_map(self):
        table_map = Subquery.create_name_to_table_map()
        self.assertEqual(len(table_map), 46)  

    def test_build_subquery_with_equality_filter(self):
        table_column_pairs = [
            ("patients", "subject_id"),
            ("admissions", "hadm_id"),
        ]

        filters = [
            ("patients", "subject_id", 10000032)
        ]

        subquery = Subquery(table_column_pairs, filters)
        query = subquery.build_query()
        expected_query = """SELECT 
patients.subject_id,
admissions.hadm_id FROM patients, admissions WHERE 
patients.subject_id = admissions.subject_id AND
(patients.subject_id = '10000032')"""

        self.assertEqual(query.strip(), expected_query.strip())

    def test_build_subquery_with_range_filter(self):
        table_column_pairs = [
            ("patients", "age"),
            ("admissions", "hadm_id"),
        ]

        filters = [
            ("patients", "age", 18, 65)
        ]

        subquery = Subquery(table_column_pairs, filters)
        query = subquery.build_query()
        expected_query = """SELECT 
patients.age,
admissions.hadm_id FROM patients, admissions WHERE 
patients.subject_id = admissions.subject_id AND
(patients.age BETWEEN 18 AND 65)"""

        self.assertEqual(query.strip(), expected_query.strip())

    def test_build_subquery_with_d_icd(self):
        table_column_pairs = [
            ("patients", "subject_id"),
            ("admissions", "hadm_id"),
            ("diagnoses_icd", "icd_code"),
            ("edstays", "ed_stay_id"),
            ("diagnosis", "icd_code"),
            ("d_icd_diagnoses", "icd_version"),
            ("d_icd_diagnoses", "icd_code"),
            ("d_icd_diagnoses", "long_title"),
        ]

        filters = [
            ("d_icd_diagnoses", "icd_code", "4589")
        ]

        subquery = Subquery(table_column_pairs, filters)
        query = subquery.build_query()
        expected_query = """SELECT 
patients.subject_id,
admissions.hadm_id,
diagnoses_icd.icd_code,
edstays.ed_stay_id,
diagnosis.icd_code,
d_icd_diagnoses.icd_version,
d_icd_diagnoses.icd_code,
d_icd_diagnoses.long_title FROM patients, admissions, diagnoses_icd, edstays, diagnosis, d_icd_diagnoses WHERE 
patients.subject_id = admissions.subject_id AND
admissions.hadm_id = diagnoses_icd.hadm_id AND
patients.subject_id = edstays.subject_id AND
edstays.ed_stay_id = diagnosis.ed_stay_id AND
diagnoses_icd.icd_code = d_icd_diagnoses.icd_code AND
diagnosis.icd_code = d_icd_diagnoses.icd_code AND
(d_icd_diagnoses.icd_code = '4589')"""

        self.assertEqual(query.strip(), expected_query.strip())
        
    def test_build_subquery_with_or_filter(self):
        table_column_pairs = [
            ("patients", "subject_id"),
            ("admissions", "hadm_id"),
        ]
        
        # Using an OR filter combination
        filters = [
            ("patients", "subject_id", 10000032),
            ("patients", "subject_id", 10000033)
        ]
        
        # Create the Subquery with 'OR' as the filter combination
        subquery = Subquery(table_column_pairs, filters, filter_combination="OR")
        query = subquery.build_query()
        
        expected_query = """SELECT 
patients.subject_id,
admissions.hadm_id FROM patients, admissions WHERE 
patients.subject_id = admissions.subject_id OR
(patients.subject_id = '10000032' OR
patients.subject_id = '10000033')"""
        
        self.assertEqual(query.strip(), expected_query.strip())

if __name__ == "__main__":
    unittest.main()
