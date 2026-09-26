# SCF G0–G7: unabhängiges Review und Umsetzungshilfe

**Stand:** 26. September 2026. **Geprüfter Commit:** `5563e6778359cffdd6e844c8a5cd4eabc7c717dc`.

Repository: <https://github.com/GenesisAeon/scoped-correspondence-formalism/tree/5563e6778359cffdd6e844c8a5cd4eabc7c717dc>

## Urteil

Die Erweiterung verbindet konkrete mathematische Strukturen mit einem reproduzierbaren realen Datenpilot. Die Trennung zwischen Halo-Parameterprodukt, tatsächlicher Säulendichte, Homologie und Beobachtungsäquivalenz ist sinnvoll. Die gemischten Pilotresultate lassen sich nachrechnen. G6 offen zu halten, ist weiterhin richtig.

**Die Aussage „G0–G5 und G7 vollständig; nur G6 offen“ ist allerdings zu stark.** Es gibt einen erheblichen numerischen Fehler im Burkert-Zweig für kleine Radien, einen unberichteten NFW-Randtreffer im echten Pilot und mehrere Lücken bei Statusweitergabe und G5-Abnahme. Der Burkert-Fehler verändert die veröffentlichten Pilotresultate in meiner Gegenrechnung nicht. Er muss trotzdem vor weiterer Nutzung des Profilmoduls behoben werden.

Empfehlung: eine begrenzte Korrekturrunde R1–R7, danach die noch fehlenden G5-Auswertungen abschließen. Keine neue Domäne ist nötig, um hier einen wesentlichen wissenschaftlichen Fortschritt zu erzielen.

## Prüfgrundlage und Grenzen dieses Reviews

