import os


def save_to_file(content, filepath):
    """
    Saves the given content string to the specified filepath.
    Creates parent directories if they don't exist.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)


def ast_to_sql(ast):
    """
    Converts the AST back into an SQL query string.
    Assumes the AST structure from your parser:
    [
        {
            "type": "SELECT",
            "columns": [...],
            "table": "...",
            "where": {...} or None
        },
        ...
    ]
    """

    def condition_to_str(cond):
        # cond can be a simple condition dict or a logical condition dict
        if cond is None:
            return ""

        if cond.get("type") == "LOGIC":
            left = condition_to_str(cond["left"])
            right = condition_to_str(cond["right"])
            op = cond["op"]
            return f"({left} {op} {right})"

        # Simple condition: {'left': ..., 'op': ..., 'right': ...}
        left = cond["left"]
        op = cond["op"]
        right = cond["right"]
        # Add quotes if right is string literal
        if isinstance(right, str) and not right.isdigit():
            right_str = f"'{right}'"
        else:
            right_str = str(right)
        return f"{left} {op} {right_str}"

    sql_statements = []

    for stmt in ast:
        if stmt["type"] == "SELECT":
            cols = ", ".join(stmt["columns"]) if stmt["columns"] != ["*"] else "*"
            table = stmt["table"]
            where_str = ""
            if stmt.get("where"):
                where_str = " WHERE " + condition_to_str(stmt["where"])
            sql = f"SELECT {cols} FROM {table}{where_str};"
            sql_statements.append(sql)
        else:
            # Unsupported statement types are ignored here
            continue

    return "\n".join(sql_statements)
