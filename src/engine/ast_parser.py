"""
Symbolic AST parser.

Extracts structural facts from source code so Gemini can be grounded
on verifiable code structure instead of pure guessing.
Supports Python natively; falls back to regex for other languages.
"""
import ast
import re
from typing import Dict, List


class ASTParser:
    def parse(self, code: str, language: str = "python") -> Dict:
        if language.lower() == "python":
            return self._parse_python(code)
        return self._parse_generic(code, language)

    # ----- Python -----
    def _parse_python(self, code: str) -> Dict:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"error": f"SyntaxError: {e}", "facts": []}

        facts: List[str] = []
        functions, classes, imports = [], [], []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                if len(node.args.args) > 5:
                    facts.append(
                        f"Function '{node.name}' has {len(node.args.args)} parameters — consider refactoring."
                    )
                if not ast.get_docstring(node):
                    facts.append(f"Function '{node.name}' has no docstring.")
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for n in node.names:
                    imports.append(n.name)

        # Hard violation: raw SQL string
        if re.search(r"(SELECT|INSERT|UPDATE|DELETE).*\+.*", code, re.IGNORECASE):
            facts.append(
                "Potential SQL injection: string concatenation detected in SQL query."
            )

        # Single-character variables
        single_chars = re.findall(r"\b([a-zA-Z])\s*=", code)
        if single_chars:
            facts.append(
                f"Single-character variable names found: {set(single_chars)} — hurts readability."
            )

        return {
            "language": "python",
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "line_count": len(code.splitlines()),
            "facts": facts,
        }

    # ----- Generic fallback -----
    def _parse_generic(self, code: str, language: str) -> Dict:
        facts: List[str] = []
        if re.search(r"eval\(|exec\(", code):
            facts.append("Use of eval/exec detected — security risk.")
        if re.search(r"password\s*=\s*['\"]", code, re.IGNORECASE):
            facts.append("Hardcoded password detected.")
        return {
            "language": language,
            "functions": [],
            "classes": [],
            "imports": [],
            "line_count": len(code.splitlines()),
            "facts": facts,
        }
