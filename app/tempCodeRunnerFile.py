def optimize(ast):
    optimized_ast = []
    for stmt in ast:
        if stmt.get("type") == "SELECT":
            stmt["optimization_log"] = []
            stmt["where"] = normalize_condition(stmt.get("where"))
            stmt = optimize_select(stmt)
            optimized_ast.append(stmt)
        else:
            raise ValueError(f"Unsupported statement type: {stmt}")
    return optimized_ast


def optimize_select(stmt):
    # Remove duplicate columns (except '*')
    if "*" not in stmt["columns"]:
        original_len = len(stmt["columns"])
        stmt["columns"] = list(dict.fromkeys(stmt["columns"]))  # preserves order
        if len(stmt["columns"]) < original_len:
            stmt["optimization_log"].append("Removed duplicate columns")

    # Reorder and simplify WHERE clause
    if stmt.get("where"):
        stmt["where"] = reorder_conditions(stmt["where"])
        stmt["where"] = constant_fold(stmt["where"])
        stmt["where"] = eliminate_redundant_condition(stmt["where"])

    # Subquery-to-Join optimization
    if stmt.get("where") and isinstance(stmt["where"], dict) and stmt["where"].get("op") == "IN":
        if isinstance(stmt["where"].get("right"), dict) and stmt["where"]["right"].get("type") == "SUBQUERY":
            stmt = convert_in_subquery_to_join(stmt)

    return stmt


def reorder_conditions(condition):
    if not isinstance(condition, dict) or condition.get("type") != "LOGIC":
        return condition

    left = reorder_conditions(condition["left"])
    right = reorder_conditions(condition["right"])

    def condition_cost(cond):
        if cond.get("type") != "CONDITION":
            return 3
        left_val = cond.get("left", {}).get("value", "")
        right_val = cond.get("right", {}).get("value", "")
        if str(left_val).isdigit() and str(right_val).isdigit():
            return 1
        elif str(right_val).isdigit():
            return 1
        return 2

    if condition_cost(left) > condition_cost(right):
        left, right = right, left

    return {
        "type": "LOGIC",
        "op": condition["op"],
        "left": left,
        "right": right
    }


def constant_fold(condition):
    if not isinstance(condition, dict):
        return condition

    if condition.get("type") == "CONDITION":
        try:
            left = condition.get("left")
            right = condition.get("right")
            if all(side.get("type") == "NUMBER" for side in [left, right]):
                result = eval(f"{left['value']} {condition['op']} {right['value']}")
                return {"type": "BOOLEAN", "value": result}
        except:
            pass
        return condition

    elif condition.get("type") == "LOGIC":
        condition["left"] = constant_fold(condition["left"])
        condition["right"] = constant_fold(condition["right"])
        return condition

    return condition


def eliminate_redundant_condition(condition):
    if not isinstance(condition, dict):
        return condition

    if condition.get("type") == "BOOLEAN":
        if condition["value"] is True:
            return None
        else:
            return {"type": "BOOLEAN", "value": False}

    if condition.get("type") == "CONDITION":
        l = condition.get("left", {})
        r = condition.get("right", {})
        if (
            l.get("type") == "NUMBER" and l.get("value") == "1"
            and r.get("type") == "NUMBER" and r.get("value") == "1"
            and condition.get("op") == "="
        ):
            return None

    if condition.get("type") == "LOGIC":
        left = eliminate_redundant_condition(condition["left"])
        right = eliminate_redundant_condition(condition["right"])

        if left is None:
            return right
        if right is None:
            return left
        return {
            "type": "LOGIC",
            "op": condition["op"],
            "left": left,
            "right": right
        }

    return condition


def convert_in_subquery_to_join(stmt):
    condition = stmt["where"]
    if not isinstance(condition, dict) or condition.get("op") != "IN":
        return stmt

    if not isinstance(condition.get("right"), dict):
        return stmt

    sub = condition["right"]
    if sub.get("type") != "SUBQUERY":
        return stmt

    main_col = condition.get("left")
    sub_columns = sub.get("columns", [])

    # Safely extract subquery's first column name
    if not sub_columns:
        return stmt
    sub_col = sub_columns[0]
    if isinstance(sub_col, dict):
        sub_col = sub_col.get("value", "<unknown_col>")

    sub_table = sub.get("table")
    sub_where = sub.get("where")

    stmt.setdefault("joins", []).append({
        "type": "JOIN",
        "table": sub_table,
        "on": {
            "left": main_col.get("value") if isinstance(main_col, dict) else str(main_col),
            "op": "=",
            "right": f"{sub_table}.{sub_col}"
        },
        "where": sub_where
    })

    stmt["where"] = None
    stmt["optimization_log"].append("Converted IN-subquery to JOIN")

    return stmt


def ast_to_sql(ast):
    def format_operand(operand):
        if not isinstance(operand, dict):
            return str(operand)
        if operand["type"] == "STRING":
            return f"'{operand['value']}'"
        return str(operand.get("value", "<unknown>"))

    def format_logic_condition(condition):
        if condition["type"] == "CONDITION":
            left = format_operand(condition["left"])
            right = format_operand(condition["right"])
            return f"{left} {condition['op']} {right}"
        elif condition["type"] == "LOGIC":
            left = format_logic_condition(condition["left"])
            right = format_logic_condition(condition["right"])
            return f"({left} {condition['op']} {right})"
        elif condition["type"] == "BOOLEAN":
            return "TRUE" if condition["value"] else "FALSE"
        else:
            return "<unknown condition>"

    sql_statements = []
    for stmt in ast:
        if stmt["type"] == "SELECT":
            columns = ", ".join(stmt["columns"])
            table = stmt["table"]
            where = stmt.get("where")
            where_clause = f" WHERE {format_logic_condition(where)}" if where else ""

            join_clause = ""
            if "joins" in stmt:
                join_strs = []
                for j in stmt["joins"]:
                    join_str = f"JOIN {j['table']} ON {j['on']['left']} {j['on']['op']} {j['on']['right']}"
                    if j.get("where"):
                        join_str += f" /* filter: {format_logic_condition(j['where'])} */"
                    join_strs.append(join_str)
                join_clause = " " + " ".join(join_strs)

            sql = f"SELECT {columns} FROM {table}{join_clause}{where_clause};"
            sql_statements.append(sql)
        else:
            raise ValueError(f"Unsupported statement type: {stmt['type']}")
    return "\n".join(sql_statements)


def normalize_condition(condition):
    if not isinstance(condition, dict):
        return condition

    if condition.get("type") == "LOGIC":
        left = normalize_condition(condition["left"])
        right = normalize_condition(condition["right"])
        return {
            "type": "LOGIC",
            "op": condition["op"],
            "left": left,
            "right": right
        }

    return condition
