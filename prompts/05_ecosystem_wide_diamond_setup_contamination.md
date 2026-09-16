# Phase-2-Prompt 5/N: Ökosystem-weite diamond-setup-Testkontamination

**Fund (2026-09-15):** die in Ticket 4 gefundene Kontamination
(`tests/test_cli.py` als unveraenderte Kopie von diamond-setup's eigener
Testsuite) betrifft nicht nur drei, sondern **13 Pakete**, und nicht nur
`test_cli.py`, sondern zusaetzlich **`tests/test_preset.py`** und
**`tests/test_validator.py`** (byte-identisch in allen geprueften Faellen)
sowie in zwei Faellen **`tests/test_protocol.py`**.

**Betroffene Pakete (12 aktive + 1 Legacy-Kopie, NICHT Teil dieses
Tickets):**
`afet-tensions`, `amazon-utac`, `cellular-genesis`, `eml-utac-bridge`,
`phaethon-chimera`, `resilience-core`, `sa-sv-duality`, `sandpile-utac`,
`scope-resilience`, `seismic-utac`, `vrig-cosmological`, `worldview`.
(`Architektur--Planungsprojekt/_diamond-setup-legacy` ist eine
Archiv-Kopie, kein aktives Paket -- explizit NICHT anfassen.)

`afet-tensions`, `resilience-core`, `scope-resilience`: `test_cli.py`
wurde in Ticket 4 bereits korrekt bereinigt (nicht erneut anfassen).
**Dieses Ticket behandelt: `test_preset.py`/`test_validator.py` in ALLEN
12 Paketen, plus `test_cli.py` in den 9 noch nicht behandelten Paketen,
plus `test_protocol.py` wo vorhanden.**

Kein Versions-Bump in diesem Schritt (folgt separat nach Review, pro Repo
einzeln).

---

## Allgemeine Methodik (auf jede Datei anwenden, bevor gehandelt wird)

Fuer jede Testdatei prüfen: **importiert und testet sie tatsaechlich
Code aus dem eigenen Paket, oder ausschliesslich `diamond_setup`-interne
Funktionen/Klassen?**

- Importiert die Datei NUR aus `diamond_setup.*` und nirgends aus dem
  eigenen Paket (`<paket_name>.*`) → **komplett loeschen**, es testet
  nichts Eigenes.
- Importiert die Datei aus dem eigenen Paket UND nutzt `diamond_setup`
  nur fuer einen echten Integrationspunkt (z.B. eine gemeinsame
  Exception-Klasse wie `NotConvergedError`, die das eigene Paket
  tatsaechlich wirft) → **behalten, nicht anfassen**.
- Grenzfall (z.B. `test_protocol.py`: testet `diamond_setup`s abstrakte
  `DiamondPackage`-Basisklasse ueber eine rein lokal definierte
  Demo-Klasse, ohne echten Bezug zum eigenen Paket) → **loeschen**, aber
  explizit im Abschlussbericht auflisten, welche Datei das war und warum,
  damit das nicht einfach durchrutscht.

**Bereits bestaetigt (nicht erneut pruefen, direkt loeschen):**
`tests/test_preset.py` und `tests/test_validator.py` sind in JEDEM der
12 Pakete zu 100% Fremdcode (verifiziert byte-identisch ueber mehrere
Pakete hinweg, testen ausschliesslich `diamond_setup.preset`/
`diamond_setup.validator`-interne Funktionen wie `_build_context`,
`_to_snake`, `validate`). Einfach loeschen, keine Einzelpruefung noetig.

---

## Teil 1: `test_preset.py` + `test_validator.py` loeschen -- alle 12 Pakete

Fuer jedes der 12 Pakete oben: `tests/test_preset.py` und
`tests/test_validator.py` loeschen (falls vorhanden -- nicht jedes Paket
hat zwingend beide, aber die meisten).

## Teil 2: `test_protocol.py` -- nur `resilience-core`, `scope-resilience`

Pruefen wie oben beschrieben (Grenzfall-Kriterium). Falls es wirklich nur
`diamond_setup.protocol.DiamondPackage` ueber eine lokale Demo-Klasse
testet (wie in `resilience-core` bereits bestaetigt): loeschen, im
Bericht auflisten.

## Teil 3: `test_cli.py` -- die 9 noch nicht behandelten Pakete

**Ohne eigene CLI gefunden (`find src -iname cli.py` liefert nichts) --
Datei einfach loeschen, wie bei `resilience-core` in Ticket 4:**
`amazon-utac`, `cellular-genesis`, `eml-utac-bridge`, `vrig-cosmological`,
`worldview`.

**Mit eigener CLI -- `test_cli.py` durch echte Tests ersetzen** (Muster
wie in Ticket 4 fuer `scope-resilience`/`afet-tensions`, mit
`typer.testing.CliRunner`):

### `phaethon-chimera` (`src/phaethon_chimera/cli.py`, Befehle: `run`, `chimera-state`, `destiny-report`)

```python
from typer.testing import CliRunner
from phaethon_chimera.cli import app

runner = CliRunner()

def test_run_shows_results():
    result = runner.invoke(app, ["run", "--n-orbits", "5"])
    assert result.exit_code == 0, result.output
    assert "Simulation Results" in result.output

def test_run_json_output():
    result = runner.invoke(app, ["run", "--n-orbits", "5", "--json"])
    assert result.exit_code == 0, result.output
    assert "gamma_phaethon" in result.output

def test_chimera_state():
    result = runner.invoke(app, ["chimera-state", "--n-orbits", "5"])
    assert result.exit_code == 0, result.output
    assert "Order parameter R" in result.output

def test_destiny_report():
    result = runner.invoke(app, ["destiny-report"])
    assert result.exit_code == 0, result.output
    assert "DESTINY+ Predictions" in result.output
```

