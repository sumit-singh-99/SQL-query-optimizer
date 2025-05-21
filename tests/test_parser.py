import pytest
from app.lexer import tokenize
from app.parser import parse

def test_parse_simple_select():
    sql = "SELECT id, name FROM users;"
    tokens = tokenize(sql)
    ast = parse(tokens)

    assert isinstance(ast, list)
    assert ast[0]['type'] == 'SELECT'
    assert 'table' in ast[0]
    assert 'columns' in ast[0]

def test_parse_invalid_syntax():
    sql = "SELEC id FROM;"
    tokens = tokenize(sql)
    with pytest.raises(Exception):
        parse(tokens)