- GitHub-HEAD und der angegebene Commit stimmten zum Prüfzeitpunkt überein. Der beobachtete CI-Lauf [36243671219](https://github.com/GenesisAeon/scoped-correspondence-formalism/actions/runs/36243671219) war erfolgreich.
- Die lokalen Produktions- und Verifikations-Pythondateien wurden gegen die Git-Blob-Hashes dieses Commits abgeglichen. Die Gegenrechnungen laufen auf diesem Stand.
- Alle sechs neuen Verifikationsskripte ausgeführt: **42/42 synthetische beziehungsweise analytische Einzelprüfungen und 5/5 echte Datenprüfungen**, ohne Skip. Das sind 47 Einzelprüfungen; die gesamte historische 99-Skripte-Suite wurde hier nicht erneut lokal ausgeführt.
- Beide offiziellen SPARC-Dateien separat heruntergeladen; Größe und SHA-256 stimmen exakt mit dem Repository-Protokoll überein. Rohdaten blieben außerhalb des Repo-Snapshots und sind nicht Teil der Übergabe.
- Den realen Pilot erneut ausgeführt, einschließlich Auswahl, aller zwölf deskriptiven Fits und aller sechs Außenradien-Vergleiche. Ergänzend unabhängige Quadraturen, gezielte Gegenbeispiele und Optimierungsdiagnostik.
- Laufzeit der Gegenrechnungen: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0. Kleine Unterschiede letzter Dezimalstellen sind zwischen Plattformen möglich.
- G6: Verlags- und SSRN-Zugriff erneut versucht; beide Seiten lieferten über den verwendeten Abrufweg 403. Kein Volltext beschafft. Das ist eine Zugriffsgrenze dieser Prüfung, keine Aussage, dass keine legal verfügbare Fassung existiert.
- Keine Änderungen am GitHub-Repository vorgenommen. Eine isolierte Korrektur der Burkert-Reihe wurde ausschließlich im Speicher verwendet, um Auswirkungen auf den Pilot zu messen.

## Unabhängig bestätigte Ergebnisse

### Daten und Auswahl

| Datei | Bytes | SHA-256 |
|---|---:|---|
| SPARC_Lelli2016c.mrt | 28259 | `5aa0501f6b0d881fa579030e315e7b5b6ef561a5bd3a07472f9929c7e5728243` |
| MassModels_Lelli2016c.mrt | 269518 | `9108994b12cc401b94a1768beca61c53ec354779385c9c9cc571049f3043244c` |

175 Metadatenzeilen, 3391 Komponenten­zeilen, 361 Zeilen mit negativem Gasbeitrag. Die Referenzentfernungen beider Tabellen stimmen für diese Dateiversion überein. Alle 175 Metadatenzeilen sind 131 Zeichen lang. Die dokumentierte Unvereinbarkeit mit dem gedruckten 113-Byte-Schema bestätigt sich; die begründete Umstellung **nur der Metadatentabelle** auf strikte 19-Token-Auswertung ist angemessen. Die Komponententabelle bleibt festspaltig.

94 geeignete Galaxien, Drittelgrößen 32/31/31, dieselben sechs Entwicklungs- und sechs Evaluationsgalaxien. Alle zwölf deskriptiven Burkert-Fits konvergieren ohne endgültigen Randtreffer. Das geschätzte Produkt reicht von ungefähr 96,86 bis 996,89 M_sun/pc².

### Reproduzierter Außenradien-Test

RMSE in km/s, Referenzannahmen des aktuellen Piloten:

| Galaxie | Burkert | NFW | algebraischer MOND-Kontrollfall | kleinster RMSE |
|---|---:|---:|---:|---|
| NGC3109 | 0,8535 | 11,2683 | 9,2569 | Burkert |
| F568-V1 | 5,9053 | 20,2497 | 22,4548 | Burkert |
| NGC1003 | 15,4821 | 7,8426 | 4,7613 | MOND |
| NGC3726 | 32,3595 | 23,1312 | 7,2012 | MOND |
| UGC02487 | 14,5660 | 9,7009 | 62,1372 | NFW |
| NGC6674 | 31,0770 | 27,4990 | 19,2966 | MOND |

Die Verteilung **2/6, 1/6, 3/6** ist bestätigt. Die Tabellenwerte stimmen bis auf kleine Rundungsunterschiede mit der Dokumentation überein. Dies bleibt ein Vergleich bedingter radialer Extrapolation unter festen baryonischen Annahmen und einem bestimmten algebraischen MOND-Modell.

Die reine Korrektur des nachstehend beschriebenen Burkert-Faktors änderte in dieser Umgebung weder die zwölf `mu_h`-Schätzer noch die 18 Test-RMSE-Werte: maximale gemessene Änderung jeweils **0,0**. Der kleinste `r/r0`-Wert an den zwölf endgültigen Modus-A-Fits liegt bei ungefähr 0,0559 und damit deutlich oberhalb der fehlerhaften Region.

## Befunde nach Priorität

| ID | Priorität | Befund | Bezug zum veröffentlichten Pilot |
|---|---|---|---|
| R1 | P1 | Burkert-Reihe liefert halbe Masse und Beschleunigung | Pilot bei isolierter Korrektur unverändert; Profil-API falsch |
| R2 | P2 | Fitstatus und Grenzen gehen im Vergleich verloren; realer NFW-Randtreffer | NGC3109 tatsächlich betroffen |
| R3 | P2 | Negative Gesamtbeschleunigungen werden still zu null | Gegenbeispiel; keine betroffenen endgültigen Fits in den zwölf Pilotgalaxien nachgewiesen |
| R4 | P2 | Falscher zentraler NFW-Grenzwert im Testvertrag | Keine Auswirkung auf positive SPARC-Radien |
| R5 | P2 | Unvollständige numerische und tabellenübergreifende Datenvalidierung | Aktuelle Dateien unauffällig; synthetisch nachgewiesene Lücke |
| R6 | P2 | G5-Abnahme: Produktprofile, Sensitivitäten und reproduzierbare Berichtsartefakte fehlen | Beschränkt die wissenschaftliche Interpretation |
| R7 | P2 | Suite-Zusammenfassung zählt übersprungene Datenprüfung als bestanden | CI-Aussage muss Ausführung und Skip trennen |

P1 bedeutet hier: vor weiterer fachlicher Nutzung korrigieren. P2 bedeutet: vor vollständiger Abnahme beziehungsweise Ausweitung auf weitere Daten abschließen. Es sind unterschiedliche Arten von Befunden, keine sieben behaupteten Fehler in den veröffentlichten Zahlen.

### R1 — Faktor 2 in der Burkert-Reihe

**Ort:** `src/scoped_correspondence/astrophysics/spherical_profiles.py`, `BurkertProfile._mass_bracket`, insbesondere Zeile 103; `verification/verify_galaxy_profiles.py`, Quadratur- und Umschalttest.

Der geschlossene Klammerausdruck lautet

\[
B(x)=\log(1+x)+\tfrac12\log(1+x^2)-\arctan x,
\qquad M(r)=2\pi\rho_0r_0^3 B(x).
\]

Seine korrekte Reihe ist

\[
B(x)=2\left(\frac{x^3}{3}-\frac{x^4}{4}+\frac{x^7}{7}-\frac{x^8}{8}+\cdots\right).
\]

Der Code verwendet die Klammer ohne diesen Faktor 2. Der Docstring sagt bereits „doubled here“, die Implementierung tut es jedoch nicht. Für `x<1e-3` sind deshalb Masse und Beschleunigung halbiert; die Kreisgeschwindigkeit beträgt nur `1/sqrt(2)` des richtigen Werts.

**Unabhängige Gegenrechnung:** `rho0=0.05 M_sun/pc³`, `r0=3000 pc`, `r=0.3 pc`, also `x=1e-4`:

| Größe | Implementierung | Dichtequadratur / richtige Relation |
|---|---:|---:|
| M(<r) [M_sun] | 0,0028272213307266956 | 0,005654442661453392 |
| M / M_ref | 0,5 | 1 |
| g / g_ref | 0,5 | 1 |
| v_c / v_ref | 0,7071067811865474 | 1 |

Bei `r=2.999997 pc` und `r=3.000003 pc` springt die implementierte Masse um den Faktor **2,000011997**. Der effektive-Dichte-Operator gewinnt bei `r=0.3 pc` nur **0,500000000003** der deklarierten Dichte zurück.

**Warum bisher grün:** Die unabhängige Massenquadratur beginnt erst bei `x=0.01`. Der „Stetigkeitstest“ vergleicht weit auseinanderliegende Radien `0.5*switch` und `2*switch` und lässt einen Massenquotienten bis 3200 zu. Das ist keine belastbare Stetigkeitsprüfung. Auch Homologie kann den Fehler nicht entdecken: eine falsch normierte Formel kann dieselbe Skalierung besitzen.

**Umsetzung:** Reihe im Klammerausdruck verdoppeln; eine einzige konsistente Massendarstellung für alle abgeleiteten Größen behalten.

**Abnahme:** unabhängige, dimensionslos skalierte Dichtequadratur bei `x=1e-6`, `1e-4` und auf beiden Seiten von `1e-3`; Grenzwert `M/(4*pi*rho0*r³/3) -> 1`; enger, fehlerkontrollierter Umschalttest; Rückgewinnung der Dichte auch innerhalb des Reihenzweigs. Keine nur aus demselben Produktionscode erzeugten Sollwerte.

### R2 — Unberichteter NFW-Randtreffer und verlorene Fitstatus

**Ort:** `src/scoped_correspondence/validation/galaxy_pilot.py`, `PredictiveScore` und `evaluate_baselines_on_holdout`, Zeilen 292–356.

Burkert wird mit drei Starts und einmaliger Grenzerweiterung gefittet. NFW erhält einen einzelnen Start und keine Grenzerweiterung. `sol_b.success` wird nicht ausgewertet. Auch Burkerts vorhandene Felder `status` und `boundary_hit` erreichen die Scoreausgabe nicht. Ein Score enthält nur Galaxie, Modell, MAE, RMSE und Punktzahl.

**Realer Befund: NGC3109, NFW-Trainingsfit.**

| Größe | Aktueller Fit | Einmalige Erweiterung der getroffenen unteren Dichtegrenze |
|---|---:|---:|
| log10(rho_s/[M_sun pc^-3]) | −4,000000000000 | −4,286067140284 |
| log10(r_s/kpc) | 2,218604884607 | 2,49999999999985 |
| Trainings-chi² | 126,3858705041 | 123,7034554072 |
| Test-RMSE [km/s] | 11,2682938 | 11,0407193 |
| Grenze aktiv | untere Dichte | obere Skalenlänge |

Die Erweiterung folgt nur der vorher vorgegebenen Regel und verwendet Trainingsdaten. Danach ist das Resultat weiterhin **grenzabhängig**. Es darf nicht still als vollständig freier NFW-Bestfit erscheinen. Die Rangfolge dieser Galaxie ändert sich dadurch nicht.

Zusätzliche Kontrolle: Drei NFW-Starts innerhalb der ursprünglichen Grenzen liefern bei allen sechs Galaxien praktisch dieselben besten Trainingskosten. Hier ist also kein anderer lokaler Fit als Ursache nachgewiesen. Das löst den Grenz- und Statusverlust nicht.

**Status-Gegenbeispiel:** In einem synthetischen Kontrolllauf wurden nur `success=False` und der Rückgabestatus der Optimierer gesetzt, bei unveränderten Zahlen. Der deskriptive Fit meldet dann `not_converged`; `evaluate_baselines_on_holdout` liefert dennoch unveränderte gewöhnliche Scores ohne Warnstatus.

**Umsetzung:** gemeinsames transparentes Fitprotokoll für beide Halo-Familien; gleiche vorab festgelegte Start- und Erweiterungsregeln, jeweils in den passenden Profilparametern. Ausgabe um Trainingsparameter, Erfolg/Grund, tatsächlich verwendete Grenzen, initialen Randtreffer, Erweiterung und endgültigen Randtreffer ergänzen. Ein möglicher diagnostischer Score eines fehlgeschlagenen Fits muss ausdrücklich als solcher markiert werden und darf nicht unbemerkt in Siegerzählungen eingehen.

**Abnahme:** NGC3109 wird als grenzabhängig sichtbar; ein kontrollierter Optimierungsfehler bleibt bis in die Vergleichstabelle sichtbar. Änderungen der Testgeschwindigkeiten verändern weder Starts noch Erweiterungen noch Trainingsparameter. Ursprüngliche Pilotresultate archivieren; die Diagnoseerweiterung erhält einen neuen Ergebnisstand.

### R3 — Stilles Nullsetzen ungültiger Gesamtbeschleunigung

**Ort:** `galaxy_pilot.py`, Zeilen 184–186, 326–327 und 348.

Mehrere Pfade verwenden `np.clip(g_total, 0, None)` vor der Wurzel. Bei negativer Gesamtbeschleunigung liefert das Modell damit scheinbar eine gültige Kreisgeschwindigkeit von null. Dieser Punkt besitzt im verwendeten Modell keine solche Kreisbahn. Die Kommentarformulierung „pathological synthetic cases“ ersetzt keinen Geltungsbereichsstatus.

Ein selbst erzeugter Datenpunkt bei `r=1000 pc` mit `Vgas=-1000 km/s`, ohne stellaren Beitrag und mit Burkert `(rho0,r0)=(0.05,3000)` ergibt `g_total=-999.3209907779398 (km/s)²/pc`. `_predicted_v_obs` liefert **0,0 km/s**, ohne Fehlerstatus.

Negativer Gasbeitrag allein ist dagegen zulässig: Erst die korrekte vorzeichenbehaftete Summe entscheidet. Der MOND-Kontrollfall benötigt darüber hinaus nichtnegatives `g_bar`. Die aktuelle MOND-Ausnahme kann den ganzen Modellvergleich abbrechen, während Halo-Ungültigkeit still gekappt wird.

In den zwölf ausgewählten Galaxien ist die baryonische Summe bei den Referenzannahmen überall positiv. Im Gesamtdatensatz existieren zwei negative baryonische Summen, beide bei UGC01281. Eine Erweiterung der Auswahl erreicht den Geltungsbereichsfall also auch mit echten Daten.

**Umsetzung:** Vorhersagegültigkeit explizit prüfen; ungültige endgültige Modellvorhersage mit Grund und Anzahl betroffener Punkte ausgeben. Für ungültige Zwischenparameter des Optimierers eine dokumentierte, numerisch geeignete Zulässigkeits- oder Strafbehandlung wählen; sie darf nicht als physikalische Vorhersage interpretiert werden. Gemeinsame Vergleichsmenge und Umgang mit modellspezifischer Ungültigkeit vorher festlegen.

**Abnahme:** Drei getrennte Fälle: negativer Gasbeitrag bei positiver Summe; negatives `g_bar` bei positiver Halo-Gesamtsumme; negative Gesamtsumme. Kein stilles Absolutwertbilden, Nullsetzen oder punktweises Auslassen zur Verbesserung von Scores.

### R4 — NFW: Ursprung und einseitiger radialer Grenzwert verwechselt

**Ort:** `NFWProfile.g` in `spherical_profiles.py`; `check_central_limits` in `verify_galaxy_profiles.py`, Zeilen 190–198; entsprechende Aussage in der Roadmap.

Aus

\[
M_{\rm NFW}(r)=2\pi\rho_s r_s r^2+O(r^3)
\]

folgt

\[
\lim_{r\to0^+}g(r)=2\pi G\rho_s r_s\ne0.
\]

Bei `rho_s=0.05`, `r_s=3000 pc` beträgt dieser Grenzwert **4,053641607755213 (km/s)²/pc**. Für `r/r_s=1e-9` liefert die Implementierung bereits **4,053641602350358**, an `r=0` aber null. Der Test nennt die Null für alle drei Profile einen zentralen Grenzwert.

**Präzisierung:** Der Richtungsvektor des sphärischen Kraftfelds ist genau im Ursprung nicht eindeutig; daraus darf kein kontinuierlicher Vektorgrenzwert konstruiert werden. Eine eigens erklärte Wertkonvention `g(0)=0` wäre etwas anderes als der Grenzwert der radialen Betragsfunktion. Der ursprüngliche Plan verlangte die Nullgrenzwerte ausdrücklich nur bei endlicher Zentraldichte.

**Umsetzung:** Den API-Vertrag ausdrücklich festlegen: entweder NFW-Beschleunigung bei exakt null zurückweisen und den einseitigen Grenzwert separat testen, oder für die skalare Radialfunktion deren Grenzwert verwenden und die fehlende Vektorrichtung dokumentieren. Eine beibehaltene Nullkonvention darf nicht als physikalischer radialer Grenzwert geprüft oder beschrieben werden.

**Abnahme:** NFW separat von Burkert/pseudoisothermisch prüfen. `M(0)=0` und `v_c(0)=0` bleiben korrekt.

### R5 — Datenvalidierung deckt nicht alle benutzten Größen ab

**Ort:** `src/scoped_correspondence/validation/sparc_data.py`, `parse_metadata_table` und `parse_component_table`; Auswahl/Verknüpfung in `galaxy_pilot.py`.

Die Parser versprechen Zurückweisung nichtendlicher numerischer Felder, prüfen aber nur Teilmengen. Nachgewiesen:

- `SBeff=inf` passiert die Metadatentabelle. Das Feld steuert die Drittelauswahl und erfüllt sogar die spätere Bedingung `SBeff>0`.
- `D_mpc=nan` passiert die Komponententabelle.
- Ein selbst erzeugter, ansonsten gültiger Satz mit Metadatenentfernung 10 Mpc und Komponentenentfernung 100 Mpc wird mit zwölf Galaxien ausgewählt. Es existiert keine gemeinsame Referenzentfernungsprüfung.

Die echten aktuellen Tabellen haben diese Abweichungen nicht. Es ist eine Lücke im Adaptervertrag, keine nachgewiesene Kontamination der veröffentlichten Ergebnisse.

**Umsetzung:** Alle numerischen Felder auf Endlichkeit prüfen; fachliche Gültigkeit und etwaige dokumentierte Fehlwertkodierung separat behandeln. Nicht pauschal alle Nullen verbieten. Eine gemeinsame Tabellenvalidierung prüft IDs und Referenzentfernung, einschließlich Konsistenz aller Zeilen derselben Galaxie. Rundungstoleranz am Dateiformat begründen. Auch Skalierungshelfer sollen unzulässige Faktoren/Winkel eindeutig zurückweisen.

**Abnahme:** Selbst erzeugte NaN/Inf-Fixtures für auswahlrelevante Größen, inkonsistente Entfernungen innerhalb und zwischen Tabellen, plus unverändert erfolgreiche Validierung der echten Dateien.

### R6 — G5 ist als Bestfit-Pilot umgesetzt, als vollständige Identifizierbarkeitsanalyse noch offen

**Orte:** `galaxy_pilot.py`, `docs/galaxy_pilot.md`, `GALAXY_DYNAMICS_ROADMAP.md`; ursprünglicher Implementierungsplan §§9.4, 10.2, 10.4–10.6.

Die vorhandenen `psi`- und `eta`-Felder sind nachträgliche Koordinaten des besten Fits. Sie sind **keine Profil-Likelihood**. Die synthetische Innenkurvenkontrolle zeigt Empfindlichkeit gegenüber Rauschen; sie ersetzt keine Untersuchung der zulässigen Produktwerte bei den realen Galaxien.

Zum ursprünglichen Abschluss fehlen:

1. Direkte Produktprofile unter Optimierung des verbleibenden Halo-Parameters.
2. Die geplanten gemeinsamen `±1 sigma`-Variationen von Entfernung und Inklination unter denselben Regeln für alle Modelle.
3. Ein eingecheckter lokaler Pilot-Aufruf, der Auswahl/Ausschlüsse, Trainingsparameter und Status, getrennte A/B-Ergebnisdateien sowie Residuen- und Profilgrafiken reproduziert. Vorhanden sind APIs und manuell dokumentierte Tabellen; der lokale G4-Datentest führt den G5-Pilot nicht aus.

Diese Punkte werden in der Roadmap nicht als verschoben gekennzeichnet. Deshalb ist „nur G6 offen“ sachlich falsch. Sie lassen sich ohne neue Rohdaten im Repository umsetzen.

**Konkreter Profilauftrag:** Für

\[
\psi=\log_{10}(\mu_h/[M_\odot pc^{-2}]),\qquad
\eta=\log_{10}(r_0/pc)
\]

bei jedem festen `psi` das Minimum

\[
q(\psi)=\min_\eta\chi^2\big(\rho_0=10^{\psi-\eta},\ r_0=10^\eta\big)
\]

berechnen. Die Zahlenwerte der Parameter stehen hier in den angegebenen Einheiten. Bestehende positive Parametergrenzen müssen korrekt transformiert werden: Bei den ursprünglichen Grenzen gilt `eta in [1,5.5]` und `psi-eta in [-4,1]`. Die zulässige Schnittmenge hängt damit von `psi` ab. Tatsächlich erweiterte Grenzen aus R2 gesondert berücksichtigen.

`q(psi)-q_min`, Scanbereich, Optimierungsstatus und Grenztreffer speichern. Flachheit auf einem endlichen Scan beweist keine globale Unbeschränktheit. Eine Schwellenüberschreitung ist nur unter angegebenen Fehler- und Regularitätsannahmen als Konfidenzgrenze interpretierbar; zunächst genügt eine ehrliche Profilkurve. Keine diagonale Fehlerfortpflanzung, die Dichte-Radius-Kovarianz verliert.

**Konkreter Sensitivitätsauftrag:** Vor der Neuberechnung das Raster festlegen, mindestens Referenz, `D±sigma_D`, `i±sigma_i` als einzeln veränderte Szenarien. Gemeinsame physikalische Grenzen dokumentieren. Radien und baryonische Komponenten mit D gemeinsam transformieren, beobachtete Geschwindigkeit und deren Fehler mit i gemeinsam transformieren; Halo-Parameter jeweils ausschließlich aus den Trainingspunkten neu schätzen. Keine der Szenarien nach Testleistung auswählen. Ergebnisse als Sensitivität, nicht als kalibrierte Unsicherheitsbänder kennzeichnen.

UGC02487 ist ein sinnvoller diagnostischer Einzelfall dafür. Der jetzige Ausreißer allein belegt noch nicht, welche Annahme ihn verursacht.

**Abnahme:** Reproduzierbare lokale CLI mit explizitem Rohdatenpfad und Hashprüfung; getrennte JSON/CSV-Ausgaben für A und B; tatsächliche Produktprofile für die Pilotgalaxien; sichtbare Referenz- und Sensitivitätsergebnisse. Grafiken aus Ergebnisdateien generieren. Ursprüngliche Evaluation erhalten, spätere Analysen als neue explorative Version kennzeichnen. Alternativ die Teilaufgaben ausdrücklich als offen führen und den G5-Abschlussanspruch zurücknehmen.

### R7 — Skip wird in der Zusammenfassung zu „passed“

**Ort:** `scripts/run_verification_suite.py`, `run_math_and_data`; lokaler SPARC-Test und Provenienzdokumentation.

Das Einzelprogramm behandelt fehlende Rohdaten korrekt: fünf Checks mit `status=skipped`, `all_skipped=true`, Rückgabecode 0. Der übergeordnete Runner wertet nur `returncode==0` aus und zählt dieses Skript als `passed`.

**Kontrolllauf mit ausschließlich diesem Skript und absichtlich fehlendem Rohdatenverzeichnis:**

```json
{
  "runner_summary": {"category": "data", "count": 1, "passed": 1, "failed_count": 0},
  "child_all_skipped": true,
  "child_check_statuses": "alle fünf: skipped"
}
```

Damit stimmt die pauschale Aussage der Provenienzdokumentation, ein übersprungener Lauf werde niemals als bestandene Datenprüfung berichtet, nur auf Ebene des Einzelreports. CI darf bei optional fehlenden Dateien weiterhin erfolgreich sein. Die Zusammenfassung muss aber `passed`, `skipped` und `failed` beziehungsweise erfolgreich beendete Prozesse von tatsächlich ausgeführten Prüfungen trennen.

**Umsetzung:** strukturierten Ergebnisvertrag zwischen Skripten und Runner schaffen; fehlende optionale Daten dürfen kein Scheinerfolg werden. Für ausdrücklich angeforderte lokale Datenverifikation einen strikten Modus anbieten, der fehlende Dateien als fehlende Voraussetzung meldet.

**Abnahme:** fehlende Dateien → sichtbarer Skip; vorhandene korrekte Dateien → fünf ausgeführte bestandene Checks; falscher Hash → sichtbarer Fehler. Dokumentation und CI-Zusammenfassung passen zusammen.

## Redaktionelle Korrekturen

1. `docs/sparc_data_provenance.md` behauptet im letzten Absatz weiterhin, beide Byte-Schemata seien explizit kodiert. Tatsächlich verwendet die Metadatentabelle die begründet abweichende Tokenisierung. Den veralteten Absatz ersetzen.
2. Die neue Prüfzahl konsistent zählen: vier `verify_galaxy_*.py`-Dateien mit 10+7+7+7 Checks, plus elf synthetische Adapterchecks = **42** synthetische/analytische Checks; plus fünf echte Checks = **47**. Die Roadmap nennt 49 synthetische Checks und fünf Galaxy-Skripte; der Übergabebericht nennt 55 neue Einzelprüfungen. Falls zusätzliche geänderte Alttests mitgezählt werden sollen, diese gesondert benennen.
3. `docs/galaxy_pilot.md` bezeichnet Donato und Yoon gemeinsam als aus größeren Populationen und Fitmethoden abgeleitete Populationsbefunde. Donatos empirischer Befund und Yoons berichtete modellabhängige Rechnung sind unterschiedliche Belegarten. Gerade bei blockiertem G6 keine gemeinsame Herkunft behaupten.
4. In der Gesamtbilanz ausdrücklich zwischen implementierter Formel, numerisch geprüftem Bereich, synthetischer Identifizierbarkeitskontrolle und realem Produktprofil unterscheiden. R1 zeigt, warum ein bestandener Referenzpunkt keine globale numerische Korrektheit belegt.

## Empfohlene Umsetzung für Claude-Code

Der folgende Auftrag ist auf die vorliegenden Befunde begrenzt. Vor Änderungen aktuellen HEAD feststellen und prüfen, welche Punkte inzwischen bereits behoben sind.

1. **Mathematik korrigieren:** R1 und R4 mit unabhängigen Gegenrechnungen und gezielten Regressionen. Danach bestehende G1–G3-Prüfungen.
2. **Vergleichsvertrag korrigieren:** R2 und R3; gemeinsame Fitdiagnostik und explizite Geltungsbereichsstatus. NGC3109 als realen, lokal reproduzierbaren Randfall dokumentieren.
3. **Datenvertrag und Berichte korrigieren:** R5 und R7 sowie die redaktionellen Punkte. Standard-CI weiterhin ohne externen Download.
4. **G5 vervollständigen:** R6. Zuerst Produktprofile und deterministische Ergebnisdateien, dann vorab definierte D/i-Sensitivitäten. Diese Reihenfolge liefert unmittelbar interpretierbare zusätzliche Wissenschaft.
5. **Gesamtprüfung und Bilanz:** vollständige vorhandene Suite und Linkchecker; lokale echte Datenprüfung zusätzlich, wenn verfügbar. Neue Ergebnistabellen mit ursprünglichem Stand vergleichen und Änderungen erklären. G6 bleibt unabhängig davon blockiert, bis die Quellenvoraussetzungen tatsächlich erfüllt sind.

Abschlusskriterium ist nicht eine höhere Anzahl grüner Skripte, sondern: Die aufgeführten Gegenbeispiele werden korrekt behandelt; der reale Vergleich berichtet seine Grenzen; Produktunsicherheit wird tatsächlich untersucht oder ausdrücklich als offen geführt.

## Reproduktionspaket

Das beigefügte ZIP enthält ausschließlich Review-Code, abgeleitete Resultate und Prüfsummeninformation, keine SPARC-Rohdateien oder Rohdatenzeilen.

```bash
python reproduce_g_review.py --repo /pfad/zum/scf-repo --output review_results.json
python reproduce_skip_summary.py --repo /pfad/zum/scf-repo --output skip_counterexample.json
```

Für die zusätzliche reale Nachrechnung:

```bash
python reproduce_g_review.py --repo /pfad/zum/scf-repo \
  --sparc /pfad/zu/lokalen/sparc-dateien --output review_results.json
```

Die Skripte sind Diagnoseprogramme für den geprüften Stand. Sie zeigen beobachtetes Verhalten und ersetzen keine nach einer Korrektur angepassten Regressionstests. Der reale Aufruf prüft beide dokumentierten Hashes und bricht bei abweichenden Dateien ab. Er lädt nichts herunter und verändert keine Repository-Quelldateien. Der Skip-Test benötigt die Möglichkeit, lokal einen temporären symbolischen Link anzulegen.

`review_results.json` enthält insbesondere unabhängige Burkert-Quadraturen, NFW-Grenzwert, Parser- und Statusgegenbeispiele, Auswahl/Ausschlüsse, sämtliche A/B-Pilotwerte, Optimierungsdiagnostik, den einmal erweiterten NFW-Fit und den isolierten Burkert-Korrekturvergleich.

## Quellen und Codeanker

- [Profilcode am Prüfcommit](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/5563e6778359cffdd6e844c8a5cd4eabc7c717dc/src/scoped_correspondence/astrophysics/spherical_profiles.py)
- [Pilotcode am Prüfcommit](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/5563e6778359cffdd6e844c8a5cd4eabc7c717dc/src/scoped_correspondence/validation/galaxy_pilot.py)
- [Adapter am Prüfcommit](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/5563e6778359cffdd6e844c8a5cd4eabc7c717dc/src/scoped_correspondence/validation/sparc_data.py)
- [Roadmap am Prüfcommit](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/5563e6778359cffdd6e844c8a5cd4eabc7c717dc/GALAXY_DYNAMICS_ROADMAP.md)
- [Ursprünglicher Implementierungsplan](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/5563e6778359cffdd6e844c8a5cd4eabc7c717dc/prompts/Answers/nicht_station%C3%A4re_Treiber/SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md)
- [Offizielle SPARC-Metadaten](https://astroweb.case.edu/SPARC/SPARC_Lelli2016c.mrt) und [Komponententabelle](https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt), Abruf dieser Reviewrunde mit oben angegebenen Hashes.
- [Yoon: Verlagsseite](https://www.sciencedirect.com/science/article/pii/S2212686426002499), [DOI](https://doi.org/10.1016/j.dark.2026.102462), [SSRN-Eintrag](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7180683). Kein Volltext in dieser Reviewrunde zugänglich; keine Gleichungsreproduktion behauptet.

Die mathematischen Fehlernachweise und neuen Zahlen dieses Reviews stammen aus den beigefügten eigenen Gegenrechnungen. Sie hängen nicht von einer Interpretation des Yoon-Volltexts ab.
