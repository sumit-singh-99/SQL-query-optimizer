def generate_ir(ast):
    ra_expressions = []
    for stmt in ast:
        if stmt.get("type") == "SELECT":
            where = stmt.get('where')
            if where:
                condition_str = condition_to_string(where)
                ra = f"π[{', '.join(stmt['columns'])}] (σ[{condition_str}] ({stmt['table']}))"
            else:
                ra = f"π[{', '.join(stmt['columns'])}] ({stmt['table']})"
            ra_expressions.append(ra)
        else:
            raise ValueError("Only SELECT statements are supported in IR.")
    return "\n".join(ra_expressions)


def generate_ir_select(stmt):
    return {
        "type": "SELECT",
        "columns": stmt["columns"],
        "table": stmt["table"],
        "where": format_condition_ir(stmt["where"]) if stmt.get("where") else None
    }


def format_condition_ir(condition):
    if condition is None:
        return None

    if condition.get("type") == "LOGIC":
        return {
            "type": "LOGIC",
            "op": condition["op"],
            "left": format_condition_ir(condition["left"]),
            "right": format_condition_ir(condition["right"]),
        }

    if condition.get("type") == "CONDITION":
        return {
            "type": "CONDITION",
            "left": condition["left"],
            "op": condition["op"],
            "right": condition["right"]
        }

    return {"type": "UNKNOWN_CONDITION", "content": condition}


def normalize_condition(condition):
    if condition is None:
        return None

    if condition.get("type") == "LOGIC":
        return {
            "type": "LOGIC",
            "op": condition["op"],
            "left": normalize_condition(condition["left"]),
            "right": normalize_condition(condition["right"]),
        }

    if "type" not in condition:
        return {
            "type": "CONDITION",
            "left": condition["left"],
            "op": condition["op"],
            "right": condition["right"]
        }

    return condition


def expression_to_string(expr):
    if expr is None:
        return "?"

    expr_type = expr.get("type")

    if expr_type in ("NUMBER", "STRING", "IDENTIFIER"):
        return str(expr.get("value"))

    if expr_type == "EXPRESSION":
        left = expression_to_string(expr.get("left"))
        right = expression_to_string(expr.get("right"))
        op = expr.get("op")
        return f"({left} {op} {right})"

    if expr_type == "SUBQUERY":
        cols = ", ".join(expr["columns"])
        table = expr["table"]
        where_clause = f" WHERE {condition_to_string(expr['where'])}" if expr.get("where") else ""
        return f"(SELECT {cols} FROM {table}{where_clause})"

    return "<unknown_expr>"


def condition_to_string(cond):
    if cond is None:
        return "?"

    cond_type = cond.get("type")

    if cond_type == "CONDITION":
        left = expression_to_string(cond.get("left"))
        right = expression_to_string(cond.get("right"))
        op = cond.get("op", "?")
        return f"{left} {op} {right}"

    if cond_type == "LOGIC":
        left_str = condition_to_string(cond["left"])
        right_str = condition_to_string(cond["right"])
        return f"({left_str} {cond['op']} {right_str})"

    if cond_type == "BOOLEAN":
        return "TRUE" if cond.get("value") else "FALSE"

    return "<unknown condition>"
