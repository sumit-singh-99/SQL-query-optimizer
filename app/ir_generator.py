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
    ir_stmt = {
        "type": "SELECT",
        "columns": stmt["columns"],
        "table": stmt["table"],
        "where": format_condition_ir(stmt["where"]) if stmt.get("where") else None
    }
    return ir_stmt


def format_condition_ir(condition):
    if condition is None:
        return None

    if condition["type"] == "LOGIC":
        return {
            "type": "LOGIC",
            "op": condition["op"],
            "left": format_condition_ir(condition["left"]),
            "right": format_condition_ir(condition["right"])
        }
    elif condition["type"] == "CONDITION":
        return {
            "type": "CONDITION",
            "column": condition["column"],
            "op": condition["op"],
            "value": condition["value"]
        }
    else:
        return {"type": "UNKNOWN_CONDITION", "content": condition}
    
def normalize_condition(condition):
    if condition is None:
        return None

    print("normalize_condition input:", condition)  # Debug print

    if isinstance(condition, dict) and condition.get("type") == "LOGIC":
        result = {
            "type": "LOGIC",
            "op": condition["op"],
            "left": normalize_condition(condition["left"]),
            "right": normalize_condition(condition["right"]),
        }
        print("normalize_condition output (LOGIC):", result)
        return result

    if isinstance(condition, dict) and "type" not in condition:
        result = {
            "type": "CONDITION",
            "column": condition["left"],
            "op": condition["op"],
            "value": condition["right"],
        }
        print("normalize_condition output (raw CONDITION):", result)
        return result

    print("normalize_condition output (as-is):", condition)
    return condition

def condition_to_string(cond):
    if cond["type"] == "LOGIC":
        left_str = condition_to_string(cond["left"])
        right_str = condition_to_string(cond["right"])
        return f"({left_str} {cond['op']} {right_str})"
    elif cond["type"] == "CONDITION":
        return f"{cond['column']} {cond['op']} {cond['value']}"
    else:
        raise ValueError(f"Unknown condition type: {cond}")
