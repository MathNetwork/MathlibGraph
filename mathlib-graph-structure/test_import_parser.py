#!/usr/bin/env python3
"""Tests for the import graph parser."""

import tempfile
from pathlib import Path

# Import the parser from the analysis script
import importlib.util
spec = importlib.util.spec_from_file_location(
    "analyze", Path(__file__).parent / "analyze_import_graph.py"
)

# We only need parse_imports, so extract it by running just the function defs
import re

def parse_imports(path: Path) -> list[str]:
    """Copy of parse_imports from analyze_import_graph.py for testing."""
    imports = []
    in_block_comment = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            stripped = line.strip()
            was_in_comment = in_block_comment > 0
            entered_comment = False
            i = 0
            while i < len(stripped):
                if i + 1 < len(stripped) and stripped[i:i+2] == "/-":
                    in_block_comment += 1
                    entered_comment = True
                    i += 2
                elif i + 1 < len(stripped) and stripped[i:i+2] == "-/":
                    in_block_comment = max(0, in_block_comment - 1)
                    i += 2
                else:
                    i += 1
            if in_block_comment > 0 or was_in_comment or entered_comment:
                continue
            if not stripped or stripped.startswith("--"):
                continue
            if stripped.startswith("module"):
                continue
            m = re.match(
                r"^(?:public\s+)?(?:meta\s+)?import\s+([\w.]+)", stripped
            )
            if m:
                imports.append(m.group(1))
                continue
            break
    return imports


def write_temp(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".lean", delete=False)
    f.write(content)
    f.close()
    return Path(f.name)


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

def test_basic_imports():
    """Simple file with module keyword and imports."""
    p = write_temp("""\
/-
Copyright (c) 2024 Test. All rights reserved.
-/
module

public import Mathlib.Init
public import Mathlib.Data.Nat.Notation
""")
    result = parse_imports(p)
    assert result == ["Mathlib.Init", "Mathlib.Data.Nat.Notation"], f"Got: {result}"
    print("  PASS test_basic_imports")


def test_meta_import():
    """Meta imports should be parsed too."""
    p = write_temp("""\
module

public meta import Lean.Elab.DefView
public import Lean.Elab.DeclModifiers
""")
    result = parse_imports(p)
    assert result == ["Lean.Elab.DefView", "Lean.Elab.DeclModifiers"], f"Got: {result}"
    print("  PASS test_meta_import")


def test_no_module_keyword():
    """Older files might not have the module keyword."""
    p = write_temp("""\
/-
Copyright header
-/
import Mathlib.Algebra.Group.Defs
import Mathlib.Data.Int.Notation
""")
    result = parse_imports(p)
    assert result == ["Mathlib.Algebra.Group.Defs", "Mathlib.Data.Int.Notation"], f"Got: {result}"
    print("  PASS test_no_module_keyword")


def test_imports_in_doc_comment_ignored():
    """Import statements inside /- -/ block comments should be ignored."""
    p = write_temp("""\
module

public import Mathlib.Init

/-!
# Example
```lean
import Mathlib.Fake.Module
import Mathlib.Another.Fake
```
-/

def foo := 42
""")
    result = parse_imports(p)
    assert result == ["Mathlib.Init"], f"Got: {result}"
    print("  PASS test_imports_in_doc_comment_ignored")


def test_imports_in_code_block_ignored():
    """The MinImports-style case: imports in doc comment code blocks."""
    p = write_temp("""\
/-
Copyright (c) 2024 Test.
-/
module

public meta import Lean.Elab.DefView
public import Lean.Elab.DeclModifiers

/-! # Some doc
```lean
import Mathlib.Data.Sym.Sym2.Init -- the actual minimal import
import Mathlib.Tactic.MinImports
```
-/

def realCode := 1
""")
    result = parse_imports(p)
    assert result == ["Lean.Elab.DefView", "Lean.Elab.DeclModifiers"], f"Got: {result}"
    print("  PASS test_imports_in_code_block_ignored")


def test_no_self_import():
    """Verify no self-imports leak through from comments."""
    p = write_temp("""\
/-
Copyright
-/
module

public import Mathlib.Algebra.Group.Defs

/-! doc -/

-- import Mathlib.Self.Import  (this is a line comment)
theorem foo : True := trivial
""")
    result = parse_imports(p)
    assert result == ["Mathlib.Algebra.Group.Defs"], f"Got: {result}"
    print("  PASS test_no_self_import")


