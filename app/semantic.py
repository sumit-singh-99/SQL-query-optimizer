import os
import json

# Load schema from JSON file
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '../schema/mock_schema.json')

try:
    with open(SCHEMA_PATH, 'r') as f:
        SCHEMA = json.load(f)
except FileNotFoundError:
    print(f"Error: Schema file not found at {SCHEMA_PATH}")
    SCHEMA = {}
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in schema file: {e}")
    SCHEMA = {}

def validate(ast):
    errors = []
    # Get the set of tables from the schema keys dynamically
    valid_tables = set(SCHEMA.keys())

    for stmt in ast:
        if stmt.get("type") == "SELECT":
            table_name = stmt.get("table")
            if table_name not in valid_tables:
                errors.append(f"Table '{table_name}' does not exist.")
        else:
            errors.append(f"Unsupported statement type: {stmt.get('type')}")
    return errors



def validate_select(stmt):
    table = stmt["table"]
    columns = stmt["columns"]
    where = stmt.get("where")
    errors = []

    if table not in SCHEMA:
        errors.append(f"Table '{table}' does not exist.")
        return errors  # Can't go further without a valid table

    table_columns = SCHEMA[table]["columns"]

    # Check selected columns
    if columns != ["*"]:
        for col in columns:
            if col not in table_columns:
                errors.append(f"Column '{col}' does not exist in table '{table}'.")

    # Check WHERE conditions
    if where:
        errors += validate_condition(where, table_columns)

    return errors


def validate_condition(cond, table_columns):
    errors = []

    cond_type = cond.get("type")

    # Fallback: assume simple condition if type is missing
    if cond_type is None and all(k in cond for k in ("left", "op", "right")):
        cond_type = "CONDITION"
        cond = {
            "type": "CONDITION",
            "column": cond["left"],
            "op": cond["op"],
            "value": cond["right"]
        }

    if cond_type == "CONDITION":
        column = cond["column"]
        if column not in table_columns:
            errors.append(f"Column '{column}' not found in table.")
    elif cond_type == "LOGIC":
        errors += validate_condition(cond["left"], table_columns)
        errors += validate_condition(cond["right"], table_columns)
    else:
        errors.append("Unknown condition type.")

    return errors
