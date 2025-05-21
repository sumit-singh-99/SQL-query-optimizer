class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def parse(self):
        ast = []
        while self.position < len(self.tokens):
            stmt = self.parse_statement()
            if stmt:
                ast.append(stmt)

            # Skip semicolon if present
            if self.position < len(self.tokens) and self.peek()[0] == "SEMICOLON":
                self.advance()

        return ast


    def parse_statement(self):
        token_type, token_value = self.peek()
        if token_type == "SELECT":
            return self.parse_select()
        else:
            raise SyntaxError(f"Unsupported SQL statement: {token_value}")

    def parse_select(self):
        self.expect("SELECT")

        columns = self.parse_columns()

        self.expect("FROM")
        table_name = self.expect("IDENTIFIER")[1]

        where_clause = None
        if self.peek()[0] == "WHERE":
            self.expect("WHERE")
            where_clause = self.parse_condition()

        return {
            "type": "SELECT",
            "columns": columns,
            "table": table_name,
            "where": where_clause
        }

    def parse_columns(self):
        columns = []
        if self.peek()[0] == "ASTERISK":
            self.expect("ASTERISK")
            return ["*"]

        while True:
            columns.append(self.expect("IDENTIFIER")[1])
            if self.peek()[0] == "COMMA":
                self.expect("COMMA")
            else:
                break
        return columns

    def parse_condition(self):
        def parse_atomic_condition():
            # If condition starts with a parenthesis, recursively parse the group
            if self.peek()[0] == "LPAREN":
                self.expect("LPAREN")
                condition = self.parse_condition()
                self.expect("RPAREN")
                return condition
            else:
                left = self.expect("IDENTIFIER")[1]
                operator_token = self.peek()
                if operator_token[0] not in ("EQ", "NEQ", "LT", "GT", "LTE", "GTE"):
                    raise SyntaxError(f"Expected comparison operator but got {operator_token[0]}")
                operator = operator_token[1]
                self.advance()

                right_type, right_value = self.peek()
                if right_type not in ("NUMBER", "STRING", "IDENTIFIER"):
                    raise SyntaxError(f"Unexpected token in WHERE clause: {right_value}")
                self.advance()

                return {
                    "left": left,
                    "op": operator,
                    "right": right_value
                }

        # Parse the left-hand side (either atomic or nested condition)
        left_condition = parse_atomic_condition()

        # Check for AND/OR to build logical tree
        while self.peek()[0] in ("AND", "OR"):
            logical_op = self.expect(self.peek()[0])[1]
            right_condition = self.parse_condition()
            left_condition = {
                "type": "LOGIC",
                "op": logical_op,
                "left": left_condition,
                "right": right_condition
            }

        return left_condition



    def peek(self):
        return self.tokens[self.position]

    def advance(self):
        self.position += 1

    def expect(self, expected_type):
        token = self.peek()
        if token[0] != expected_type:
            raise SyntaxError(f"Expected {expected_type} but got {token[0]}")
        self.advance()
        return token
