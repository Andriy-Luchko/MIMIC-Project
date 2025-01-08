from subquery import Subquery
class Query:
    """
    The Query class represents a collection of queries combined recursively using either 
    UNION or INTERSECT. It allows the building of complex queries by combining individual subqueries.
    """
    def __init__(self, queries, union_or_intersect="UNION"):
        """
        Initializes the Query object with a list of subqueries and the operation to combine them.

        :param queries: A list of Subquery or Query objects to be combined.
        :param union_or_intersect: The operation used to combine queries ("UNION" or "INTERSECT").
        """
        self.union_or_intersect = union_or_intersect
        self.queries = queries 

        if not all(isinstance(query, (Subquery, Query)) for query in self.queries):
            raise ValueError("All elements in queries must be Subquery or Query objects.")

    def combine_queries(self):
        """
        Recursively combines all subqueries using the specified operation (UNION or INTERSECT).
        Returns a string representing the combined query.

        :return: A string representing the combined query.
        """
        if len(self.queries) == 1:
            return self.queries[0].build_query()
        
        return f"\n{self.union_or_intersect}\n".join(["SELECT * FROM (\n" + query.build_query() + "\n)" for query in self.queries])

    def build_query(self):
        """
        Constructs the final query string by combining subqueries using UNION or INTERSECT.

        :return: A string representing the final query.
        """
        if not self.queries:
            raise ValueError("No queries have been added to the Query object.")

        return self.combine_queries()
