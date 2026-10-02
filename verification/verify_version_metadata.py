"""Version metadata consistency (release 0.42.0a1, 2026-10-02).

The package version must agree in pyproject.toml, CITATION.cff and
``scoped_correspondence.__version__`` (which had silently stayed at
0.10.0a1 while the package moved to 0.41.0a1), and RELEASE_NOTES.md must
have a section for it.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:  # tomllib exists from Python 3.11; pyproject allows >= 3.10
    import tomllib
except ImportError:  # pragma: no cover - exercised only on 3.10
    tomllib = None

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def check_versions_agree():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    if tomllib is not None:
        py = tomllib.loads(text)["project"]["version"]
    else:
        py = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M).group(1)
    cff = re.search(r'^version:\s*"([^"]+)"', (ROOT / "CITATION.cff").read_text(encoding="utf-8"), re.M).group(1)
    import scoped_correspondence

    require(py == cff == scoped_correspondence.__version__, f"pyproject {py}, CITATION {cff}, __version__ {scoped_correspondence.__version__}")
    notes = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")
    require(f"## {py} " in notes, f"RELEASE_NOTES.md needs a section '## {py} ...'")
    return {"version": py}


def main():
    try:
        r = check_versions_agree()
        print("PASS  versions_agree")
        ok = True
    except AssertionError as e:
        r = {"error": str(e)}
        print(f"FAIL  versions_agree: {e}")
        ok = False
    print(f"\n{int(ok)}/1 checks passed")
    Path(__file__).with_name("verify_version_metadata_results.json").write_text(
        json.dumps({"n_passed": int(ok), "n_total": 1, "results": {"versions_agree": r}}, indent=2), encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
