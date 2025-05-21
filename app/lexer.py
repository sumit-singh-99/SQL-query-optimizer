import re

# Define token patterns
TOKEN_SPECIFICATION = [
    ('NUMBER',       r'\b\d+(\.\d+)?\b'),
    ('STRING',       r"'[^']*'"),
    ('SELECT',       r'\bSELECT\b'),
    ('FROM',         r'\bFROM\b'),
    ('WHERE',        r'\bWHERE\b'),
    ('AND',          r'\bAND\b'),
    ('OR',           r'\bOR\b'),
    ('NOT',          r'\bNOT\b'),
    ('IDENTIFIER',   r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('ASTERISK',     r'\*'),
    ('EQ',           r'='),
    ('NEQ',          r'!='),
    ('LTE',          r'<='),
    ('GTE',          r'>='),
    ('LT',           r'<'),
    ('GT',           r'>'),
    ('COMMA',        r','),
    ('SEMICOLON',    r';'),
    ('LPAREN',       r'\('),
    ('RPAREN',       r'\)'),
    ('SKIP',         r'[ \t\n]+'),
    ('MISMATCH',     r'.'),
]

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
            tokens.append((kind.upper(), value))

    return tokens
