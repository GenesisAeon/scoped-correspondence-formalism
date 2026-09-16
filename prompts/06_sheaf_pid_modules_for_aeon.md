Auftrag: F08 (Sheaf-Kontextualitäts-Modul) und F09 (PID/Redundancy-Bottleneck-Modul)
für CREP-UTAC-AFET umsetzen, nach deiner eigenen Spec aus
reviews/2026-09-16_gemini_extensions_review_aeon.md, Abschnitte 3 und 4.

Kontext: D:\mandala\crep-utac-afet-formalism\ enthält den CREP-UTAC-AFET-Formalismus
(FORMALISM.md, Revision 3.2, plus die Layer-Dokumente information_layer_crep.md,
system_layer_utac.md, coupling_layer_afet.md, context_transformations.md,
emergence_and_closure.md). Frühere Revisionen (Astra/ChatGPT) haben jeweils ein
verify_*.py-Skript mit reproduzierbarem JSON-Report mitgeliefert — siehe
verification/verify_formalism.py, verify_extensions.py, verify_transformations.py
als Vorbild für Stil und Struktur (reine stdlib + numpy, feste Seeds, druckt
{"count", "passed", "failed", "report"} als JSON, schreibt einen results.json
daneben).

Johann hat die offenen Fragen aus deinem Review (Abschnitt 8) wie folgt entschieden:

1. VB1 (Verträglichkeitsbedingung 1 in context_transformations.md/FORMALISM.md)
   bleibt UNVERÄNDERT für deterministische Bestände. Das Sheaf-Modul ist ein
   SEPARATES, optionales Modul daneben, keine Erweiterung/Ersetzung von VB1.
2. PID-Variante: Williams-Beer (I_min-Atome) ALS BASIS, ergänzt um Kolchinskys
   Redundancy-Bottleneck (arXiv:2405.07665, PMC11276267, Entropy 26(7):546, 2024)
   als moderneren Redundanzbegriff. NICHT Rosas-O-Information als Hauptmetrik.
   Referenzimplementierung zur Orientierung: github.com/artemyk/pid-as-ib.
3. Kanonisches erstes (Quellen,Ziel)-Paar für PID: Mikro→Makro — knüpft an
   worked_example_causal_emergence.md an (das SVD/EI-Gegenbeispiel nutzt schon
   dieses Setup: mikroskopischer Übergangskern → aggregierter Makrozustand).
4. Erstes Sheaf-Toy-Beispiel darf und soll bewusst unphysikalisch sein (PR-Box),
   um die CF-Infrastruktur (LP-Löser etc.) gegen exakt bekannte Werte zu härten,
   bevor sie auf echte GenesisAeon-Fälle angewendet wird.

## Teil A — F08: verify_sheaf_contextuality.py

Primärquellen (bereits verifiziert, bitte exakt so zitieren):
- Abramsky & Brandenburger, "The sheaf-theoretic structure of non-locality and
  contextuality", arXiv:1102.0264, New J. Phys. 13, 113036 (2011),
  DOI 10.1088/1367-2630/13/11/113036
- Abramsky, Barbosa & Mansfield, "The contextual fraction as a measure of
  contextuality", arXiv:1705.07918, Phys. Rev. Lett. 119, 050504 (2017),
  DOI 10.1103/PhysRevLett.119.050504

