"""Unit tests for the symbolic AST parser."""
from src.engine.ast_parser import ASTParser


parser = ASTParser()


def test_detects_missing_docstring():
    code = "def add(a, b):\n    return a + b"
    result = parser.parse(code, "python")
    facts = result["facts"]
    assert any("no docstring" in f for f in facts)


def test_detects_single_char_variables():
    code = "def add(a, b):\n    \"\"\"Add two numbers.\"\"\"\n    x = a + b\n    return x"
    result = parser.parse(code, "python")
    facts = result["facts"]
    assert any("Single-character" in f for f in facts)


def test_counts_functions_and_classes():
    code = "class Foo:\n    pass\n\ndef bar():\n    \"\"\"Doc.\"\"\"\n    pass"
    result = parser.parse(code, "python")
    assert "Foo" in result["classes"]
    assert "bar" in result["functions"]


def test_handles_syntax_error_gracefully():
    code = "def broken(:\n    pass"
    result = parser.parse(code, "python")
    assert "error" in result


def test_returns_line_count():
    code = "x = 1\ny = 2\nz = 3"
    result = parser.parse(code, "python")
    assert result["line_count"] == 3
