def optimize(ast):
    optimized_ast = []
    for stmt in ast:
        if stmt.get("type") == "SELECT":
            optimized_ast.append(optimize_select(stmt))
        else:
            raise ValueError(f"Unsupported statement type: {stmt}")
    return optimized_ast



def optimize_select(stmt):
    # Remove duplicate columns (except '*')
    if "*" not in stmt["columns"]:
        stmt["columns"] = list(dict.fromkeys(stmt["columns"]))  # preserves order

    # Reorder conditions in WHERE clause if it exists
    if stmt.get("where"):
        stmt["where"] = reorder_conditions(stmt["where"])

    return stmt



def reorder_conditions(condition):
    """
    Recursively reorders AND conditions to push simpler ones first.
    Simplicity is estimated by assuming literals are cheaper than columns.
    """
    # If 'type' key not present or not LOGIC, treat as leaf condition
    if not isinstance(condition, dict) or condition.get("type") != "LOGIC":
        return condition

    left = reorder_conditions(condition["left"])
    right = reorder_conditions(condition["right"])

    def condition_cost(cond):
        # Leaf conditions expected to be dicts with 'right' key
        if not isinstance(cond, dict):
            return 3  # highest cost if unknown structure
        if isinstance(cond.get("right"), str) and cond["right"].isdigit():
            return 1  # likely indexed numeric
        elif isinstance(cond.get("right"), str):
            return 2  # string comparison
        else:
            return 3  # maybe another column or unknown

    if condition_cost(left) > condition_cost(right):
        # Swap to push cheaper condition first
        left, right = right, left

    return {
        "type": "LOGIC",
        "op": condition["op"],
        "left": left,
        "right": right
    }

def ast_to_sql(ast):
    """
    Convert AST back to an SQL query string.
    Supports only SELECT statements with optional WHERE.
    """
    def format_logic_condition(condition):
        if condition["type"] == "CONDITION":
            return f"{condition['column']} {condition['op']} {condition['value']}"
        elif condition["type"] == "LOGIC":
            left = format_logic_condition(condition["left"])
            right = format_logic_condition(condition["right"])
            return f"({left} {condition['op']} {right})"
        else:
            return "<unknown condition>"

    sql_statements = []
    for stmt in ast:
        if stmt["type"] == "SELECT":
            columns = ", ".join(stmt["columns"])
            table = stmt["table"]
            where = stmt.get("where")
            where_clause = ""
            if where:
                if "type" not in where:
                    # Support fallback for older condition format
                    where_clause = f" WHERE {where['left']} {where['op']} {where['right']}"
                elif where["type"] == "CONDITION":
                    where_clause = f" WHERE {where['column']} {where['op']} {where['value']}"
                elif where["type"] == "LOGIC":
                    where_clause = f" WHERE {format_logic_condition(where)}"
                else:
                    where_clause = ""
            sql = f"SELECT {columns} FROM {table}{where_clause};"
            sql_statements.append(sql)
        else:
            raise ValueError(f"Unsupported statement type: {stmt['type']}")
    return "\n".join(sql_statements)
