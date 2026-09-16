# Folgetickets — Revision 2, 16. September 2026

## Neue offene Punkte aus der Formalismus-Konsolidierung

Diese Tickets betreffen gezielte Folgearbeiten. Die mathematischen Korrekturen in den Dokumenten sind umgesetzt; die hier genannten Produktionscodeänderungen sind nicht Bestandteil dieses abgeschlossenen Dokumentationsschritts.

| ID | Gegenstand | Nächster prüfbarer Schritt | Status |
|---|---|---|---|
| F02 | Bedeutungen im Ökosystem | Kommentare, Datenfelder und Rechnungen auf die getrennten Größen prüfen; S/K/R/V nicht still auf C/R/E/P abbilden | offen |
| F03 | Neural `effective_r()` | Zeitabstände explizit behandeln; Schätzung bei verschiedenen Δt prüfen; fehlende Identifizierbarkeit nicht als Messung eines Defaults ausgeben | offen |
| F04 | Solar geomagnetischer Pfad | Peak-Ereignis versus verfügbare Erholung dokumentieren; eine fortlaufende Zustandskopplung nur mit eigener Modellentscheidung ergänzen | offen |
| F05 | Resilience Kopplungsregister | Einfluss-/Lastscore als solchen typisieren; Onsager-Bezeichnung erst mit Fluss/Kraft-Bilanz | offen |
| F06 | Γ-Pfade und gemeinsame Defaults | Herkunft, Verbraucher und Kalibrier-/Testtrennung pro Pfad erfassen; keine erzwungene neue Verdrahtung | offen |
| F07 | Selbstähnlichkeit | Transformation, Zeitskala, Fehlermaß und unabhängigen Modellvergleich vorab festlegen | offen |

Aktuelle Definitionen: [FORMALISM.md](FORMALISM.md). Prüfplan: [ROADMAP.md](ROADMAP.md). Die Gegenbeispiele und korrigierten Modellbeziehungen stehen in [VERIFICATION.md](VERIFICATION.md).

## Erhaltene Paket-Folgetickets vom 15. September

Der folgende Bestand bleibt vollständig erhalten. Seine Prüf- und Releaseangaben sind die damaligen Arbeitsnachweise; diese Dokumentrevision behauptet keine erneute Ausführung. Spätere Präzisierungen einzelner Worked Examples (etwa AMOC 1.3.3 oder Cygnus 1.0.2) stehen in den jeweiligen aktuellen Beispieldateien und der Roadmap.

# Phase-2-Folgetickets (nicht Teil des jeweiligen Haupttickets)

Sammelt Funde, die waehrend eines Phase-2-Reviews auftauchen, aber nichts
mit dem eigentlichen Ticket zu tun haben -- damit sie nicht verloren
gehen, ohne das laufende Ticket aufzublaehen.

## Offen

