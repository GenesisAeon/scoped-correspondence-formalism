Wissenschaftlicher DeepResearch-Auftrag: natürliche mathematische
Erweiterungen des Scoped-Correspondence-Formalismus finden

Zielformat: DeepResearch-Modus (ChatGPT/Astra, Gemini oder vergleichbar).
Kein Code-Auftrag, keine Domänenentscheidung — reine Literaturrecherche.

## Ausgangslage

Wir betreiben ein kleines, formal geprüftes Software-Repository
(`scoped-correspondence-formalism`), das aus mehreren unabhängig
voneinander stehenden, mathematisch geprüften Modulen besteht — KEINE
vereinheitlichte Theorie, sondern einzelne, für sich bewiesene/verifizierte
Bausteine, verbunden über einen expliziten Übersetzungsvertrag
(`correspondence`: Konjugation `T∘Φ≈Φ∘T`, Transformationsregeln T1-T4).
Bestehende Bausteine (Stand 17. September 2026):

- `correspondence` — typisierter Übersetzungsvertrag zwischen Modellen.
- `observation` — Kanalkapazität, Retention, deklarierte
  Interventionsinformation `EI_q=I_q(Z_t;Z_{t+1})`.
- `dynamics` — kubische Normalform mit bewiesener
  Bistabilitätsbedingung `4a³>27b²`, Sigmoid-Antwort, Erholungsraten.
- `coupling` — paarweise Kopplung, GENERIC-Strukturtest
  (`J^T=-J`, `M^T=M≥0`, `J∇S=0`, `M∇E=0`) als reiner Strukturcheck.
- `closure` — exakte Makro-Geschlossenheit `PC=CQ`, TV-Fehlerschranke,
  Kreisrekonstruktion, Projektions-Gedächtnis (kleines 2D-Beispiel).
- `viability` — bewiesener Satz zur sicheren Eingriffsübertragung
  (Ausführbarkeit, Nachfolgerverträglichkeit, sichere Darstellung),
  gekoppelter Budget-Konfliktfall.
- `membership` — binäre Zugehörigkeitsmatrix `M_eα`, gemeinsame
  Eingriffsmenge `U_joint=U_physical∩⋂_α U_α`.
- `identifiability` — Konditionierung, Parameter-Nichtidentifizierbarkeit,
  SVD-vs-EI-Entkopplung, Data-Processing-Inequality.
- `validation` — erster echter Datenpilot (VLBI-Zeitreihe, Kalibrierung/
  Holdout-Split, Baseline-Vergleich).
- `contextuality` — Abramsky-Brandenburger empirische Modelle +
  Contextual Fraction (Abramsky-Barbosa-Mansfield).
- `information_decomposition` — Williams-Beer `I_min`-PID +
  Kolchinsky-Blackwell-Redundancy-Bottleneck, TWO_BIT_COPY-Gegenfall.
- `thermo` — GENERIC-Wärmebeispiel, Drei-Zyklus-Gegenfall (stochastische
  Invertierbarkeit ≠ Detailed Balance ≠ thermodynamische Reversibilität),
  algebraische Projektionsprüfung für GENERIC-Struktur.

## Bereits geprüft und bewusst zurückgestellt (NICHT erneut vorschlagen,
## außer es gibt eine neue, entscheidende Quelle dazu)

- Structured Cospans (Baez-Courser, arXiv:1911.04630) — zurückgestellt,
  kein akuter Verify-Gap.
- Liu-Slotine-Barabási-Netzwerksteuerbarkeit (Nature 473, 167-173, 2011)
  — zurückgestellt, Skalen-Mismatch (unsere Beispiele sind 2-3D).
- N-Quellen-Verallgemeinerung von PID (über Williams-Beer/Blackwell
  hinaus) — als größeres, offenes Forschungsfeld erkannt.
- Gewichtete/kontinuierliche Zugehörigkeit (`M_eα∈[0,1]`) — zurückgestellt,
  fehlende Bedeutung der Gewichte.
- Metaregeln `m'=H(m,z,c,u,t)` — in `context_transformations.md` §6
  spezifiziert, noch nicht implementiert.
- Vollständiger Mori-Zwanzig-Projektionsformalismus — bisher nur ein
  kleines 2D-Spielzeugbeispiel in `closure`.
- RG-Universalität für die kubische Normalform — als eigenständige,
  größere Behauptung erkannt, keine Voraussetzung des Ausgangsprojekts.
- Epsilon-Machine-/Causal-States-Rekonstruktion (Crutchfield) — bisher
  nur winzige, exakt durchgerechnete endliche Fälle.

## Rechercheauftrag

Finde **weitere, bisher nicht in Betracht gezogene** mathematische
Theorien, Sätze oder Formalismen aus der etablierten Literatur, die sich
NATÜRLICH an einen oder mehrere der oben genannten Bausteine anschließen
ließen — also eine echte, zitierfähige Erweiterung eines bestehenden,
bereits bewiesenen/verifizierten Bausteins, kein neuer eigenständiger
Ast und keine Vereinheitlichung mehrerer Bausteine zu einer Größe.

### Harte Ausschlusskriterien (Grund: dokumentierte Vorgeschichte)

Dieses Projekt hat mehrfach falsche Cross-Layer-Identitäten korrigieren
müssen (u.a. β≡Stabilität, V≡Panarchy≡Onsager-L, geteiltes σ=2,2 als
"Universalität", A_ij≡L_ij). Deshalb gilt zwingend:

1. **Keine Vorschläge, die zwei oder mehr der obigen Bausteine
   gleichsetzen oder unter einem gemeinsamen Parameter/einer
   gemeinsamen Konstante vereinen.** Jeder Vorschlag bezieht sich auf
   GENAU EINEN bestehenden Baustein und erweitert ihn in sich.
2. Keine "Universalitäts"- oder "Meta-Theorie"-Behauptungen.
3. Jede Quelle muss ein echtes, prüfbares arXiv/DOI-Zitat haben —
   keine Sekundärquellen, keine Blogposts, keine KI-generierten
   Zusammenfassungen ohne Primärquelle.
4. Bevorzugt: Theorien mit einem kleinen, von Hand durchrechenbaren
   Beispiel (analog zu unseren bisherigen `verify_*.py`-Skripten) —
   keine reinen Existenzsätze ohne konstruktives Beispiel.

### Gewünschtes Ausgabeformat pro Vorschlag

1. Name der Theorie/des Satzes + Primärquelle (Autor, Jahr, arXiv/DOI).
2. Kernformel in Text/LaTeX (keine Bildformeln).
3. An welchen bestehenden Baustein (siehe Liste oben) schließt es sich
   an, und warum — konkrete Formel-zu-Formel-Anknüpfung, kein
   thematisches "passt ungefähr".
4. Ein durchgerechnetes Mini-Beispiel mit konkreten Zahlen (falls in
   der Quelle vorhanden) oder ein klarer Hinweis, dass eines
   konstruiert werden müsste.
5. Geschätzter Umfang (klein/mittel/groß) für eine spätere
   Implementierung nach unserem "Astra-Standard" (Textformeln,
   `verify_*.py` mit reproduzierbarem JSON-Report, durchgerechnetes
   Beispiel aus dem Skriptlauf, explizites Mapping, geprüfte Zitate).

Liefere mindestens 5, höchstens 10 Vorschläge, sortiert nach
Bausteinen (nicht nach vermuteter Priorität — die Bewertung, was davon
umgesetzt wird, trifft Johann separat). Wenn zu einem Baustein nichts
Neues und Zitierfähiges gefunden wird, das ehrlich vermerken statt
einen schwachen Vorschlag zu erzwingen.
