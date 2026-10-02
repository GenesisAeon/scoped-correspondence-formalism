"""J3 verification of the mutation RUNNER itself (not of the registry run).

``scripts/run_targeted_mutations.py`` must classify outcomes correctly,
otherwise its report would overstate what the checks detect (plan section
9: syntax errors and non-executable mutants are not detections; equivalent
mutants must not silently enter the denominator). This script builds a tiny
throw-away toy repository and asserts every outcome class on it:
killed (assertion), killed (error only), survived, invalid (snippet missing),
invalid (does not compile), invalid (failing baseline), timeout,
equivalent_or_unresolved -- and that the toy working tree is unchanged.
Fast (seconds); no SCF numerics involved.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_targeted_mutations", REPO / "scripts" / "run_targeted_mutations.py")
rtm = importlib.util.module_from_spec(spec)
sys.modules["run_targeted_mutations"] = rtm
spec.loader.exec_module(rtm)

TOY_SRC = '''
def double(x):
    return 2 * x

def is_positive(x):
    return x > 0

def unused_branch(x):
    y = x + 0
    return x
'''

TOY_VERIFY = '''
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from toy import double, is_positive, unused_branch
ok = True
if double(3) != 6:
    print("FAIL  double"); ok = False
if not is_positive(1):
    print("FAIL  positive"); ok = False
assert unused_branch(4) == 4
print("PASS" if ok else "")
raise SystemExit(0 if ok else 1)
'''

SLOW_VERIFY = '''
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import toy
if toy.double(1) == 3:
    time.sleep(30)
print("PASS")
'''

BROKEN_VERIFY = '''
print("FAIL  always broken")
raise SystemExit(1)
'''

ERROR_VERIFY = '''
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import toy
1 / (toy.double(1) - 2 + 1)  # ZeroDivisionError when double(1) == 1
print("PASS")
'''


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="toyrepo_"))
    try:
        (tmp / "src").mkdir()
        (tmp / "verification").mkdir()
        (tmp / "src" / "toy.py").write_text(TOY_SRC, encoding="utf-8")
        (tmp / "verification" / "verify_toy.py").write_text(TOY_VERIFY, encoding="utf-8")
        (tmp / "verification" / "verify_slow.py").write_text(SLOW_VERIFY, encoding="utf-8")
        (tmp / "verification" / "verify_broken.py").write_text(BROKEN_VERIFY, encoding="utf-8")
        (tmp / "verification" / "verify_error.py").write_text(ERROR_VERIFY, encoding="utf-8")
        M = rtm.Mutant
        mutants = (
            M("assert_kill", "T", "src/toy.py", "return 2 * x", "return 3 * x", ("verify_toy.py",), "content"),
            M("error_kill", "T", "src/toy.py", "return 2 * x", "return 1 * x", ("verify_error.py",), "crash only"),
            M("survivor", "T", "src/toy.py", "    y = x + 0", "    y = x + 1", ("verify_toy.py",), "dead code"),
            M("equivalent", "T", "src/toy.py", "    y = x + 0", "    y = x - 0", ("verify_toy.py",), "dead code",
              equivalent_reason="y is never used"),
            M("missing_snippet", "T", "src/toy.py", "return 7 * x", "return 8 * x", ("verify_toy.py",), "-"),
            M("syntax_error", "T", "src/toy.py", "return x > 0", "return x >", ("verify_toy.py",), "-"),
            M("bad_baseline", "T", "src/toy.py", "return 2 * x", "return 3 * x", ("verify_broken.py",), "-"),
            M("slow", "T", "src/toy.py", "return 2 * x", "return 2 * x + 1", ("verify_slow.py",), "-"),
        )
        before = (tmp / "src" / "toy.py").read_text(encoding="utf-8")
        report = rtm.run(mutants, timeout=5.0, repo=tmp)
        by_id = {m["id"]: m for m in report["mutants"]}
        expect = {
            "assert_kill": ("killed", "assertion"),
            "error_kill": ("killed", "error"),
            "survivor": ("survived", None),
            "equivalent": ("equivalent_or_unresolved", None),
            "missing_snippet": ("invalid", None),
            "syntax_error": ("invalid", None),
            "bad_baseline": ("invalid", None),
            "slow": ("timeout", None),
        }
        for mid, (status, kind) in expect.items():
            got = (by_id[mid]["status"], by_id[mid]["kill_kind"])
            require(got == (status, kind), f"{mid}: expected {(status, kind)}, got {got} {by_id[mid]['detail']}")
        require(report["kill_ratio_excluding_equivalent"] == "2/3", f"denominator must exclude equivalent/invalid/timeout: {report['kill_ratio_excluding_equivalent']}")
        require((tmp / "src" / "toy.py").read_text(encoding="utf-8") == before, "toy working tree must be unchanged")
        out = {"n_passed": 1, "n_total": 1, "outcomes": {k: v["status"] for k, v in by_id.items()},
               "kill_ratio": report["kill_ratio_excluding_equivalent"]}
        print("PASS  runner_classifies_all_outcome_classes")
        rc = 0
    except AssertionError as e:
        print(f"FAIL  runner_classifies_all_outcome_classes: {e}")
        out = {"n_passed": 0, "n_total": 1, "error": str(e)}
        rc = 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    Path(__file__).with_name("verify_targeted_mutation_runner_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