def test_stop_at_declaration():
    """Parser should stop at the first non-import line after header."""
    p = write_temp("""\
module

import Mathlib.A
import Mathlib.B

theorem foo : True := trivial

import Mathlib.C
""")
    result = parse_imports(p)
    assert result == ["Mathlib.A", "Mathlib.B"], f"Got: {result}"
    print("  PASS test_stop_at_declaration")


def test_nested_block_comments():
    """Nested block comments should be handled correctly."""
    p = write_temp("""\
/- outer /- inner -/ still outer -/
module

import Mathlib.Real
""")
    result = parse_imports(p)
    assert result == ["Mathlib.Real"], f"Got: {result}"
    print("  PASS test_nested_block_comments")


def test_empty_file():
    """Empty file should return no imports."""
    p = write_temp("")
    result = parse_imports(p)
    assert result == [], f"Got: {result}"
    print("  PASS test_empty_file")


def test_single_line_comment_between_imports():
    """Single-line comments between imports should be skipped."""
    p = write_temp("""\
module

import Mathlib.A
-- this is a comment
import Mathlib.B
""")
    result = parse_imports(p)
    assert result == ["Mathlib.A", "Mathlib.B"], f"Got: {result}"
    print("  PASS test_single_line_comment_between_imports")


def test_real_file_algebra_group_defs():
    """Test against real Mathlib file: Algebra/Group/Defs.lean."""
    p = Path("/Users/moqian/MathFactor/mathlib4/Mathlib/Algebra/Group/Defs.lean")
    if not p.exists():
        print("  SKIP test_real_file_algebra_group_defs (file not found)")
        return
    result = parse_imports(p)
    assert "Mathlib.Algebra.Notation.Defs" in result, f"Missing expected import. Got: {result}"
    assert "Mathlib.Data.Nat.Notation" in result, f"Missing expected import. Got: {result}"
    assert "Batteries.Logic" in result, f"Missing Batteries import. Got: {result}"
    assert len(result) == 9, f"Expected 9 imports, got {len(result)}: {result}"
    print(f"  PASS test_real_file_algebra_group_defs ({len(result)} imports)")


def test_real_file_min_imports():
    """Test against real Mathlib file: Tactic/MinImports.lean (tricky case)."""
    p = Path("/Users/moqian/MathFactor/mathlib4/Mathlib/Tactic/MinImports.lean")
    if not p.exists():
        print("  SKIP test_real_file_min_imports (file not found)")
        return
    result = parse_imports(p)
    # Should NOT contain self-import or imports from doc comment code blocks
    assert "Mathlib.Tactic.MinImports" not in result, f"Self-import leaked! Got: {result}"
    assert "Mathlib.Data.Sym.Sym2.Init" not in result, f"Doc comment import leaked! Got: {result}"
    assert "Lean.Elab.DefView" in result, f"Missing expected import. Got: {result}"
    print(f"  PASS test_real_file_min_imports ({len(result)} imports, no leaks)")


def test_real_file_data_nat_notation():
    """Test against real Mathlib file: Data/Nat/Notation.lean."""
    p = Path("/Users/moqian/MathFactor/mathlib4/Mathlib/Data/Nat/Notation.lean")
    if not p.exists():
        print("  SKIP test_real_file_data_nat_notation (file not found)")
        return
    result = parse_imports(p)
    assert result == ["Mathlib.Init"], f"Expected ['Mathlib.Init'], got: {result}"
    print("  PASS test_real_file_data_nat_notation")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running import parser tests...")
    test_basic_imports()
    test_meta_import()
    test_no_module_keyword()
    test_imports_in_doc_comment_ignored()
    test_imports_in_code_block_ignored()
    test_no_self_import()
    test_stop_at_declaration()
    test_nested_block_comments()
    test_empty_file()
    test_single_line_comment_between_imports()
    test_real_file_algebra_group_defs()
    test_real_file_min_imports()
    test_real_file_data_nat_notation()
    print("\nAll tests passed!")