Kernformeln (aus deinem Review, Abschnitt 3.2 — dort vollständig in LaTeX):
- Ereignisgarbe E(U)=O^U mit Restriktionen s↦s|_U
- Lokale Verträglichkeit der Ränder: e_C|_{C∩C'} = e_C'|_{C∩C'} für alle C,C'
- Globales Schnittstück: Verteilung d auf O^X mit d|_C = e_C für alle C
- Kontextualität ⇔ kein solches globales Schnittstück existiert
- Contextual Fraction über LP: max Σb s.t. Mb ≤ v^e, b≥0 (Inzidenzmatrix M wie
  in Abschnitt 3.2 definiert), NCF(e)=Σb*, CF(e)=1-NCF(e)

Minimal-API (aus deiner Spec, Abschnitt 3.4):
    SheafScenario(X, contexts, outcomes)
    EmpiricalModel.from_tables(scenario, tables)   # prüft Randverträglichkeit
    has_global_section(model) -> bool              # LP/Exact über R≥0
    contextual_fraction(model) -> float            # NCF/CF via LP
    report(model) -> {compatible_margins, NCF, CF, witness_inequality?}

Pflicht-Testfälle (aus deiner Spec, Abschnitt 3.5), Zahlen NUR aus echtem
Skriptlauf, keine erfundenen Werte im Code-Kommentar oder in der Doku:
1. Randverträglichkeit auf einem Toy-(2,2,2)-Szenario (Alice/Bob, 2 Settings,
   binäre Outcomes)
2. Klassisches faktorielles Modell → has_global_section=True, CF≈0
3. PR-Box → CF=1 (starke Kontextualität, Literaturwert)
4. Eine CHSH-artige QM-Tabelle aus der Literatur → 0<CF<1
5. Mapping-Smoke-Test: der VB1-Widerspruchsfall aus context_transformations.md
   §2 (x=y, y=z, z=x+1 gleichzeitig unerfüllbar) als deterministischer
   Drei-Sichten-Fall — zeigt: kein globales Assignment, analog zum Sheaf-Fall
6. Dokumentierte Links auf arXiv:1102.0264 und arXiv:1705.07918 im Skript/Doku

## Teil B — F09: verify_pid_rb.py

Primärquellen:
- Williams & Beer, "Nonnegative Decomposition of Multivariate Information",
  arXiv:1004.2515
- Kolchinsky, "Partial information decomposition: redundancy as information
  bottleneck", arXiv:2405.07665, PMC11276267, Entropy 26(7):546 (2024)
- Referenzimpl.: github.com/artemyk/pid-as-ib

Kernformeln (aus deinem Review, Abschnitt 4.2 — vollständig in LaTeX):
- I(S;R1,R2) = Red(S;{R1}{R2}) + Unq(S;R1) + Unq(S;R2) + Syn(S;{R1,R2})
- I_min(S;{A1,...,Ak}) = Σ_s p(s) min_i I(S=s;A_i)
- Red = Π(S;{1}{2}) = I_min(S;{1}{2}); Unq(R1)=I(S;R1)-Red;
  Syn = I(S;R1,R2)-Unq(R1)-Unq(R2)-Red
- RB-Formulierung (Kolchinsky): I_∩ = max_Q I(Q;Y) s.t. Q⪯_Y X_s ∀s

Minimal-API (aus deiner Spec, Abschnitt 4.4):
    pid_atoms(sources, target, measure="williams_beer") -> {Red, Unq[], Syn, I_joint}
    rb_curve(sources, target, betas|R_grid) -> [(R, I_RB), ...]   # optional Phase 2
    assert_nonnegative_atoms(atoms)
    compare_to_EI_q(channel, q) -> {EI_q, pid_summary}  # nur Dokumentation, KEINE Gleichsetzung

Pflicht-Testfälle (aus deiner Spec, Abschnitt 4.5):
1. UNIQUE-Gate: eine Quelle = Kopie von Y, andere unabhängig → Red≈0, Unq dominant
2. XOR/Synergie-Gate: Einzel-MI≈0, gemeinsame MI>0 → Syn dominant
3. AND-Gate/vollständige Redundanz: Red≈I(Y;X_i)
4. Nichtnegativität aller Atome
5. RB(0) = Blackwell-Redundanz auf kleinem System (gegen Exact-Solver/Referenzwerte)
6. Smoke: EI_q auf demselben Toy berechnen und NEBEN PID berichten, keine
   Behauptung "EI = Syn"

## Abnahmekriterien (Astra-Standard, aus deinem Review Abschnitt 6 — gilt unverändert)

1. Textformeln (LaTeX/Markdown), KEINE Bildformeln
2. verify_*.py mit reproduzierbarem JSON-Report unter verification/
3. Durchgerechnetes Mini-Beispiel mit Zahlen AUS DEM SKRIPTLAUF, Toleranzen
   dokumentiert
4. Explizites Mapping auf bestehende Begriffe (VB1, EI_q) — keine parallele
   Terminologie ohne Brücke
5. Literatur-DOIs/arXiv-IDs wie oben, unverändert
6. KEINE Mutation von FORMALISM.md/REVISION_3_2.md — das entscheidet Johann erst
   nach grünem Verify-Lauf

## Lieferformat

Bitte als ZIP liefern, analog zu den vorherigen Revisions-Paketen (siehe
apply_manifest_revision_3_2.json als Vorbild für das Format): ein
apply_manifest.json mit Pfad, Aktion (add/replace_after_base_check),
SHA-256 der neuen Datei und ggf. bekannter Ausgangs-Prüfsumme, damit Claude
das sicher gegen den aktuellen Stand einspielen kann, ohne etwas zu
überschreiben. Neue Dateien: sheaf_contextuality.md bzw. pid_redundancy_bottleneck.md
(die Dokument-Seite mit Formeln+Mapping), verification/verify_sheaf_contextuality.py,
verification/verify_pid_rb.py, plus die jeweiligen results.json.

Claude reviewed das Ergebnis anschließend (Checksummen, Skript selbst nachrechnen,
Zitate stichprobenartig gegenprüfen) bevor irgendetwas an den Formalismus-Kern geht.
