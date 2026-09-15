"""
Multi-language symbolic AST parser.

Extracts structural facts from source code so Gemini can be grounded
on verifiable code structure instead of pure guessing.

- Python: real AST via the `ast` module
- JavaScript / TypeScript: regex-based structural extraction
- Other languages: generic security/style heuristics
"""
import ast
import re
from typing import Dict, List


class ASTParser:
    def parse(self, code: str, language: str = "python") -> Dict:
        lang = (language or "python").lower()

        if lang in ("python", "py"):
            return self._parse_python(code)
        if lang in ("javascript", "js", "typescript", "ts", "jsx", "tsx"):
            return self._parse_js_ts(code, lang)
        return self._parse_generic(code, lang)

    # ---------- Python ----------
    def _parse_python(self, code: str) -> Dict:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"language": "python", "error": f"SyntaxError: {e}", "facts": []}

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

        if re.search(r"(SELECT|INSERT|UPDATE|DELETE).*\+.*", code, re.IGNORECASE):
            facts.append(
                "Potential SQL injection: string concatenation detected in SQL query."
            )

        single_chars = re.findall(r"\b([a-zA-Z])\s*=", code)
        if single_chars:
            facts.append(
                f"Single-character variable names found: {set(single_chars)} — hurts readability."
            )

        if re.search(r"\bprint\s*\(", code):
            facts.append("print() statement found — consider structured logging.")

        return {
            "language": "python",
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "line_count": len(code.splitlines()),
            "facts": facts,
        }

    # ---------- JavaScript / TypeScript ----------
    def _parse_js_ts(self, code: str, lang: str) -> Dict:
        facts: List[str] = []

        # Functions
        functions = re.findall(
            r"(?:function\s+([A-Za-z_$][\w$]*))|(?:const\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\()",
            code,
        )
        func_names = [a or b for a, b in functions if (a or b)]

        # Classes
        classes = re.findall(r"class\s+([A-Za-z_$][\w$]*)", code)

        # Imports
        imports = re.findall(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", code)

        # Anti-patterns
        if re.search(r"\bvar\s+\w+", code):
            facts.append("'var' used — prefer 'let' or 'const' in modern JavaScript.")

        if "console.log(" in code:
            facts.append("console.log() left in code — remove before production.")

        if re.search(r"\beval\s*\(", code):
            facts.append("eval() detected — dangerous, allows arbitrary code execution.")

        if re.search(r"password\s*[:=]\s*['\"][^'\"]+['\"]", code, re.IGNORECASE):
            facts.append("Hardcoded password detected in source.")

        if re.search(r"api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"]", code, re.IGNORECASE):
            facts.append("Hardcoded API key detected — use environment variables.")

        # Missing JSDoc on functions
        for name in func_names:
            pattern = rf"/\*\*[\s\S]*?\*/\s*(?:async\s+)?function\s+{re.escape(name)}"
            if not re.search(pattern, code):
                facts.append(f"Function '{name}' has no JSDoc comment.")

        # Single-character variables
        single_chars = re.findall(r"\b(?:let|const|var)\s+([a-zA-Z])\s*=", code)
        if single_chars:
            facts.append(
                f"Single-character variable names found: {set(single_chars)} — hurts readability."
            )

        # TypeScript-specific
        if lang in ("typescript", "ts", "tsx"):
            if ": any" in code:
                facts.append("'any' type used — weakens TypeScript type safety.")
            if re.search(r"@ts-ignore", code):
                facts.append("@ts-ignore suppresses type errors — fix the root cause.")

        return {
            "language": lang,
            "functions": func_names,
            "classes": classes,
            "imports": imports,
            "line_count": len(code.splitlines()),
            "facts": facts,
        }

    # ---------- Generic fallback ----------
    def _parse_generic(self, code: str, language: str) -> Dict:
        facts: List[str] = []
        if re.search(r"\beval\s*\(|exec\s*\(", code):
            facts.append("Use of eval/exec detected — security risk.")
        if re.search(r"password\s*[:=]\s*['\"][^'\"]+['\"]", code, re.IGNORECASE):
            facts.append("Hardcoded password detected.")
        if re.search(r"TODO|FIXME", code):
            facts.append("TODO/FIXME markers present in code.")
        return {
            "language": language,
            "functions": [],
            "classes": [],
            "imports": [],
            "line_count": len(code.splitlines()),
            "facts": facts,
        }
