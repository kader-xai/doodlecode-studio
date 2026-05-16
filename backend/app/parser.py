"""AST → logical code blocks. Used both for explanation generation and arrow targets."""
from __future__ import annotations

import ast
from typing import Optional

from .models import CodeBlock


def _kind_of(node: ast.AST) -> tuple[str, Optional[str]]:
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        else:
            names = [f"{node.module or ''}.{a.name}" for a in node.names]
        return "import", ", ".join(names) or None
    if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
        return "function", node.name
    if isinstance(node, ast.ClassDef):
        return "class", node.name
    if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
        return "loop", None
    if isinstance(node, ast.If):
        return "conditional", None
    if isinstance(node, ast.Assign):
        targets = []
        for t in node.targets:
            if isinstance(t, ast.Name):
                targets.append(t.id)
        return "assign", ", ".join(targets) or None
    if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
        return "assign", node.target.id
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return "assign", node.target.id
    if isinstance(node, ast.Expr):
        return "expr", None
    if isinstance(node, ast.Return):
        return "return", None
    if isinstance(node, ast.With) or isinstance(node, ast.AsyncWith):
        return "context", None
    if isinstance(node, ast.Try):
        return "try", None
    return type(node).__name__.lower(), None


def parse_blocks(code: str, cell_id: str = "cell") -> list[CodeBlock]:
    """Return one CodeBlock per top-level statement."""
    if not code.strip():
        return []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    blocks: list[CodeBlock] = []
    for i, node in enumerate(tree.body):
        kind, name = _kind_of(node)
        start = getattr(node, "lineno", 1)
        end = getattr(node, "end_lineno", start) or start
        summary = _summarize(node, kind, name)
        blocks.append(
            CodeBlock(
                id=f"{cell_id}-b{i}",
                start_line=start,
                end_line=end,
                kind=kind,
                name=name,
                summary=summary,
            )
        )
    return blocks


def _summarize(node: ast.AST, kind: str, name: Optional[str]) -> str:
    if kind == "import":
        return f"Pulls in {name}." if name else "Imports a module."
    if kind == "function":
        args = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
        sig = f"{name}({', '.join(args)})" if name else "anonymous"
        return f"Defines function {sig}."
    if kind == "class":
        return f"Defines class {name}."
    if kind == "loop":
        return "Iterates — repeats the body."
    if kind == "conditional":
        return "Branches on a condition."
    if kind == "assign":
        return f"Assigns value to {name}." if name else "Assigns a value."
    if kind == "return":
        return "Returns a value from the enclosing function."
    if kind == "expr":
        # call?
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name):
                return f"Calls {func.id}()."
            if isinstance(func, ast.Attribute):
                return f"Calls .{func.attr}()."
        return "Evaluates an expression."
    if kind == "context":
        return "Enters a context manager (with-block)."
    if kind == "try":
        return "Try/except — handles potential errors."
    return "Statement."
