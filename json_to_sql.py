import json

# Define the table relationships
TABLE_RELATIONSHIPS = {
    "root_table": "patients",
    
    "patient_subject_id_joins": [
        "admissions", "edstays", "patient_blood_pressure", "patient_blood_pressure_lying",
        "patient_blood_pressure_sitting", "patient_blood_pressure_standing",
        "patient_blood_pressure_standing_1min", "patient_blood_pressure_standing3mins",
        "patient_bmi", "patient_eGFR", "patient_height", "patient_weight", "labevents",
        "microbiologyevents", "radiology", "transfers"
    ],
    
    "admissions_hadm_id_joins": [
        "diagnoses_icd", "discharge", "drgcodes", "emar", "hcpcsevents", "icustays",
        "pharmacy", "poe", "procedures_icd", "services", "prescriptions"
    ],
    
    "edstays_ed_stay_id_joins": [
        "diagnosis", "medrecon", "pyxis", "triage", "vitalsign"
    ],
    
    "icustays_icu_stay_id_joins": [
        "outputevents", "datetimeevents", "chartevents", "ingredientevents",
        "procedureevents", "inputevents"
    ],
    
    "special_joins": {
        "d_hcpcs": {"parent": "hcpcsevents", "conditions": [("hcpcs_cd", "code")]},
        "d_icd_diagnoses": {
            "parents": ["diagnoses_icd", "diagnosis"],
            "conditions": [("icd_code", "icd_code"), ("icd_code", "icd_code")]
        },
        "d_icd_procedures": {"parent": "procedures_icd", "conditions": [("icd_code", "icd_code")]},
        "emar_detail": {"parent": "emar", "conditions": [("emar_id", "emar_id")]},
        "poe_detail": {"parent": "poe", "conditions": [("poe_id", "poe_id")]},
        "d_items": {
            "parents": ["chartevents", "datetimeevents", "ingredientevents", "inputevents", 
                       "procedureevents", "outputevents"],
            "conditions": [("itemid", "itemid")] * 6
        },
        "lab_items": {"parent": "poe", "conditions": [("poe_id", "poe_id")]}
    }
}

def get_table_parent(table_name, diagnosed_in):
    """Determine the parent table and join condition for a given table"""
    if table_name == TABLE_RELATIONSHIPS["root_table"]:
        return None, None
        
    # Check patient direct joins
    if table_name in TABLE_RELATIONSHIPS["patient_subject_id_joins"]:
        return "patients", ("subject_id", "subject_id")
        
    # Check admissions joins
    if table_name in TABLE_RELATIONSHIPS["admissions_hadm_id_joins"]:
        return "admissions", ("hadm_id", "hadm_id")
        
    # Check edstays joins
    if table_name in TABLE_RELATIONSHIPS["edstays_ed_stay_id_joins"]:
        return "edstays", ("ed_stay_id", "ed_stay_id")
        
    # Check icustays joins
    if table_name in TABLE_RELATIONSHIPS["icustays_icu_stay_id_joins"]:
        return "icustays", ("icu_stay_id", "icu_stay_id")
        
    # Check special joins
    if table_name in TABLE_RELATIONSHIPS["special_joins"]:
        special_join = TABLE_RELATIONSHIPS["special_joins"][table_name]
        if table_name == "d_icd_diagnoses":
            if diagnosed_in == "ed":
                return special_join["parents"][1], special_join["conditions"][1]
            return special_join["parents"][0], special_join["conditions"][0]
        
        return special_join["parent"], special_join["conditions"][0]

            
    return None, None

def recursive_join(table_name, from_tables, where_conditions, visited_tables, diagnosed_in):
    """Recursively determine necessary joins for a table"""
    if table_name in visited_tables:
        return
        
    visited_tables.add(table_name)
    
    parent_table, join_condition = get_table_parent(table_name, diagnosed_in)
    
    if parent_table is None:
        if table_name not in from_tables:
            from_tables.append(table_name)
        return
        
    # Recursively join parent table first
    recursive_join(parent_table, from_tables, where_conditions, visited_tables, diagnosed_in)
    
    # Add current table and join condition
    if table_name not in from_tables:
        from_tables.append(table_name)
        
    where_conditions.append(
        f"{parent_table}.{join_condition[0]} = {table_name}.{join_condition[1]}"
    )

def needs_icd_joins(filters, select_tables):
    """Check if ICD diagnosis tables need to be joined based on usage"""
    # Check if d_icd_diagnoses is directly referenced
    if "d_icd_diagnoses" in select_tables:
        return True
        
    # Check filters for ICD references
    def check_filters(filter_list):
        for filter_obj in filter_list:
            if filter_obj["table"] == "d_icd_diagnoses":
                return True
        return False
    
    return check_filters(filters)

