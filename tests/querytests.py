import unittest
from subquery import Subquery
from query import Query

class QueryTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        
    def test_single_query(self):
        # Create a single subquery
        query1 = Subquery(
            table_column_pairs=[("patients", "subject_id"), ("admissions", "race")],
            filters=[("patients", "anchor_age", 30, 50), ("admissions", "race", "WHITE")],
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
            table_column_pairs=[("patients", "subject_id"), ("admissions", "race"), ('patients', "anchor_age")],
            filters=[("patients", "anchor_age", 50, 80)]
        )

        subquery2 = Subquery(
            table_column_pairs=[("patients", "subject_id"), ("admissions", "race"), ('patients', "anchor_age")],
            filters=[("admissions", "race", "WHITE")]
        )

        intersect_query = Query(queries=[subquery1, subquery2], union_or_intersect="INTERSECT")

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
            table_column_pairs=[("patients", "subject_id"), ('patients', "anchor_age")],
            filters=[("patients", "anchor_age", 0, 18)]
        )

        subquery2 = Subquery(
            table_column_pairs=[("patients", "subject_id"), ('patients', "anchor_age")],
            filters=[("patients", "anchor_age", 65, 120)]
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
            table_column_pairs=[("patients", "subject_id"), ("admissions", "race"), ('patients', "anchor_age")],
            filters=[("patients", "anchor_age", 0, 18)]
        )

        subquery2 = Subquery(
            table_column_pairs=[("patients", "subject_id"), ("admissions", "race"), ('patients', "anchor_age")],
            filters=[("patients", "anchor_age", 65, 120)]
        )

        union_query = Query(queries=[subquery1, subquery2], union_or_intersect="UNION")

        subquery1 = Subquery(
            table_column_pairs=[("patients", "subject_id"), ("admissions", "race"), ('patients', "anchor_age")],
            filters=[("patients", "anchor_age", 50, 80)]
        )

        subquery2 = Subquery(
            table_column_pairs=[("patients", "subject_id"), ("admissions", "race"), ('patients', "anchor_age")],
            filters=[("admissions", "race", "WHITE")]
        )

        intersect_query = Query(queries=[subquery1, subquery2], union_or_intersect="INTERSECT")
        
        level_two_union_query = Query(queries=[union_query, intersect_query], union_or_intersect="UNION")
        
        expected_query = """"""

        self.assertEqual(level_two_union_query.build_query(), expected_query)
if __name__ == "__main__":
    unittest.main()
    QueryTests.test_level_three_query()