### `sa-sv-duality` (`src/sa_sv_duality/cli.py`, Befehle: `run`, `q4-map`, `route`, `benchmark`, `version`)

```python
from typer.testing import CliRunner
from sa_sv_duality.cli import app

runner = CliRunner()

def test_run_shows_results():
    result = runner.invoke(app, ["run", "--duration", "2.0"])
    assert result.exit_code == 0, result.output
    assert "S_A (action entropy)" in result.output

def test_q4_map():
    result = runner.invoke(app, ["q4-map"])
    assert result.exit_code == 0, result.output
    assert "Q4 State Entropy Map" in result.output

def test_route_reports_actual_outcome():
    # Do NOT assume a path always exists between 0 and 15 -- report the
    # real exit code/output instead of forcing an assumption.
    result = runner.invoke(app, ["route", "0", "15"])
    assert result.exit_code in (0, 1), result.output
    if result.exit_code == 0:
        assert "Optimal path" in result.output
    else:
        assert "No path found" in result.output

def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0, result.output
    assert "sa-sv-duality" in result.output
```
(`benchmark` absichtlich ausgelassen, falls es lange laeuft/instabil ist
-- bitte kurz selbst pruefen, ob ein `--fast`-Testaufruf praktikabel ist,
und falls ja, denselben Konsistenz-Stil wie beim `afet-tensions`-
Benchmark-Test aus Ticket 4 verwenden (Exit-Code gegen die echte
`run_benchmarks(fast=True)`-Rueckgabe pruefen, nicht "alles muss
bestehen" annehmen).)

### `sandpile-utac` (`src/sandpile_utac/cli.py`, Befehle: `run`, `phase-diagram`, `crep-spectrum`, `benchmark`, `version`)

**Wichtig: kleine Parameter verwenden, Defaults sind fuer echte
Simulationen gedacht (grains=50000) und waeren als Test zu langsam.**

```python
from typer.testing import CliRunner
from sandpile_utac.cli import app

runner = CliRunner()

def test_run_small():
    result = runner.invoke(app, ["run", "--L", "16", "--grains", "500", "--warmup", "100"])
    assert result.exit_code == 0, result.output
    assert "CREP state" in result.output
    assert "UTAC state" in result.output

def test_phase_diagram_small():
    result = runner.invoke(app, ["phase-diagram", "--L", "16", "--n-points", "3"])
    assert result.exit_code == 0, result.output
    assert "Critical density estimate" in result.output

def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0, result.output
    assert "sandpile-utac" in result.output
```
(`crep-spectrum` und `benchmark` absichtlich ausgelassen -- `crep-spectrum`
ruft `update_from_live()` auf, was von externen/Live-Daten abhaengen
koennte; `benchmark` hat unklare Laufzeit mit Default-Parametern. Bitte
BEIDE kurz selbst antesten und zurueckmelden, ob sie praktikabel
(schnell, offline-faehig) sind -- wenn ja, gerne im selben Stil
ergaenzen, wenn nein, als offenen Punkt im Bericht vermerken statt
zu erzwingen.)

**Zusaetzlich pruefen:** `sandpile-utac` hat eine weitere,
unbekannte Datei `tests/test_diamond_interface.py` (anderer Name als
`test_diamond.py`). Bitte deren Inhalt nach der obigen Methodik pruefen
(eigenes Paket getestet -> behalten; nur diamond_setup -> loeschen) und
im Bericht explizit erwaehnen, welcher Fall zutraf.

### `seismic-utac` (`src/seismic_utac/cli.py`, Befehle: `run`, `b-value-monitor`, `predict`, `benchmark`)

```python
from typer.testing import CliRunner
from seismic_utac.cli import app

runner = CliRunner()

def test_run_small():
    result = runner.invoke(app, ["run", "--duration", "2.0"])
    assert result.exit_code == 0, result.output
    assert "UTAC Seismic Results" in result.output

def test_b_value_monitor_small():
    result = runner.invoke(app, ["b-value-monitor", "--n-events", "50"])
    assert result.exit_code == 0, result.output
    assert "b-value monitor" in result.output

def test_predict():
    result = runner.invoke(app, ["predict"])
    assert result.exit_code == 0, result.output
    assert "Seismic Forecast" in result.output
```
(`benchmark` absichtlich ausgelassen -- bitte kurz selbst antesten und
zurueckmelden, ob praktikabel; falls ja, im Konsistenz-Stil ergaenzen wie
oben beschrieben.)

---

## Gesamt-Akzeptanzkriterien

- Fuer JEDES der 12 Pakete einzeln melden: welche Dateien geloescht,
  welche ersetzt, wie viele Tests laufen jetzt, alle gruen?
- Keine Aenderung an Nicht-Test-Code in irgendeinem Paket.
- `Architektur--Planungsprojekt/_diamond-setup-legacy` NICHT anfassen.
- Kein Versions-Bump, kein CHANGELOG-Eintrag, kein Zenodo-Release in
  irgendeinem Repo -- macht Claude nach Review, pro Repo einzeln.
- Bei jeder ausgelassenen/unklaren Datei (siehe "bitte selbst pruefen und
  zurueckmelden"-Stellen oben) den tatsaechlichen Befund melden, nicht
  raten oder stillschweigend eine Annahme treffen.

## Bitte NICHT tun

- `diamond-setup` selbst NICHT anfassen.
- Keine neuen Abhaengigkeiten.
- Keine Annahmen ueber Laufzeit/Netzwerkzugriff treffen, die nicht
  tatsaechlich getestet wurden.
