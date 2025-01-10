import unittest
from subquery import Subquery, EqualityFilter, RangeFilter, ReadmissionFilter
from query import Query


class QueryTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_single_query(self):
        # Create a single subquery
        query1 = Subquery(
            table_column_pairs=[("patients", "subject_id"), ("admissions", "race")],
            filters=[
                RangeFilter("patients", "anchor_age", 30, 50),
                EqualityFilter("admissions", "race", "WHITE"),
            ],
        )

        # Create a query with just one subquery
        main_query = Query(queries=[query1], union_or_intersect="UNION")

        expected_query = """SELECT
patients.subject_id,
admissions.race
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
(patients.anchor_age BETWEEN 30 AND 50
AND
admissions.race = 'WHITE')"""

        self.assertEqual(main_query.build_query(), expected_query)

    def test_intersect_query(self):
        subquery1 = Subquery(
            table_column_pairs=[
                ("patients", "subject_id"),
                ("admissions", "race"),
                ("patients", "anchor_age"),
            ],
            filters=[RangeFilter("patients", "anchor_age", 50, 80)],
        )

        subquery2 = Subquery(
            table_column_pairs=[
                ("patients", "subject_id"),
                ("admissions", "race"),
                ("patients", "anchor_age"),
            ],
            filters=[EqualityFilter("admissions", "race", "WHITE")],
        )

        intersect_query = Query(
            queries=[subquery1, subquery2], union_or_intersect="INTERSECT"
        )

        expected_query = """SELECT * FROM (
SELECT
patients.subject_id,
admissions.race,
patients.anchor_age
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
(patients.anchor_age BETWEEN 50 AND 80)
)
INTERSECT
SELECT * FROM (
SELECT
patients.subject_id,
admissions.race,
patients.anchor_age
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
(admissions.race = 'WHITE')
)"""
        self.assertEqual(intersect_query.build_query(), expected_query)

    def test_union_query(self):
        subquery1 = Subquery(
            table_column_pairs=[("patients", "subject_id"), ("patients", "anchor_age")],
            filters=[RangeFilter("patients", "anchor_age", 0, 18)],
        )

        subquery2 = Subquery(
            table_column_pairs=[("patients", "subject_id"), ("patients", "anchor_age")],
            filters=[RangeFilter("patients", "anchor_age", 65, 120)],
        )

        union_query = Query(queries=[subquery1, subquery2], union_or_intersect="UNION")

        expected_query = """SELECT * FROM (
SELECT
patients.subject_id,
patients.anchor_age
FROM patients
WHERE
(patients.anchor_age BETWEEN 0 AND 18)
)
UNION
SELECT * FROM (
SELECT
patients.subject_id,
patients.anchor_age
FROM patients
WHERE
(patients.anchor_age BETWEEN 65 AND 120)
)"""

        self.assertEqual(union_query.build_query(), expected_query)

    def test_level_three_query(self):
        subquery1 = Subquery(
            table_column_pairs=[
                ("patients", "subject_id"),
                ("admissions", "race"),
                ("patients", "anchor_age"),
            ],
            filters=[RangeFilter("patients", "anchor_age", 0, 18)],
        )

        subquery2 = Subquery(
            table_column_pairs=[
                ("patients", "subject_id"),
                ("admissions", "race"),
                ("patients", "anchor_age"),
            ],
            filters=[RangeFilter("patients", "anchor_age", 65, 120)],
        )

        union_query = Query(queries=[subquery1, subquery2], union_or_intersect="UNION")

        subquery1 = Subquery(
            table_column_pairs=[
                ("patients", "subject_id"),
                ("admissions", "race"),
                ("patients", "anchor_age"),
            ],
            filters=[RangeFilter("patients", "anchor_age", 50, 80)],
        )

        subquery2 = Subquery(
            table_column_pairs=[
                ("patients", "subject_id"),
                ("admissions", "race"),
                ("patients", "anchor_age"),
            ],
            filters=[EqualityFilter("admissions", "race", "WHITE")],
        )

        intersect_query = Query(
            queries=[subquery1, subquery2], union_or_intersect="INTERSECT"
        )

        level_two_union_query = Query(
            queries=[union_query, intersect_query], union_or_intersect="UNION"
        )

        expected_query = """SELECT * FROM (
SELECT * FROM (
SELECT
patients.subject_id,
admissions.race,
patients.anchor_age
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
(patients.anchor_age BETWEEN 0 AND 18)
)
UNION
SELECT * FROM (
SELECT
patients.subject_id,
admissions.race,
patients.anchor_age
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
(patients.anchor_age BETWEEN 65 AND 120)
)
)
UNION
SELECT * FROM (
SELECT * FROM (
SELECT
patients.subject_id,
admissions.race,
patients.anchor_age
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
(patients.anchor_age BETWEEN 50 AND 80)
)
INTERSECT
SELECT * FROM (
SELECT
patients.subject_id,
admissions.race,
patients.anchor_age
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
(admissions.race = 'WHITE')
)
)"""

        self.assertEqual(level_two_union_query.build_query(), expected_query)

    def test_readmission_and_blood_pressure_query(self):
        # Create a readmission filter subquery
        readmission_filter = ReadmissionFilter(
            table_name="admissions", time_between_admissions="30"
        )

        # Create a subquery with the readmission filter
        query1 = Subquery(
            table_column_pairs=[
                ("patients", "subject_id"),
                ("admissions", "hadm_id"),
                ("patient_blood_pressure", "systolic"),
            ],
            filters=[readmission_filter],
        )

        # Create a subquery with a blood pressure filter (between 150 and 1e999)
        blood_pressure_filter = RangeFilter(
            table_name="patient_blood_pressure",
            column_name="systolic",
            min_value="150",
            max_value="1e999",
        )

        query2 = Subquery(
            table_column_pairs=[
                ("patients", "subject_id"),
                ("admissions", "hadm_id"),
                ("patient_blood_pressure", "systolic"),
            ],
            filters=[blood_pressure_filter],
        )

        # Combine the two subqueries with a UNION
        main_query = Query(queries=[query1, query2], union_or_intersect="INTERSECT")

        expected_query = """SELECT
patients.subject_id,
admissions.hadm_id
FROM patients, admissions
WHERE
patients.subject_id = admissions.subject_id
AND
admissions.hadm_id IN
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
UNION
SELECT
patients.subject_id,
patient_blood_pressure.systolic
FROM patients, patient_blood_pressure
WHERE
patients.subject_id = patient_blood_pressure.subject_id
AND
patient_blood_pressure.systolic BETWEEN 150 AND 1e999"""

        print(main_query.build_query())
        # self.assertEqual(main_query.build_query(), expected_query)


if __name__ == "__main__":
    unittest.main()
