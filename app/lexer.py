import re

# Define token patterns
TOKEN_SPECIFICATION = [
    ('SELECT',       r'\bSELECT\b'),
    ('FROM',         r'\bFROM\b'),
    ('WHERE',        r'\bWHERE\b'),
    ('AND',          r'\bAND\b'),
    ('OR',           r'\bOR\b'),
    ('NOT',          r'\bNOT\b'),
    ('IN',           r'\bIN\b'),
    ('NUMBER',       r'\b\d+(\.\d+)?\b'),
    ('STRING',       r"'[^']*'"),
    ('ASTERISK',     r'\*'),
    ('EQ',           r'='),
    ('NEQ',          r'!='),
    ('LTE',          r'<='),
    ('GTE',          r'>='),
    ('LT',           r'<'),
    ('GT',           r'>'),
    ('PLUS',         r'\+'),
    ('MINUS',        r'-'),
    ('MULTIPLY',     r'\*'),
    ('DIVIDE',       r'/'),
    ('COMMA',        r','),
    ('SEMICOLON',    r';'),
    ('LPAREN',       r'\('),
    ('RPAREN',       r'\)'),
    ('IDENTIFIER',   r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),  # Place after keywords to avoid conflicts
    ('SKIP',         r'[ \t\n]+'),
    ('MISMATCH',     r'.'),
]

# SQL keywords to capitalize in token values
SQL_KEYWORDS = {'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN'}

def tokenize(code):
    tokens = []
    regex_parts = [f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION]
    regex = re.compile('|'.join(regex_parts), re.IGNORECASE)

    for match in regex.finditer(code):
        kind = match.lastgroup
        value = match.group()

        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f"Unexpected character: {value}")
        else:
            if kind.upper() in SQL_KEYWORDS:
                tokens.append((kind.upper(), value.upper()))
            else:
                tokens.append((kind.upper(), value))

    return tokens
