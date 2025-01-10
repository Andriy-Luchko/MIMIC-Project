import unittest
from subquery import Subquery, EqualityFilter, RangeFilter, ReadmissionFilter


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

        filters = [EqualityFilter("patients", "subject_id", 10000032)]

        subquery = Subquery(table_column_pairs, filters)
        query = subquery.build_query()
        expected_query = """SELECT
patients.subject_id,
admissions.hadm_id
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
(patients.subject_id = '10000032')"""

        self.assertEqual(query.strip(), expected_query.strip())

    def test_build_subquery_with_range_filter(self):
        table_column_pairs = [
            ("patients", "age"),
            ("admissions", "hadm_id"),
        ]

        filters = [RangeFilter("patients", "age", 18, 65)]

        subquery = Subquery(table_column_pairs, filters)
        query = subquery.build_query()
        expected_query = """SELECT
patients.age,
admissions.hadm_id
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
(patients.age BETWEEN 18 AND 65)"""

        self.assertEqual(query.strip(), expected_query.strip())

    def test_build_subquery_with_d_icd(self):
        table_column_pairs = [
            ("patients", "subject_id"),
            ("admissions", "hadm_id"),
            ("diagnoses_icd", "icd_code"),
        ]

        filters = [EqualityFilter("d_icd_diagnoses", "icd_code", "4589")]

        subquery = Subquery(table_column_pairs, filters)
        query = subquery.build_query()
        expected_query = """SELECT
patients.subject_id,
admissions.hadm_id,
diagnoses_icd.icd_code
FROM patients, admissions, diagnoses_icd, d_icd_diagnoses, diagnosis, edstays
WHERE
patients.subject_id = admissions.subject_id
AND
admissions.hadm_id = diagnoses_icd.hadm_id
AND
diagnoses_icd.icd_code = d_icd_diagnoses.icd_code
AND
diagnosis.icd_code = d_icd_diagnoses.icd_code
AND
edstays.ed_stay_id = diagnosis.ed_stay_id
AND
patients.subject_id = edstays.subject_id
AND
(d_icd_diagnoses.icd_code = '4589')"""

        self.assertEqual(query.strip(), expected_query.strip())

    def test_build_subquery_with_or_filter(self):
        table_column_pairs = [
            ("patients", "subject_id"),
            ("admissions", "hadm_id"),
        ]

        filters = [
            EqualityFilter("patients", "subject_id", 10000032),
            EqualityFilter("patients", "subject_id", 10000033),
        ]

        subquery = Subquery(table_column_pairs, filters, filter_combination="OR")
        query = subquery.build_query()

        expected_query = """SELECT
patients.subject_id,
admissions.hadm_id
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
(patients.subject_id = '10000032'
OR
patients.subject_id = '10000033')"""

        self.assertEqual(query.strip(), expected_query.strip())

    def test_to_sql_basic(self):
        table_column_pairs = [("admissions", "hadm_id")]

        filters = [
            ReadmissionFilter(table_name="admissions", time_between_admissions=30)
        ]
        subquery = Subquery(table_column_pairs, filters)
        query = subquery.build_query()
        expected_query = """SELECT
admissions.hadm_id
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
(admissions.hadm_id IN
(
	SELECT * FROM (
		SELECT a.hadm_id
		FROM admissions a
		JOIN admissions a2
		WHERE CAST((julianday(a2.admittime) - julianday(a.admittime)) AS REAL) < 30
		AND CAST((julianday(a2.admittime) - julianday(a.admittime)) AS REAL) > 0
		AND a.hadm_id != a2.hadm_id
		AND a.subject_id = a2.subject_id
	UNION
		SELECT a.hadm_id
		FROM admissions a
		JOIN admissions a2
		WHERE CAST((julianday(a.admittime) - julianday(a2.admittime)) AS REAL) < 30
		AND CAST((julianday(a.admittime) - julianday(a2.admittime)) AS REAL) > 0
		AND a.hadm_id != a2.hadm_id
		AND a.subject_id = a2.subject_id
	)
)
)"""
        # print(query)
        self.assertEqual(query.strip(), expected_query.strip())


if __name__ == "__main__":
    unittest.main()
