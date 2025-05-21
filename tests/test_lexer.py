import pytest
from app.lexer import tokenize

def test_tokenize_simple_select():
    sql = "SELECT id, name FROM users;"
    tokens = tokenize(sql)
    token_types = [t['type'] for t in tokens]

    assert "SELECT" in token_types
    assert "IDENTIFIER" in token_types
    assert "FROM" in token_types
    assert "SEMICOLON" in token_types

def test_tokenize_empty_string():
    tokens = tokenize("")
    assert tokens == []
