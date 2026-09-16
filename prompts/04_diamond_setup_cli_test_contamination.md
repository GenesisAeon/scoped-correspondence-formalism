# Phase-2-Prompt 4/N: drei Repos -- `tests/test_cli.py` ist Fremdcode

**Repos, alle drei in diesem einen Ticket:**
- `D:\mandala\resilience-core` (P40)
- `D:\mandala\scope-resilience` (P41)
- `D:\mandala\afet-tensions` (P34)

**Root Cause (verifiziert 2026-09-15, kein diamond-setup-Bug):** In allen
drei Repos ist `tests/test_cli.py` eine vollstaendige, unveraenderte Kopie
von `diamond-setup`s EIGENER Testsuite (`from diamond_setup.cli import
app`, `from diamond_setup.templates import REGISTRY`, Tests wie
`test_scaffold_minimal`, `test_validate_current_project` mit Docstring
"Running validate on diamond-setup's own root should pass"). Geprueft:
`diamond-setup`s Scaffold-Templates (`templates/minimal.py`,
`templates/genesis.py`) enthalten diese Datei NICHT -- sie kam nicht durch
Scaffolding, sondern durch Copy-Paste, ohne die Imports anzupassen. Nur
`test_version` faellt auf (druckt "diamond-setup X.Y.Z" statt der eigenen
Paketversion) -- die anderen ~10 Tests pro Datei "bestehen" nur zufaellig,
weil sie tatsaechlich `diamond-setup`s eigene, mitinstallierte
Funktionalitaet pruefen, nicht die des jeweiligen Pakets. **Kein Test in
diesen drei Dateien prueft je etwas aus dem eigenen Paket.**

Kein Versions-Bump in diesem Schritt (folgt separat nach Review, pro Repo).

---

## Teil A: `resilience-core` -- Datei loeschen

`resilience-core` hat KEINE eigene CLI (`find src -iname cli.py` findet
nichts). `tests/test_cli.py` testet daher ausschliesslich Fremdcode.

**Aufgabe:** `tests/test_cli.py` komplett loeschen. Nichts ersetzen --
es gibt nichts Eigenes zu testen, solange `resilience-core` keine eigene
CLI hat.

**Akzeptanzkriterium:** `pytest` laeuft weiterhin komplett gruen (eine
Testdatei weniger, kein Fehlschlag mehr durch `test_version`).

---

## Teil B: `scope-resilience` -- echte CLI-Tests schreiben

`scope-resilience` hat eine echte, bisher komplett ungetestete CLI in
`src/scope_resilience/_cli.py` (Typer-App `app`, Befehle: `serve`,
`assess`, `export-llms-txt`, `path`).

**Aufgabe:** `tests/test_cli.py` komplett ersetzen durch:

```python
"""Tests for scope-resilience's own CLI (src/scope_resilience/_cli.py)."""

from typer.testing import CliRunner

from scope_resilience._cli import app

runner = CliRunner()


def test_assess_runs_and_shows_metrics():
    result = runner.invoke(app, ["assess", "AMOC tipping point"])
    assert result.exit_code == 0, result.output
    assert "Hallucination Risk" in result.output
    assert "Risk Level" in result.output


def test_assess_with_domain_option():
    result = runner.invoke(app, ["assess", "quantum computing", "--domain", "physics_dense"])
    assert result.exit_code == 0, result.output
    assert "Hallucination Risk" in result.output


def test_export_llms_txt_runs():
    result = runner.invoke(app, ["export-llms-txt", "test topic"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() != ""


def test_path_command_runs():
    result = runner.invoke(app, ["path", "test topic"])
    assert result.exit_code == 0, result.output
    assert "Topic:" in result.output
    assert "\u0393_sem:" in result.output or "Gamma_sem:" in result.output


def test_path_command_no_path_found_is_graceful():
    # min_rho=1.1 is unreachable (rho_sem is bounded well below 1.1),
    # so get_semantic_path's own "no path meets threshold" branch still
    # returns a path with a warning attached -- assert this stays exit 0.
    result = runner.invoke(app, ["path", "test topic", "--min-rho", "1.1"])
    assert result.exit_code == 0, result.output


def test_serve_without_mcp_extra_fails_gracefully():
    # fastmcp is an optional extra; if not installed, serve() must exit
    # cleanly with code 1 and an explanatory message, not crash.
    result = runner.invoke(app, ["serve"])
    if result.exit_code != 0:
        assert "fastmcp" in result.output.lower() or "mcp" in result.output.lower()
    # If fastmcp IS installed in this environment, serve would try to
    # actually bind a port and block -- do not assert exit_code==0 here.
```

