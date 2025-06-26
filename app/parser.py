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
        if self.position < len(self.tokens) and self.peek()[0] == "WHERE":
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
        def parse_subquery():
            self.expect("LPAREN")
            self.expect("SELECT")
            columns = self.parse_columns()
            self.expect("FROM")
            table = self.expect("IDENTIFIER")[1]

            where = None
            if self.position < len(self.tokens) and self.peek()[0] == "WHERE":
                self.expect("WHERE")
                where = self.parse_condition()

            self.expect("RPAREN")
            return {
                "type": "SUBQUERY",
                "columns": columns,
                "table": table,
                "where": where
            }

        def parse_operand():
            if self.peek()[0] == "LPAREN":
                self.expect("LPAREN")
                expr = parse_expression()
                self.expect("RPAREN")
                return expr
            elif self.peek()[0] in ("NUMBER", "STRING", "IDENTIFIER"):
                tok_type, tok_val = self.expect(self.peek()[0])
                return {"type": tok_type, "value": tok_val}
            else:
                raise SyntaxError(f"Unexpected token in condition: {self.peek()[1]}")

        def parse_expression():
            left = parse_operand()
            while self.position < len(self.tokens) and self.peek()[0] in ("PLUS", "MINUS", "STAR", "SLASH"):
                op = self.expect(self.peek()[0])[1]
                right = parse_operand()
                left = {
                    "type": "EXPRESSION",
                    "op": op,
                    "left": left,
                    "right": right
                }
            return left

        def parse_atomic_condition():
            if self.peek()[0] == "LPAREN":
                self.expect("LPAREN")
                condition = self.parse_condition()
                self.expect("RPAREN")
                return condition

            left = parse_operand()

            if self.peek()[0] == "IN":
                self.expect("IN")
                subquery = parse_subquery()
                return {
                    "type": "CONDITION",
                    "op": "IN",
                    "left": left,
                    "right": subquery
                }

            op_type, op_val = self.peek()
            if op_type not in ("EQ", "NEQ", "LT", "GT", "LTE", "GTE"):
                raise SyntaxError(f"Expected comparison operator but got {op_type}")
            self.advance()

            right = parse_expression()

            return {
                "type": "CONDITION",
                "left": left,
                "op": op_val,
                "right": right
            }

        left_condition = parse_atomic_condition()

        while self.position < len(self.tokens) and self.peek()[0] in ("AND", "OR"):
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