- **`phaethon-chimera` Prediction #47 (Perihel-Durchgaenge vor Flyby)**:
  urspruenglich als "4.0 folgt arithmetisch nicht aus einer einfachen
  Perioden-Divisionsschaetzung" geflaggt. Mit echten Bahnelementen von
  JPL SBDB (tp=JD 2461285.616438 TDB, period=523.6665665 d, Loesung
  2026-06-25) nachgerechnet: reale Periheldurchgaenge liegen auf
  2026-09-02, 2028-02-07, 2029-07-15, 2030-12-21 -- nicht gleichmaessig
  ueber Kalenderjahre verteilt, wie eine Perioden-Division annimmt.
  `4.0` IST mit echten Daten konsistent, WENN der JFY2030-Flyby
  (Apr 2030-Mar 2031) am oder nach dem 2030-12-21 stattfindet; `3.0`
  waere korrekt, falls davor. JAXAs oeffentlicher Zeitplan nennt bisher
  nur "JFY2030" ohne Monat -- bleibt offen, aber jetzt praezise auf
  "3 oder 4, abhaengig vom noch nicht veroeffentlichten Flyby-Monat"
  eingegrenzt (vorher: "unklar um ~2"). Dokumentiert in
  `destiny_predictions.py` (Prediction #47).

## Erledigt

- **`aeon-trikaya`: Git-Remote fehlte** -- rein lokales Repo (2 Commits,
  `master`-Branch), nie zu GitHub gepusht. Johann bestaetigt: kein
  Absicht wie bei `vesta-sim`, sollte veroeffentlicht werden. Vor dem
  Push: `master`->`main` umbenannt (Oekosystem-Konvention), Test-Artefakte
  (`aeon_proto_*.yaml`, `test_log.yaml`, die die eigene Testsuite per
  Default im Arbeitsverzeichnis erzeugt) zu `.gitignore` ergaenzt, 76/76
  Tests lokal verifiziert. Repo erstellt und gepusht:
  https://github.com/GenesisAeon/aeon-trikaya (public, `main`). Noch
  OHNE die Standard-GenesisAeon-Release-Infrastruktur, die andere Pakete
  laengst haben (`.zenodo.json`, CI/Release-Workflows, CONTRIBUTING.md,
  Issue-Templates) -- war nicht Teil dieser Anfrage, waere ein
  natuerlicher naechster Schritt.

- **`phi-scaling-validator`: zwei redundante Release-Workflows** --
  `publish.yml` (klassisches `PYPITOKEN`-Secret, funktionierte) und
  `release.yml` (Trusted Publishing via `environment: pypi`, dessen
  Publisher nie bei pypi.org registriert war und daher bei jedem
  Tag-Push fehlschlug: `invalid-publisher`). Zusammengefuehrt in ein
  einzelnes `release.yml`, das den bereits funktionierenden
  Token-Upload nutzt; `publish.yml` entfernt, ungenutzte
  `id-token: write`-Permission entfernt. YAML-Syntax lokal validiert,
  CI nach dem Push gruen. Volle Bestaetigung erst beim naechsten
  Tag-Release moeglich (Release-Workflow triggert nur auf Tags, nicht
  auf normale Pushes).

## Erledigt (vorherige Runde)

- **`phaethon-chimera`: vollstaendiger Audit der restlichen 44 DESTINY+-
  Vorhersagen (#2, #5-47)** -- stichprobenartige Gegenpruefung aller
  Vorhersagen mit echten externen Quellenangaben (ZTF, STEREO, Hanus et
  al. 2016, JAXA-Missionsplan, Geminiden-Literatur) sowie der
  paketinternen Physik-Funktionen. Drei echte, unabhaengig verifizierte
  Fehler gefunden und korrigiert:
  - **#26 (mittlerer Radius)**: war 2,78 km, zugeschrieben "Hanus et al.
    2016 Okkultationsdaten" -- der echte Hanus et al. 2016 (A&A 592, A34)
    Befund ist ein Durchmesser von 5,1±0,2 km aus Thermophysik-Modellierung
    von Infrarotdaten, weder der Wert noch die Methode stimmten. Korrigiert
    auf 2,55 km (=5,1/2), Quellenangabe korrigiert.
  - **#40 (Auswurfgeschwindigkeit)**: war fest auf 1,2 m/s codiert, aber
    `GeminidModel.ejection_velocity_ms()` (die eigene Fluchtgeschwindigkeits-
    Formel des Pakets, v_esc=√(2GM/r)) wurde nie tatsaechlich aufgerufen, um
    diesen Wert zu erzeugen -- mit den eigenen Parametern (ρ=1700 kg/m³)
    ergibt sich ≈2,49 m/s. Vorhersage und die (gleichermassen falsche)
    Docstring-Behauptung der Funktion korrigiert.
  - **#46 (DESTINY+ Flyby-Jahr)**: war 2029, ein aelterer Missionsplan.
    JAXAs aktueller oeffentlicher Zeitplan (Traegerraketenwechsel auf H3)
    zielt auf JFY2030 fuer den Phaethon-Flyby. `DESTINY_FLYBY_YEAR`
    korrigiert und in README.md, `.zenodo.json`, `__init__.py`, `system.py`
    propagiert.
  - Zusaetzlich `data/ztf_photometry_summary.yaml` markiert (nicht
    geloescht): wird von keinem Code tatsaechlich geladen, und die
    `genesisaeon_utac_fit`-Sektion entspricht exakt bereits bestehenden
    Oekosystem-Defaults (σ=2,2, Γ=0,165) statt einer glaubwuerdigen
    eigenstaendigen Anpassung an die spaerlichen echten Daten daneben.
  - Vorhersagen #5-25, #27-35, #38-45 sind reine UTAC/Chimera/SOC-
    Modellausgaben ohne externe Literatur zum Gegenpruefen vor dem Flyby --
    unveraendert gelassen. #36 (Geminid-ZHR) und #37 (Stream-Alter) gegen
    echte publizierte Schaetzungen geprueft und konsistent befunden, auch
    wenn die "UTAC-Modell"-Zuschreibung nicht unabhaengig verifizierbar ist.
  - #47 (Perihel-Durchgaenge) hat eine verbleibende, dokumentierte
    Inkonsistenz -- s. "Offen" oben. Released als `1.0.3`, live bestaetigt
    auf PyPI.

- **`beta-clustering-utac` (P32): "σ≈2.2 emerges from the β
  distribution (UTAC v1.0 finding)" numerisch nachgerechnet -- Behauptung
  ist FALSCH.** `sigma_from_beta_distribution()` (die eigene Formel des
  Pakets) liefert auf den eigenen Daten (Standard-Synthetik-Generator UND
  literaturzitierende `data/utac_v1_78_systems.yaml`) σ≈1.28, nicht 2.2 --
  eine ~42%-Abweichung. `BETA_SCALE=2.2` ist derselbe geteilte
  Oekosystem-Default wie in `amoc-utac`/`afet-tensions`, keine
  eigenstaendige Herleitung fuer diese Domaene. Zusaetzlich entdeckt:
  dieselbe "measured-but-unused"-Diskonnektion wie bei `amoc-utac`
  -- `system.py`s `_build_crep_state()` nutzt immer den hartcodierten
  Default, nie den von `_run_cycle()` berechneten und separat
  ausgegebenen σ≈1.28-Wert. Nur die Falschbehauptung korrigiert
  (Kommentare/README/`.zenodo.json`), `BETA_SCALE`-Zahlenwert
  unveraendert gelassen -- keine unabhaengigen Daten, um einen
  "richtigen" Wert zu rechtfertigen. Released als `1.1.1`, live
  bestaetigt auf PyPI.

- **Diamond-setup 2.3.0 `bridge_adapted`-Feld bricht `==`-Exact-Match-
  Tests oekosystemweit** -- entdeckt waehrend der `beta-clustering-utac`-
  Pruefung (lokale `diamond-setup` war veraltet auf 2.2.0 gepinnt, echte
  PyPI-Version 2.3.0 fuegt additiv `bridge_adapted: bool` zu `CREPState`
  hinzu). Lokal via `pip install --upgrade diamond-setup` behoben, dann
  gezielt per Grep nach allen `test_get_crep_state_keys`-artigen Tests im
  Oekosystem gesucht. Betroffen: `beta-clustering-utac` (behoben in
  1.1.1, s.o.), `implosive-origin-utac` (behoben, `1.1.0`->`1.1.1`),
  `phi-scaling-validator` (behoben, `1.1.0`->`1.1.1`). NICHT betroffen:
  `solar-flare-utac` (nutzt eigene lokale `CREPState`-Klasse, nicht
  `diamond_setup.protocol`). Alle drei Fixes: exakter Set-Vergleich durch
  Teilmengen-Check (`{"C","R","E","P","Gamma"} <= set(state.keys())`)
  ersetzt. **Offene Frage, noch nicht geprueft:** ob die bereits vorher
  in dieser Runde released Pakete (`amazon-utac`, `hikari-ledger`,
  `amoc-utac`, `cygnus-jet-utac`, `solar-flare-utac`,
  `neural-avalanche-utac`, `phaethon-chimera`) denselben
  `diamond_setup.protocol.CREPState`-Exact-Match-Testmuster haben und
  durch die lokale 2.2.0-Veraltung faelschlich als "gruen" durchgelaufen
  sind -- noch nicht zurueckgeprueft.

- **`phi-scaling-validator`: falsche DOI in `test_to_zenodo_record`** --
  erwartete `afet-tensions`' DOI (`10.5281/zenodo.17472834`) statt der
  eigenen (`10.5281/zenodo.20513358`); derselbe Copy-Paste-Fehler wie
  zuvor bei `sa-sv-duality`. Korrigiert in `1.1.1`.

- **`solar-flare-utac`: PyPI Trusted Publishing** -- hatte seit dem
  allerersten v1.0.0-Release (2026-06-25) nie funktioniert. Johann hat
  den Trusted-Publisher-Eintrag bei pypi.org ergaenzt (2026-09-15);
  `gh run rerun --failed` danach erfolgreich. Live bestaetigt: `1.0.1`.

- **`cygnus-jet-utac`, `hikari-ledger`: PyPI Trusted Publishing hatte NIE
  funktioniert** -- `invalid-publisher` seit dem jeweils allerersten
  Release. Johann hat fuer beide einen Trusted-Publisher-Eintrag bei
  pypi.org ergaenzt (2026-09-15); `gh run rerun --failed` danach fuer
  beide erfolgreich. Live bestaetigt: beide zeigen `1.0.1`.

- **`resilience-core`: `CI`-Workflow (ruff+mypy Lint) war seit mindestens
  2026-08-01 bei jedem Push auf `main` rot (5/5 Runs `failure`), ohne
  Releases zu blockieren.** Zwei Ursachen: eine zu lange Docstring-Zeile
  in `src/resilience_core/__init__.py` (umgebrochen), unsortierte Imports
  in `tests/test_diamond.py` (ruffs eigenen Sortiervorschlag angewendet:
  `pytest`+`diamond_setup` als Drittanbieter-Gruppe, `resilience_core` als
  eigene Erstanbieter-Gruppe danach). `ruff check`+`mypy` lokal sauber,
  v1.0.3 released (2026-09-15), CI zum ersten Mal seit Wochen gruen.

- **`sandpile-utac`, `seismic-utac`: `CI`-Workflow (`Tests (Python 3.10)`)
  war seit 2026-07-17 bei jedem Push rot**, weil `diamond-setup>=2.2.0`
  seit 2026-06-25 `Requires-Python >=3.11` verlangt, aber beide Pakete
  noch `requires-python = ">=3.10"` deklarierten (alle anderen 10 Ticket-
  4/5-Pakete standen bereits korrekt bei `>=3.11`). Behoben: `requires-
  python` auf `>=3.11` gesetzt, 3.10-Zeile aus beiden CI-Matrizen entfernt.
  Dabei aufgedeckt: der `Lint`-Job (`ruff` gefolgt von `mypy` im selben
  Schritt) war durch den vorher fehlschlagenden `ruff`-Schritt seit
  Langem nie bis zu `mypy` gekommen -- nach dem Ruff-Fix liefen erstmals
  wieder 13 (`sandpile-utac`) bzw. 15 (`seismic-utac`) vorbestehende
  `mypy --strict`-Fehler auf (fehlende Generic-Typparameter auf
  `np.ndarray`, jetzt `np.ndarray[Any, Any]` -- selbes Muster wie in
  `afet-tensions`; ausserdem ein `matplotlib.cm.viridis`-Typisierungsfehler
  in `sandpile-utac`, behoben via `plt.get_cmap("viridis")`).
  `seismic-utac`s mypy-Konfiguration hatte zusaetzlich einen ungueltigen
  Fehlercode (`"untyped-decorator"`, mypy-Warnung, keine echte Suppression)
  -- entfernt, da nicht mehr benoetigt (verifiziert: `afet-tensions` hat
  eine echte Typer-CLI und besteht `mypy --strict` ohne jede Decorator-
  Sonderregel). `ruff check`+`mypy` in beiden Paketen lokal sauber,
  v1.0.2 released (2026-09-15), `CI` bei beiden zum ersten Mal seit
  2026-06-25 wieder komplett gruen (Lint + Tests).

- **Stale editable installs auf `.claude/worktrees/<paket>-vendor-fix/`
  statt Hauptcheckout, in 8 von 12 Ticket-5-Paketen entdeckt (2026-09-15).**
  `phaethon-chimera`, `sa-sv-duality`, `sandpile-utac`, `seismic-utac`,
  `cellular-genesis`, `eml-utac-bridge`, `vrig-cosmological`, `worldview`
  waren via `pip install -e` auf alte, unabhaengige
  `.claude/worktrees/<paket>-vendor-fix/`-Verzeichnisse verlinkt statt auf
  den Hauptordner -- vorbestehender Umgebungsfehler. Alle 8 per
  `pip install -e .` aus dem jeweiligen Hauptordner neu installiert und
  per `import <paket>; print(<paket>.__file__)` verifiziert. Die alten
  `-vendor-fix`-Worktree-Verzeichnisse selbst wurden NICHT angefasst.

- **`sa-sv-duality::test_system_zenodo_record`** -- hartkodierte
  `afet-tensions`' DOI statt der eigenen. Beim v1.0.1-Bump (2026-09-15)
  korrigiert auf `10.5281/zenodo.20842509` (passend zu `__zenodo__` in
  `__init__.py`).

- **`worldview::test_cli.py::TestVersionFlag::test_version_short_flag`**
  -- Rich-ANSI-Splitting-Bugmuster bei der `-V`-Flag-Pruefung. Beim
  v1.0.1-Bump (2026-09-15) per ANSI-Escape-Strip vor dem Assert behoben.

- **resilience-core: PyPI Trusted Publishing** -- Johann hat den fehlenden
  Trusted-Publisher-Eintrag direkt bei PyPI ergaenzt (2026-09-15). Re-Run
  von GitHub-Actions-Run `34951902193` (`gh run rerun --failed`) danach
  erfolgreich: PyPI zeigt `1.0.1`/`1.0.2` live (JSON-API bestaetigt),
  GitHub-Release veroeffentlicht. Offen bleibt nur die unabhaengige
  Verifikation, ob Zenodo tatsaechlich eine neue Version archiviert hat
  (der "Publish to Zenodo"-Workflow-Schritt selbst ist weiterhin nur ein
  Platzhalter-Echo, siehe `release.yml`).

- **`cellular-genesis`, `eml-utac-bridge`, `phaethon-chimera`: PyPI
  Trusted Publishing hat NIE funktioniert** -- `gh run list` zeigte, dass
  der `Release`-Workflow bei allen drei Paketen seit ihrem initialen
  v1.0.0-Release (Juni 2026) durchgehend an `invalid-publisher` scheiterte
  (deren live stehende 1.0.0-Versionen wurden damals also ausserhalb
  dieser Pipeline hochgeladen, vermutlich manuell per API-Token). Johann
  hat fuer alle drei Projekte einen Trusted-Publisher-Eintrag bei pypi.org
  ergaenzt (2026-09-15); `gh run rerun --failed` danach fuer alle drei
  erfolgreich. Live bestaetigt (PyPI JSON-API, nach kurzer CDN-Verzoegerung
  fuer cellular-genesis/eml-utac-bridge): alle drei zeigen `1.0.1`.

- **`worldview::tests/test_cli.py` faelschlich als diamond-setup-
  Kontamination geloescht (Ticket 5, 2026-09-15).** GrokBots Suche
  `find src -iname cli.py` fand `worldview`s eigenes CLI-Modul nicht, weil
  es unter `src/worldview/cli/main.py` liegt (nicht `cli.py` direkt) --
  daher faelschlich als "keine eigene CLI" eingestuft und die Datei
  geloescht, OHNE ihren Inhalt zu pruefen (Verstoss gegen die im Prompt
  selbst verlangte Methodik). Tatsaechlich war es eine vollstaendige,
  funktionierende Testsuite fuer `worldview.cli.main.app`
  (`--version`/`-V`/`info` etc.), erkennbar auch daran, dass die
  Coverage nach Loeschung von 99% auf 71% (`src/worldview/cli/main.py`:
  0%) fiel -- das vermeintlich "vorbestehende" `fail_under=99`-Problem aus
  GrokBots Bericht war also real, aber selbstverschuldet, nicht
  vorbestehend. Per `git checkout HEAD -- tests/test_cli.py`
  wiederhergestellt, Coverage wieder bei 99.59%. `test_preset.py`/
  `test_validator.py` fuer `worldview` dagegen unabhaengig geprueft und
  zu 100% echte diamond-setup-Kontamination bestaetigt -- deren Loeschung
  bleibt bestehen.

- **`phaethon-chimera::test_run_with_n_orbits` (neu von Ticket 5
  geschrieben) schlug nach Fix der Stale-Install-Umgebung real fehl --
  Rich-ANSI-Splitting-Bugmuster (`assert "5 orbits" in result.output`
  scheitert, weil rich die "5" separat hervorhebt).** In Claude-Review
  direkt behoben (ANSI-Escape-Codes vor dem Assert per Regex entfernt,
  gleiches Muster wie beim diamond-setup-CLI-Bug oben). 56/56 Tests
  gruen danach, deckt sich mit GrokBots urspruenglicher Zahl -- aber aus
  den richtigen Gruenden (GrokBots Testlauf lief vermutlich in einer
  korrekten Umgebung und hatte diesen Bug nie gesehen, waehrend Claudes
  erster Review-Lauf durch die Stale-Install falschen Code testete, der
  zufaellig ebenfalls fehlschlug -- zwei unabhaengige Probleme, die sich
  ueberlagert haben).