def build_filter_query(filters, operator, select_columns, select_tables, diagnosed_in=None):
    """Builds a query from a set of filters with proper table joins"""
    from_tables = []
    where_conditions = []
    visited_tables = set()
    
    # Add tables from filters and selected tables
    needed_tables = set(filter_obj["table"] for filter_obj in filters)
    needed_tables.update(select_tables)
    
    # Only add diagnosis tables if ICD codes are being used
    if needs_icd_joins(filters, select_tables):
        if diagnosed_in == "ed":
            needed_tables.add("diagnosis")
            needed_tables.add("edstays")
        elif diagnosed_in == "hospital":
            needed_tables.add("diagnoses_icd")
            needed_tables.add("admissions")
    
    # Recursively add all necessary tables and joins
    for table in needed_tables:
        recursive_join(table, from_tables, where_conditions, visited_tables, diagnosed_in)
    
    # Add filter conditions
    filter_conditions = [filter_to_sql(filter_obj) for filter_obj in filters]
    
    # Construct the query
    query = f"SELECT {select_columns}\nFROM " + ", ".join(from_tables)
    
    # Add WHERE clause if we have conditions
    if where_conditions or filter_conditions:
        all_conditions = [cond for cond in where_conditions if not cond.startswith("LEFT JOIN")]
        left_joins = [cond for cond in where_conditions if cond.startswith("LEFT JOIN")]
        
        if left_joins:
            query += "\n" + "\n".join(left_joins)
        
        if all_conditions or filter_conditions:
            query += "\nWHERE " + "\nAND ".join(all_conditions)
            if filter_conditions:
                if all_conditions:
                    query += f"\nAND ({f'\n{operator} '.join(filter_conditions)})"
                else:
                    query += f"({f'\n{operator} '.join(filter_conditions)})"
    
    return query

def filter_to_sql(filter_obj):
    """Converts a filter object to its SQL representation"""
    if filter_obj["filter_type"] == "range":
        return f"{filter_obj['table']}.{filter_obj['column']} BETWEEN {filter_obj['min']} AND {filter_obj['max']}"
    elif filter_obj["filter_type"] == "value":
        return f"{filter_obj['table']}.{filter_obj['column']} = '{filter_obj['value']}'"
    else:
        raise ValueError(f"Unknown filter type: {filter_obj['filter_type']}")

def query_to_sql(query, select_columns, select_tables, diagnosed_in=None):
    """Takes in a query object and converts it to SQL with proper table joins"""
    subqueries = query.get("subqueries", [])
    filters = query.get("filters", [])
    operator = query.get("operator", "AND")
    
    # List to hold all parts of the query
    query_parts = []
    
    # Check if any subquery needs ICD joins
    def check_subqueries_for_icd(query_obj):
        if needs_icd_joins(query_obj["filters"], select_tables):
            return True
        return any(check_subqueries_for_icd(sq) for sq in query_obj["subqueries"])
    
    # If we have filters, build a query from them
    if filters:
        filter_query = build_filter_query(filters, operator, select_columns, select_tables, 
                                        diagnosed_in if check_subqueries_for_icd(query) else None)
        query_parts.append(f"SELECT * FROM (\n{filter_query}\n)")
    
    # Process all subqueries
    if subqueries:
        for subquery in subqueries:
            subquery_sql = query_to_sql(subquery, select_columns, select_tables, 
                                      diagnosed_in if check_subqueries_for_icd(subquery) else None)
            query_parts.append(f"SELECT * FROM (\n{subquery_sql}\n)")
    
    # Combine all parts with the operator
    if query_parts:
        return f"\n{"UNION" if operator == "OR" else "INTERSECT"}\n".join(query_parts)
    else:
        # If no filters or subqueries, return a basic SELECT with proper joins
        return build_filter_query([], operator, select_columns, select_tables, 
                                diagnosed_in if check_subqueries_for_icd(query) else None)

def get_select_columns(query_object):
    """
    Constructs the SELECT clause of the SQL query based on the selected tables and columns.
    """
    select_columns = []
    for table in query_object["select_tables"]:
        for column in table["columns"]:
            select_columns.append(f"{table['name']}.{column}")

    return ", ".join(select_columns)

def json_to_sql(query_object):
    """
    Converts a query to an SQL statement.
    """
    select_columns = get_select_columns(query_object)
    select_tables = set(table["name"] for table in query_object["select_tables"])
    diagnosed_in = query_object.get("diagnosed_in")  # Get the diagnosis location

    return query_to_sql(query_object["query"], select_columns, select_tables, diagnosed_in)



def main():
    query_json = """
    {
  "diagnosed_in": "hospital",
  "select_tables": [
    {
      "name": "patients",
      "columns": ["subject_id", "anchor_age"]
    },
    {
      "name": "admissions", 
      "columns": ["race"]
    },
    {
      "name": "d_icd_diagnoses",
      "columns": ["long_title"]
    }
  ],
  "query": {
    "operator": "AND",
    "filters": [],
    "subqueries": [
      {
        "operator": "OR",
        "filters": [
          {
            "filter_type": "range",
            "table": "patients",
            "column": "anchor_age",
            "min": 0,
            "max": 18
          },
          {
            "filter_type": "range",
            "table": "patients",
            "column": "anchor_age",
            "min": 65,
            "max": 120
          }
        ],
        "subqueries": []
      },
      {
        "operator": "AND",
        "filters": [
          {
            "filter_type": "range",
            "table": "patients",
            "column": "anchor_age",
            "min": 50,
            "max": 80
          },
          {
            "filter_type": "value",
            "table": "admissions",
            "column": "race",
            "value": "WHITE"
          }
        ],
        "subqueries": [
          {
            "operator": "OR",
            "filters": [
              {
                "filter_type": "value",
                "table": "d_icd_diagnoses",
                "column": "long_title",
                "value": "Pneumonia due to Streptococcus pneumoniae"
              },
              {
                "filter_type": "value",
                "table": "d_icd_diagnoses",
                "column": "long_title",
                "value": "Pneumonia due to Hemophilus influenzae"
              }
            ],
            "subqueries": []
          }
        ]
      }
    ]
  }
}
    """
    print(json_to_sql(query_json))


if __name__ == "__main__":
    main()
