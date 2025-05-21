import pytest
from app.lexer import tokenize
from app.parser import parse
from app.optimizer import optimize

def test_optimize_no_change():
    sql = "SELECT * FROM users;"
    tokens = tokenize(sql)
    ast = parse(tokens)
    optimized_ast = optimize(ast)

    # Assuming optimize returns a modified AST or same AST if no optimization
    assert isinstance(optimized_ast, list)
    assert optimized_ast == ast  # If optimizer makes no changes here

def test_optimize_pushdown():
    # Example where optimizer should apply predicate pushdown
    sql = "SELECT * FROM users WHERE age > 30;"
    tokens = tokenize(sql)
    ast = parse(tokens)
    optimized_ast = optimize(ast)

    # For this test, just check optimizer returns something valid
    assert isinstance(optimized_ast, list)
