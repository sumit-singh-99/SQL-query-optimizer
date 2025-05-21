import pytest
from app.lexer import tokenize
from app.parser import parse
from app.semantic import validate
from app.optimizer import optimize
from app.ir_generator import generate_ir

def test_full_pipeline_success():
    sql = "SELECT id, name FROM users WHERE age > 25;"
    tokens = tokenize(sql)
    ast = parse(tokens)

    semantic_errors = validate(ast)
    assert semantic_errors == []

    optimized_ast = optimize(ast)
    ir = generate_ir(optimized_ast)

    assert isinstance(ir, dict) or isinstance(ir, list)  # Depending on your IR structure

def test_full_pipeline_with_semantic_error():
    sql = "SELECT id, foo FROM users;"
    tokens = tokenize(sql)
    ast = parse(tokens)
    errors = validate(ast)

    assert len(errors) > 0
    assert "Column 'foo' does not exist" in errors[0]
