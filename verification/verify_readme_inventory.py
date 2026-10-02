"""README inventory consistency (2026-10-02).

The README once said the discipline keeps "~70" modules trustworthy, while
the release notes said 166 and the tree had 167 Python files. These count
different things, and one number had gone stale. This check counts the
real tree and requires the README to state the counts with their
definitions, and to list every top-level subpackage in its module table:

- python_files: all ``*.py`` under ``src/scoped_correspondence/``
- subpackages: directories with ``__init__.py`` below the top-level package
  (including nested ones such as ``validation/modular_networks``)
- modules: ``*.py`` files that are not ``__init__.py``
- importable_modules: python_files - 1 (packages are modules too)
- verification_scripts: ``verification/verify_*.py`` (what the suite runs)
- archived_verify_scripts: other ``verify_*.py`` in the repo (not run)

python_files = 1 (top-level ``__init__``) + subpackages + modules.
The wheel smoke test imports ``python_files - 1`` submodules.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "src" / "scoped_correspondence"


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def inventory():
    files = sorted(PKG.rglob("*.py"))
    inits = [f for f in files if f.name == "__init__.py"]
    sub = [f.parent for f in inits if f.parent != PKG]
    mods = [f for f in files if f.name != "__init__.py"]
    verify = sorted((ROOT / "verification").glob("verify_*.py"))
    top_skip = {".git", ".claude", "verification", "src"}  # only the TOP-level dirs (archives have own verification/ subdirs)
    archived = sorted(p for p in ROOT.rglob("verify_*.py")
                      if p.relative_to(ROOT).parts[0] not in top_skip and "__pycache__" not in p.parts)
    require(len(files) == 1 + len(sub) + len(mods), "file count decomposition")
    top = sorted(p.name for p in PKG.iterdir() if p.is_dir() and (p / "__init__.py").exists())
    return {"python_files": len(files), "subpackages": len(sub), "modules": len(mods),
            "importable_modules": len(files) - 1, "verification_scripts": len(verify),
            "archived_verify_scripts": len(archived), "top_level_subpackages": top}


def check_readme_counts():
    inv = inventory()
    readme = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())  # line breaks do not matter
    phrase = (f"{inv['importable_modules']} importable modules ({inv['modules']} module files in "
              f"{inv['subpackages']} subpackages, {inv['python_files']} Python files)")
    require(phrase in readme, f"README must state: '{phrase}'")
    vphrase = (f"{inv['verification_scripts']} `verify_*.py` scripts that try to break them, "
               f"plus {inv['archived_verify_scripts']} archived ones the suite no longer runs")
    require(vphrase in readme, f"README must state: '{vphrase}'")
    require("~70" not in readme, "stale '~70' module count still in README")
    return {k: v for k, v in inv.items() if k != "top_level_subpackages"}


def check_module_table_complete():
    inv = inventory()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    table = readme[readme.index("## Module overview"):readme.index("## Scope, composition and evidence")]
    listed = set(re.findall(r"^\| `([a-z_]+)/", table, re.M))
    missing = sorted(set(inv["top_level_subpackages"]) - listed)
    unknown = sorted(listed - set(inv["top_level_subpackages"]))
    require(not missing and not unknown, f"README module table: missing {missing}, not existing {unknown}")
    return {"top_level_subpackages": len(inv["top_level_subpackages"])}


CHECKS = [check_readme_counts, check_module_table_complete]


def main():
    results, n_passed = {}, 0
    for check in CHECKS:
        name = check.__name__.removeprefix("check_")
        try:
            results[name] = check()
            print(f"PASS  {name}")
            n_passed += 1
        except AssertionError as e:
            results[name] = {"error": str(e)}
            print(f"FAIL  {name}: {e}")
    print(f"\n{n_passed}/{len(CHECKS)} checks passed")
    Path(__file__).with_name("verify_readme_inventory_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