**Wichtig:** falls `fastmcp` im Testumfeld tatsaechlich installiert ist
und `serve` deshalb versucht, einen echten Port zu binden (blockierend),
bitte `test_serve_without_mcp_extra_fails_gracefully` anpassen oder mit
einem Timeout/Mock versehen -- nicht die Testsuite haengen lassen. Bitte
kurz zurueckmelden, welcher Fall tatsaechlich zutraf.

**Akzeptanzkriterium:** `pytest` laeuft komplett gruen, alle neuen Tests
pruefen tatsaechlich `scope_resilience`s eigene CLI, nicht `diamond_setup`.

---

## Teil C: `afet-tensions` -- echte CLI-Tests schreiben

`afet-tensions` hat eine echte, bisher komplett ungetestete CLI in
`src/afet_tensions/cli.py` (Typer-App `app`, Befehle: `run`,
`h0-predict`, `s8-predict`, `benchmark`, `falsification-schedule`).

**Aufgabe:** `tests/test_cli.py` komplett ersetzen durch:

```python
"""Tests for afet-tensions's own CLI (src/afet_tensions/cli.py)."""

from typer.testing import CliRunner

from afet_tensions.cli import app

runner = CliRunner()


def test_run_shows_cycle_results():
    result = runner.invoke(app, ["run"])
    assert result.exit_code == 0, result.output
    assert "Cycle Results" in result.output
    assert "H\u2080 local" in result.output or "H0 local" in result.output


def test_h0_predict():
    result = runner.invoke(app, ["h0-predict", "--z", "0.5"])
    assert result.exit_code == 0, result.output
    assert "H\u2080_eff" in result.output or "H0_eff" in result.output


def test_s8_predict():
    result = runner.invoke(app, ["s8-predict", "--z", "0.5"])
    assert result.exit_code == 0, result.output
    assert "S\u2088" in result.output or "S8" in result.output


def test_benchmark_runs_and_reports_consistently():
    from afet_tensions.benchmark import run_benchmark

    result = runner.invoke(app, ["benchmark"])
    expected_results = run_benchmark()
    expected_exit_code = 0 if all(expected_results.values()) else 1
    assert result.exit_code == expected_exit_code, result.output
    assert "Benchmark" in result.output


def test_falsification_schedule():
    result = runner.invoke(app, ["falsification-schedule"])
    assert result.exit_code == 0, result.output
    assert "DESI DR2" in result.output
    assert "Euclid DR1" in result.output
    assert "LIGO O5" in result.output
```

**Wichtig zu `test_benchmark_runs_and_reports_consistently`:** dieser Test
prueft bewusst NICHT, ob alle Benchmarks bestehen (das haengt vom
aktuellen, gerade erst neu gefitteten Kalibrierungsstand ab, siehe Ticket
3/`v1.0.1`) -- er prueft nur, dass der CLI-Exit-Code konsistent mit
`run_benchmark()`s eigenem Ergebnis ist. Bitte NICHT durch
`assert result.exit_code == 0` ersetzen, falls das beim ersten Lauf nicht
zutrifft.

**Akzeptanzkriterium:** `pytest` laeuft komplett gruen, alle neuen Tests
pruefen tatsaechlich `afet_tensions`s eigene CLI, nicht `diamond_setup`.

---

## Gesamt-Akzeptanzkriterien

- Drei separate `git diff`s (ein Repo pro Diff) -- bitte am Ende fuer
  jedes der drei Repos einzeln melden: welche Datei geaendert/geloescht,
  wie viele Tests laufen jetzt, alle gruen?
- Keine Aenderung an Nicht-Test-Code in einem der drei Repos.
- Kein Versions-Bump, kein CHANGELOG-Eintrag, kein Zenodo-Release in
  irgendeinem der drei Repos -- macht Claude nach Review, pro Repo
  einzeln.

## Bitte NICHT tun

- `diamond-setup` selbst NICHT anfassen -- der Fehler liegt nicht dort.
- Keine neuen Abhaengigkeiten in einem der drei Repos.
- Keine Annahmen ueber Testergebnisse treffen, die nicht tatsaechlich
  durch Ausfuehren verifiziert wurden -- bei Abweichungen (z.B. `fastmcp`
  installiert, `benchmark`-Exit-Code) bitte den echten Befund melden.
