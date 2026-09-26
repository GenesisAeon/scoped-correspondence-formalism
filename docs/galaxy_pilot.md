# SPARC-Pilot: eingefrorene Auswahl, deskriptiver Fit, gehaltener Test (G5)

Antwort auf `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` §10. Module:
[`validation/sparc_data.py`](../src/scoped_correspondence/validation/sparc_data.py),
[`validation/galaxy_pilot.py`](../src/scoped_correspondence/validation/galaxy_pilot.py).
Verifikation (synthetisch, kein Netzwerk/reale Daten nötig):
[`verify_galaxy_pilot.py`](../verification/verify_galaxy_pilot.py) (7/7).

**Dies ist der ECHTE, einmalig in dieser Sitzung reproduzierte Pilotlauf**
gegen die realen, lokal (außerhalb des Repos) gespeicherten SPARC-Dateien
— siehe `docs/sparc_data_provenance.md`. Analog zum etablierten
`docs/hydrology_pilot.md`-Muster bleibt `verify_galaxy_pilot.py` rein
synthetisch für CI; dieses Dokument ist der Nachweis, dass der Pilot
tatsächlich mit echten Daten gelaufen ist. Rohdaten-Abhängigkeit:
`D:\mandala\scf_external_data\sparc\` (Lizenzstatus ungeklärt, siehe
`docs/sparc_data_provenance.md`) — dieser Lauf ist deshalb nicht Teil der
Standard-CI und muss bei Bedarf manuell wiederholt werden.

## 1. Eingefrorene Auswahl (§10.1)

Von 175 SPARC-Galaxien insgesamt erfüllen **94** die Eignungskriterien
(Q ∈ {1,2}, D>0, SBeff>0, Inklination 30–80°, ≥10 Radialpunkte). 81
Galaxien ausgeschlossen: 36 mit weniger als 10 Radialpunkten, 33 wegen
Inklination außerhalb [30°,80°], 12 wegen Qualitätsflag ∉ {1,2} (nach dem
jeweils ersten zutreffenden Ausschlussgrund gezählt, Mehrfachgründe pro
Galaxie möglich).

Sortierung nach `log10(SBeff)` dann ID, Aufteilung in drei möglichst
gleich große zusammenhängende Drittel (94 = 32+31+31, Überhang in die
früheren Drittel gelegt — eine dokumentierte, deterministische Konvention,
da der Plan die Verteilung eines nicht durch 3 teilbaren Rests nicht
festlegt). Innerhalb jedes Drittels Ranking nach
`sha256("SCF-GALAXY-v1|<ID>")`, die ersten vier gewählt, davon die ersten
zwei Entwicklung und die folgenden zwei Evaluation:

| Drittel | n geeignet | Gewählt (Rang 1–4 nach Hash) | Entwicklung | Evaluation |
|---|---:|---|---|---|
| unteres (niedrigstes SBeff) | 32 | DDO168, F583-4, NGC3109, F568-V1 | DDO168, F583-4 | NGC3109, F568-V1 |
| mittleres | 31 | NGC0024, NGC3917, NGC1003, NGC3726 | NGC0024, NGC3917 | NGC1003, NGC3726 |
| oberes (höchstes SBeff) | 31 | NGC3893, NGC3521, UGC02487, NGC6674 | NGC3893, NGC3521 | UGC02487, NGC6674 |

**Entwicklung (6):** DDO168, F583-4, NGC0024, NGC3917, NGC3893, NGC3521.
**Evaluation (6):** NGC3109, F568-V1, NGC1003, NGC3726, UGC02487, NGC6674.

Kein Drittel unterschritt die Mindestanzahl von vier geeigneten Objekten
— keine Protokollabweichung nötig.

## 2. Modus A — deskriptiver Burkert-Fit, volle Kurve (§10.2)

Alle 12 ausgewählten Galaxien, `Upsilon_d=0,5`, `Upsilon_b=0,7`, feste
Rechengrenzen `log10(rho0/[Msun/pc^3]) ∈ [-4,1]`,
`log10(r0/kpc) ∈ [-2, 2,5]`:

| Galaxie | Satz | n Punkte | `rho0` [Msun/pc³] | `r0` [pc] | `mu_h` [Msun/pc²] | Status | Randtreffer | RMSE [km/s] |
|---|---|---:|---:|---:|---:|---|---|---:|
| DDO168 | dev | 10 | 0,0267 | 3828 | 102,1 | konvergiert | nein | 3,23 |
| F583-4 | dev | 12 | 0,0448 | 2494 | 111,7 | konvergiert | nein | 3,01 |
| NGC0024 | dev | 29 | 0,3850 | 1547 | 595,7 | konvergiert | nein | 4,12 |
| NGC3917 | dev | 17 | 0,0498 | 4782 | 238,1 | konvergiert | nein | 4,03 |
| NGC3893 | dev | 10 | 0,0694 | 5128 | 356,0 | konvergiert | nein | 4,04 |
| NGC3521 | dev | 41 | 0,0719 | 5666 | 407,1 | konvergiert | nein | 7,93 |
| NGC3109 | eval | 25 | 0,0213 | 4650 | 99,1 | konvergiert | nein | 0,93 |
| F568-V1 | eval | 15 | 0,1141 | 2993 | 341,6 | konvergiert | nein | 3,01 |
| NGC1003 | eval | 36 | 0,0104 | 9336 | 96,9 | konvergiert | nein | 5,37 |
| NGC3726 | eval | 12 | 0,0092 | 12760 | 117,3 | konvergiert | nein | 9,03 |
| UGC02487 | eval | 17 | 0,1148 | 8683 | 996,9 | konvergiert | nein | 12,84 |
| NGC6674 | eval | 15 | 0,0333 | 10956 | 364,9 | konvergiert | nein | 23,26 |

Alle 12 Fits konvergieren, keiner trifft eine Rechengrenze. `mu_h` streut
über fast eine Größenordnung (97–997 Msun/pc²) — auf dieser Stichprobe
**keine auffällige Konstanz**, im Gegensatz zur Donato/Yoon-Halo-Konstante
aus G0 (dort ~141 bzw. ~174 Msun/pc², aus ganz anderen, größeren
Populationen und Fit-Methoden abgeleitet). Dies ist eine deskriptive
Beobachtung auf 12 Galaxien, **keine Widerlegung** jener Populationsbefunde
— dafür wäre eine der dortigen Methodik entsprechende Stichprobe und
Fit-Prozedur nötig, die dieser Pilot nicht repliziert.

## 3. Modus B — gehaltener Außenradien-Test, nur Evaluationsgalaxien (§10.3–10.4)

70/30-Aufteilung nach aufsteigendem Radius (≥7 Training-, ≥3 Testpunkte);
Baseline A (Burkert) und B (NFW) auf Trainingsradien gefittet, alle drei
Baselines (A, B, C=MOND) auf den gehaltenen Außenradien ausgewertet:

| Galaxie | n Test | Baseline | MAE [km/s] | RMSE [km/s] |
|---|---:|---|---:|---:|
| NGC3109 | 8 | A (Burkert) | **0,64** | **0,85** |
| NGC3109 | 8 | B (NFW) | 11,24 | 11,27 |
| NGC3109 | 8 | C (MOND) | 9,23 | 9,26 |
| F568-V1 | 5 | A (Burkert) | **5,64** | **5,91** |
| F568-V1 | 5 | B (NFW) | 19,48 | 20,25 |
| F568-V1 | 5 | C (MOND) | 21,53 | 22,46 |
| NGC1003 | 11 | A (Burkert) | 15,22 | 15,48 |
| NGC1003 | 11 | B (NFW) | 7,67 | 7,84 |
| NGC1003 | 11 | C (MOND) | **4,37** | **4,76** |
| NGC3726 | 4 | A (Burkert) | 30,93 | 32,36 |
| NGC3726 | 4 | B (NFW) | 22,05 | 23,13 |
| NGC3726 | 4 | C (MOND) | **4,35** | **7,20** |
| UGC02487 | 6 | A (Burkert) | 11,41 | 14,57 |
| UGC02487 | 6 | B (NFW) | **8,25** | **9,70** |
| UGC02487 | 6 | C (MOND) | 62,10 | 62,14 |
| NGC6674 | 5 | A (Burkert) | 29,66 | 31,08 |
| NGC6674 | 5 | B (NFW) | 26,12 | 27,50 |
| NGC6674 | 5 | C (MOND) | **19,11** | **19,30** |

**Ehrliches Ergebnis: kein Baseline gewinnt einheitlich.** Burkert gewinnt
bei 2 von 6 Galaxien (NGC3109 klar, F568-V1 klar), MOND bei 3 von 6
(NGC1003, NGC3726, NGC6674), NFW bei 1 von 6 (UGC02487). Auffällig: bei
UGC02487 versagt das MOND-Modell sehr deutlich (RMSE 62 km/s) — dieselbe
Galaxie hatte in Modus A auch das mit Abstand höchste `mu_h` (997
Msun/pc²), ein Hinweis, dass hier baryonische oder Entfernungsannahmen
(feste `Upsilon_d/b`) für alle drei Modelle ungünstig sein könnten, nicht
spezifisch für ein Modell. Sechs Evaluationsgalaxien erlauben laut Plan
§10.4 höchstens eine vorsichtige Pilotbeschreibung — **keine
Siegerbehauptung, keine Entscheidung über dunkle Materie versus MOND.**

## 4. Synthetische Pflichtkontrollen (§10.5)

Alle sieben in `verify_galaxy_pilot.py` (7/7 grün):

- Exakte rauschfreie Rückgewinnung auf einer weitreichenden synthetischen
  Burkert-Kurve (`rho0`/`r0` bis auf `~1e-15` relative Abweichung).
- Informationsverlust bei reiner Innenkurve: bei realistischem Rauschen
  (`sigma=2` km/s, 5 unabhängige Rauschzüge) bleibt der `r0`-Fehler bei
  weitreichender Abdeckung bei 2–6 %, bei reiner Innenkurve dagegen bei
  72–96 % — durchgängig >10-fach schlechter, wie vom Plan erwartet
  (reine Rauschfreiheit allein hätte das NICHT gezeigt, da ein perfekter
  Optimierer auch schwach konditionierte Probleme exakt löst — das
  eigentliche Identifizierbarkeitsproblem zeigt sich erst unter Rauschen).
- Vorzeichenkonvention: `v_gas=-10, v_disk=40 → v_bar²=700`, nicht 900.
- Entfernungsskalierung entspricht exakt der G2-Homologie-Vorhersage
  (`rho0/lambda`, `r0*lambda` bei `lambda=2,5`) — verbindet G2, G4 und G5.
- Lecktest: Verfälschung der gehaltenen Testwerte ändert weder
  Trainingsdaten noch gefittete Parameter (bit-identisch).
- Beobachtungsäquivalenz `g→v_c` erneut bestätigt (aus G3 wiederverwendet).
- Randtreffer wird korrekt gemeldet, wenn der wahre Wert weit außerhalb
  der deklarierten Rechengrenzen liegt (nicht stillschweigend akzeptiert).

## 5. Einordnung (§10.6 / §13.1)

| Befund | Zulässige Aussage | Nicht belegt |
|---|---|---|
| Alle 12 Burkert-Fits konvergieren, keine Randtreffer | Der deskriptive Fit ist auf dieser Stichprobe numerisch gutartig | Universelle Anwendbarkeit auf beliebige SPARC-Galaxien |
| `mu_h` streut über fast eine Größenordnung | Bedingter Befund unter Profil-, Auswahl- und Fehlerannahmen dieses Piloten | Widerlegung der Donato/Yoon-Populationskonstante |
| Kein Baseline gewinnt einheitlich im Außenradientest | Bessere bedingte Testleistung variiert pro Galaxie auf dieser Stichprobe | Endgültige Entscheidung über Dunkle Materie vs. MOND |
| UGC02487: MOND-Ausreißer | Auffälliger Einzelfall, wert näher untersucht zu werden | Systematisches MOND-Versagen |

Dieser Pilot ist bewusst klein (12 Galaxien, Arbeitsbegrenzung laut Plan
§10.1) und liefert **explorative, keine konfirmatorischen** Aussagen.
