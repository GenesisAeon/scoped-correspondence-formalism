# Review: Gemini-Erweiterungsvorschläge zu CREP–UTAC–AFET Revision 3.2

**Datum:** 2026-09-16 (Europe/Berlin)  
**Adressat:** Johann Römer  
**Status:** Review only — keine Mutation von `FORMALISM.md` / `REVISION_3_2.md`  
**Triage-Grundlage:** Claude-Urteil zur Gemini-Export-Datei (Formeln als Bilder) + Abgleich mit lokalem Revisionsstand 3.2 + Primärquellen

---

## TL;DR Empfehlung

| Vorschlag | Empfehlung | Begründung in einem Satz |
|---|---|---|
| **A. Sheaf-theoretische Kontextualität** (Abramsky–Brandenburger + Contextual Fraction) | **Jetzt ernsthaft vorbereiten / als Modul spezifizieren** | Behebt die Fehlbehandlung widersprüchlicher Multi-System-Überlappungen als „bloßer Modellierfehler“ und liefert eine prüfbare Quantitative (CF). |
| **B. PID + Redundancy Bottleneck** | **Natürlicher nächster Schritt** (nach oder parallel zu A-Minimal-API) | Ersetzt den skalaren `EI_q`-Engpass durch Atome Red/Unq/Syn; Rosas ist in `LITERATURE_CONNECTIONS.md` genannt, aber **nicht operationalisiert**. |
| **C. Structured Cospans** (Baez) | **Zurückstellen** | `context_transformations.md` ist bereits informell kompositional; Cospans wären premature Formalisierung ohne Verify-Skript und ohne skalare Lücke. |
| **D. Liu–Slotine–Barabási Controllability** | **Zurückstellen** (Anhang möglich) | Skalenmismatch: Toy-Systeme 2–3D vs. Netzwerk-Controllability; UTAC-Steuerung hat andere Prüffragen. |

**Astra-Standard (Aufnahmebedingung):** Textformeln (kein Bild), `verify_*.py`, durchgerechnetes Mini-Beispiel mit Zahlen **aus dem Skriptlauf** — nicht aus dem Review. Gemini-Export erfüllt das derzeit **nicht**.

---

## 1. Diagnose der Gemini-Datei

1. **Formeln als Bilder:** Nicht diffbar, nicht zitierfähig, nicht in Verify-Skripten nutzbar. Rekonstruktion muss aus Primärliteratur erfolgen (unten).
2. **Keine `verify_*.py` / keine durchgerechneten Zahlen:** Unter Astra-Standard **nicht adoptionsfähig**.
3. **Inhaltlich starke Treffer bei A und B:** Claude-Triage deckt sich mit dem lokalen Gap (Verträglichkeit = Konsistenzforderung; `EI_q` = Skalar ohne Zerlegung).
4. **C und D** sind literaturseitig korrekt referenzierbar, aber **nicht** die kritische Lücke von Revision 3.2.

---

## 2. Abgleich mit Revision 3.2 lokal — was wirklich klafft

### 2.1 Verträglichkeitsbedingung 1 (Gemeinsame Größen)

Aus `FORMALISM.md` (Verträglichkeitsbedingungen):

> 1. **Gemeinsame Größen:** Sichten auf denselben physischen Bestand müssen nach Rücktransformation übereinstimmen. Relationale Größen wie Reserve oder Anteil dürfen verschieden sein. Überlappende Zugehörigkeiten verdoppeln keinen Bestand.

Aus `context_transformations.md` §2:

> Wenn zwei Sichten dieselbe Größe enthalten, werden Rückabbildungen auf diese gemeinsame Größe angegeben:
>
> \[ R_{\alpha e}(y_\alpha,c,t) = R_{\beta e}(y_\beta,c,t) = x_e. \]
>
> Aus beliebig gewählten lokalen Beschreibungen folgt nicht automatisch ein gemeinsamer Zustand. Die Menge verträglicher Kombinationen ist als Teilmenge ihres Produktraums zu prüfen. Beispielsweise lassen sich die drei Forderungen \(x=y\), \(y=z\) und \(z=x+1\) nicht gleichzeitig erfüllen. Eine widersprüchliche Kombination wird nicht durch eine zusätzliche Ebene aufgelöst; mindestens eine Annahme oder die Interpretation der Variablen muss sich ändern.

**Gap:** Widerspruch wird als **Inkonsistenz der Annahmen** behandelt. Die Sheaf-Lesart sagt: lokale Verteilungen/Abschnitte können **marginal-konsistent** (no-signalling / Verträglichkeit der Ränder) sein und dennoch **kein globales Schnittstück** besitzen — das ist **Kontextualität**, kein bloßer Modellierfehler. Contextual Fraction misst den Anteil, der sich nicht nicht-kontextuell erklären lässt.

### 2.2 `EI_q` als Skalar

Aus `FORMALISM.md`:

> Für einen deklarierten Interventionskanal wird `EI_q(P)=I_q(Z_t;Z_(t+1))` verwendet.

Aus `information_layer_crep.md` / Literatur:

> Für kollektive Prognosebeiträge kann eine begründete Informationszerlegung verwendet werden. […] Ein Überschuss der gemeinsamen MI gegenüber der Summe einzelner MI ist nicht allgemein bereits eine eindeutig bestimmte PID-Synergie.

Aus `LITERATURE_CONNECTIONS.md`:

> Rosas et al. operationalisieren Emergenz über Informationszerlegung und kollektive Vorhersagebeiträge. […] **Übernahme:** EI, spektrale Redundanz und Synergie erhalten getrennte Metrikkennungen.

**Gap:** PID/RB ist **benannt**, aber **nie als API + Verify** operationalisiert. Der Skalar `EI_q` kann Redundanz und Synergie nicht trennen.

### 2.3 Was Revision 3.2 bereits hat (kein Gap)

- Kontexttransformationen T1/T2, Komposition/Zerlegung, Metaregeln (`context_transformations.md`).
- `verification/verify_transformations.py` (18 Prüfgruppen) — Astra-Vorbild für neue Module.
- Explizite Ablehnung, widersprüchliche lokale Daten „wegzuheben“.

---

## 3. Vorschlag A: Sheaf-Modul (TAKE SERIOUSLY)

### 3.1 Primärquellen (verifiziert)

| Werk | Identifikatoren |
|---|---|
| Abramsky & Brandenburger, *The sheaf-theoretic structure of non-locality and contextuality* | arXiv:1102.0264; New J. Phys. 13 113036 (2011); DOI [10.1088/1367-2630/13/11/113036](https://doi.org/10.1088/1367-2630/13/11/113036) |
| Abramsky, Barbosa & Mansfield, *The contextual fraction as a measure of contextuality* | arXiv:1705.07918; Phys. Rev. Lett. 119, 050504 (2017); DOI [10.1103/PhysRevLett.119.050504](https://doi.org/10.1103/PhysRevLett.119.050504) |

### 3.2 Kernformeln (Standardformen, Text/LaTeX)

**Messszenario:** \(\langle X,\mathcal{M},O\rangle\) — Messungen \(X\), Kontexte \(\mathcal{M}\) (Anti-Kette maximaler kompatibler Mengen), Outcomes \(O\).

**Ereignisgarbe:** Für \(U\subseteq X\) ist \(\mathcal{E}(U)=O^U\) (Abschnitte = Outcome-Zuweisungen). Restriktionen \(s\mapsto s|_U\).

**Empirisches Modell (lokale Familien):** Für jedes \(C\in\mathcal{M}\) eine Verteilung \(e_C\) auf \(O^C\), mit **lokaler Verträglichkeit der Ränder** (verallgemeinertes No-Signalling):

\[
\forall C,C'\in\mathcal{M}:\quad
e_C\big|_{C\cap C'} = e_{C'}\big|_{C\cap C'}.
\]

**Globales Schnittstück:** Existenz einer Verteilung \(d\) auf \(O^X\) mit \(d|_C = e_C\) für alle \(C\).  
**Kontextualität** \(\Leftrightarrow\) **kein solches globales Schnittstück** (Abramsky–Brandenburger).

**Incidence-Matrix / LP-Test (nicht-kontextuell):** Mit globalen Assignments \(g\in O^X\) und lokalen \((C,s)\):

\[
\mathbf{M}[\langle C,s\rangle, g]
=
\begin{cases}
1 & \text{falls } g|_C = s,\\
0 & \text{sonst.}
\end{cases}
\]

Nicht-Kontextualität: \(\exists\,\mathbf{d}\ge\mathbf{0}\) mit \(\mathbf{M}\,\mathbf{d}=\mathbf{v}^e\) und \(\mathbf{1}\cdot\mathbf{d}=1\).

**Contextual Fraction / Non-contextual Fraction** (Abramsky–Barbosa–Mansfield):

\[
e = \lambda\, e^{\mathrm{NC}} + (1-\lambda)\, e',\qquad
\mathsf{NCF}(e)=\max\lambda,\qquad
\mathsf{CF}(e)=1-\mathsf{NCF}(e).
\]

LP-Form (maximale Gewichtung einer globalen Subverteilung \(\mathbf{b}\)):

\[
\max_{\mathbf{b}}\;\mathbf{1}\cdot\mathbf{b}
\quad\text{s.t.}\quad
\mathbf{M}\,\mathbf{b}\le\mathbf{v}^e,\quad \mathbf{b}\ge\mathbf{0}.
\]

Dann \(\mathsf{NCF}(e)=\mathbf{1}\cdot\mathbf{b}^\*\), \(\mathsf{CF}(e)=1-\mathsf{NCF}(e)\).  
Werte in \([0,1]\); \(\mathsf{CF}=1\) \(\Leftrightarrow\) starke Kontextualität (kein globales Assignment im Support).

### 3.3 Mapping auf Verträglichkeitsbedingung 1

| Lokal (Revision 3.2) | Sheaf-Modul |
|---|---|
| Rückabbildungen \(R_{\alpha e}=R_{\beta e}=x_e\) | Restriktion/Gleiten auf gemeinsame Messung \(e\) |
| „Menge verträglicher Kombinationen ⊂ Produktraum“ | Compatible family \(\{e_C\}\) bzw. Abschnitte |
| Widerspruch \(x=y\), \(y=z\), \(z=x+1\) | Leerer Raum globaler Abschnitte (deterministisch) |
| **Fehlende Stufe** | Marginal-konsistent, aber \(\nexists\) globales \(d\) → **CF > 0** als Befund, nicht als „Bug“ |

**Empfehlung an Johann:** Verträglichkeitsbedingung 1 bleibt für **deterministische Bestände**. Zusätzlich ein optionaler Modus für **stochastische/kontextuelle Überlappungen**: lokale Familien + CF-Bericht.

### 3.4 Minimal-API (Vorschlag, noch nicht implementiert)

```text
SheafScenario(X, contexts, outcomes)
EmpiricalModel.from_tables(scenario, tables)   # prüft Randverträglichkeit
has_global_section(model) -> bool              # LP / Exact über ℝ≥0
contextual_fraction(model) -> float            # NCF/CF via LP
report(model) -> {compatible_margins, NCF, CF, witness_inequality?}
```

### 3.5 Verify-Skript-Spezifikation: `verify_sheaf_contextuality.py`

**Muss berechnen / prüfen (Akzeptanzkriterien):**

1. **Randverträglichkeit** auf einem Toy-(2,2,2)-Szenario (Alice/Bob, zwei Settings, binäre Outcomes).
2. **Globales Schnittstück existiert** für ein klassisches (faktorielles) Modell → `has_global_section=True`, `CF≈0` (Toleranz dokumentieren).
3. **PR-Box / stark kontextuelles Support-Modell** → `CF=1` (Literatur: starke Kontextualität ⇔ CF=1).
4. **Bell/CHSH-artige Tabelle** (aus Literatur, z. B. Werte wie in Abramsky–Brandenburger / PRL-CF-Paper) → `0 < CF < 1`; **keine erfundenen Zahlen im Review** — Zahlen stehen erst nach Skriptlauf in `verification/sheaf_results.json`.
5. **Mapping-Smoke-Test:** Ein Mini-Fall „drei Sichten, gemeinsames \(x_e\)“ als deterministische Abschnitte → leeres/nichtleeres globales Assignment analog zum \(x=y,y=z,z=x+1\)-Beispiel aus `context_transformations.md`.
6. Dok-Links: Referenzen auf arXiv:1102.0264 und arXiv:1705.07918 vorhanden.

**Toy-Beispiel-Plan (auszufüllen durch Skriptlauf):**

| Fall | Erwartung | Ergebnis |
|---|---|---|
| Faktorielles klassisches Modell | CF = 0 | *to be filled by running script* |
| PR-Box | CF = 1 | *to be filled by running script* |
| CHSH-artige QM-Tabelle | CF ∈ (0,1) | *to be filled by running script* |
| Deterministischer VB1-Widerspruch | kein globales Assignment | *to be filled by running script* |

---

## 4. Vorschlag B: PID / Redundancy-Bottleneck-Modul (NATURAL NEXT STEP)

### 4.1 Primärquellen (verifiziert; Zitationen getrennt halten)

| Rolle | Werk | Identifikatoren |
|---|---|---|
| Klassische PID-Atome | Williams & Beer, *Nonnegative Decomposition of Multivariate Information* | arXiv:1004.2515 |
| Emergenz / Zerlegung (bereits im Repo genannt) | Rosas et al., *PLOS Comput Biol* 2020 | DOI [10.1371/journal.pcbi.1008289](https://doi.org/10.1371/journal.pcbi.1008289) |
| O-Information (Rosas et al.) | *Quantifying high-order interdependencies…* | arXiv:1902.11239; Phys. Rev. E 100, 032305 (2019) |
| Redundancy Bottleneck (IB-Formulierung der Redundanz) | Kolchinsky, *Partial information decomposition: redundancy as information bottleneck* | arXiv:2405.07665; Entropy 26(7):546 (2024); **PMC: PMC11276267** |

**Hinweis zur Gemini-/Prompt-Zitation:** „Rosas / PMC11276267“ vermengt zwei Stränge. **PMC11276267 = Kolchinsky (RB)**; Rosas ist separat (PLOS 2020 / O-Info 2019). Im Modul klar trennen.

### 4.2 Kernformeln (Standardformen)

**Zwei Quellen \(R_1,R_2\), Ziel \(S\)** (Williams–Beer-Struktur):

\[
I(S;R_1,R_2)
=
\operatorname{Red}(S;\{R_1\}\{R_2\})
+ \operatorname{Unq}(S;R_1)
+ \operatorname{Unq}(S;R_2)
+ \operatorname{Syn}(S;\{R_1 R_2\}).
\]

Mit \(I_{\min}\) (Redundanz als erwartetes Minimum spezifischer Information):

\[
I_{\min}(S;\{\mathbf{A}_1,\ldots,\mathbf{A}_k\})
=
\sum_s p(s)\,\min_i I(S=s;\mathbf{A}_i).
\]

Partial-Information-Atome via Möbius-Inversion auf dem Redundanzgitter:

\[
\Pi_{\mathbf{R}}(S;\alpha)
=
I_{\min}(S;\alpha)
-
\sum_{\beta\prec\alpha}\Pi_{\mathbf{R}}(S;\beta).
\]

Für zwei Quellen insbesondere:

\[
\begin{aligned}
\operatorname{Red} &= \Pi(S;\{1\}\{2\}) = I_{\min}(S;\{1\}\{2\}),\\
\operatorname{Unq}(R_1) &= I(S;R_1)-\operatorname{Red},\\
\operatorname{Syn} &= I(S;R_1,R_2)-\operatorname{Unq}(R_1)-\operatorname{Unq}(R_2)-\operatorname{Red}.
\end{aligned}
\]

**Blackwell-Redundanz / RB** (Kolchinsky): maximale Information in \(Q\), die über jede Quelle hinaus nicht mehr über \(Y\) informiert als die Quelle selbst (Blackwell-Ordnung); RB-Relaxation:

\[
I_{\cap}
=
\max_Q I(Q;Y)
\quad\text{s.t.}\quad
Q\preceq_Y X_s\ \forall s,
\]

\[
I_{\mathrm{RB}}(R)
=
\max_{Q:\,Q-(Z,S)-Y}
I(Q;Y|S)
\quad\text{s.t.}\quad
I(Q;S|Y)\le R,
\]

mit \(I_{\mathrm{RB}}(0)=I_{\cap}\). Referenzimplementierung: [github.com/artemyk/pid-as-ib](https://github.com/artemyk/pid-as-ib).

**TODO (falls Gemini andere PID-Variante zeigte):** Exact-Atom-Definitionen anderer Schulen (BROJA, etc.) nur nach expliziter Quellenwahl — hier Williams–Beer + Kolchinsky-RB als Default-Kandidaten.

### 4.3 Mapping auf `EI_q`-Schwäche

| Status quo | PID/RB-Modul |
|---|---|
| `EI_q(P)=I_q(Z_t;Z_{t+1})` ein Skalar | Zerlegung der gemeinsamen Info in Red/Unq/Syn (oder RB-Kurve) |
| „Synergie“ nur verbal / MI-Überschuss unsicher | Syn-Atom bzw. RB-Prediction vs. Compression getrennt |
| Rosas in Literatur, nicht operational | API + `verify_pid_rb.py` |

`EI_q` bleibt als **Kanal-EI**; PID/RB wird **zusätzliche Zerlegung** unter deklarierten Quellen und Ziel (z. B. Mikrovariablen → Makroziel, oder mehrere Teilsysteme → gemeinsame Aufgabe).

### 4.4 Minimal-API

```text
pid_atoms(sources, target, measure="williams_beer") -> {Red, Unq[], Syn, I_joint}
rb_curve(sources, target, betas|R_grid) -> [(R, I_RB), ...]   # optional Phase 2
assert_nonnegative_atoms(atoms)
compare_to_EI_q(channel, q) -> {EI_q, pid_summary}  # Dokumentation, keine Gleichsetzung
```

### 4.5 Verify-Skript-Spezifikation: `verify_pid_rb.py`

1. **UNIQUE-Gate** (Literaturbeispiel Kolchinsky/Williams): eine Quelle Kopie von \(Y\), andere unabhängig → Red≈0, Unq dominant — *Zahlen to be filled by running script*.
2. **XOR/Synergie-Gate:** Einzel-MI ≈ 0, gemeinsame MI > 0 → Syn dominant.
3. **AND-Gate / vollständige Redundanz-Fall:** Red ≈ \(I(Y;X_i)\) (soweit Measure das verlangt).
4. **Nichtnegativität** aller Atome (Williams–Beer \(\Pi\)).
5. **RB(0) = Blackwell-Redundanz** auf einem kleinen System (gegen Exact-Solver oder Referenzwerte aus Paper/Repo — keine erfundenen Floats hier).
6. Smoke: `EI_q` auf demselben Toy berechnen und **neben** PID berichten (keine Behauptung „EI = Syn“).

---

## 5. Zurückgestellt: Structured Cospans + Controllability

### 5.1 Structured Cospans — DEFER

- Baez & Courser, *Structured Cospans*, arXiv:1911.04630; TAC 35 (2020) 1771–1822; DOI [10.70930/tac/dca3obx4](https://doi.org/10.70930/tac/dca3obx4).
- Form: \(L(a)\to x\leftarrow L(b)\) für offene Netzwerke.
- **Warum defer:** `context_transformations.md` beschreibt Komposition/Zerlegung bereits informell; kein Verify-Gap der Größe von VB1/EI_q; Categorical overhead ohne neuen empirischen Nutzen in 2–3D-Beispielen.

### 5.2 Liu–Slotine–Barabási Controllability — DEFER (optionaler Anhang)

- Liu, Slotine & Barabási, *Controllability of complex networks*, Nature 473, 167–173 (2011); DOI [10.1038/nature10011](https://doi.org/10.1038/nature10011).

**Kalman-Rang** (LTI \(\dot x=Ax+Bu\)):

\[
\operatorname{rank}\big[B,\ AB,\ \ldots,\ A^{N-1}B\big] = N.
\]

**Strukturelle Treiberknotenzahl** (Maximum Matching \(M^*\) der bipartiten Repräsentation):

\[
N_D = \max\{N-|M^*|,\,1\}.
\]

**Warum defer:** Revision-3.2-Beispiele und Viability/UTAC sind typischerweise **niedrigdimensional** und aufgabenbezogen; Netzwerk-Controllability adressiert eine andere Skala. Als Anhangformel ok, als Kernmodul premature.

---

## 6. Aufnahmebedingungen (Astra-Standard)

Ein Erweiterungsvorschlag wird erst dann in den Formalismus-Kern übernommen, wenn **alle** Punkte erfüllt sind:

1. **Textformeln** (LaTeX/Markdown), keine Bildformeln.
2. **`verify_*.py`** mit reproduzierbarem JSON-Report unter `verification/`.
3. **Durchgerechnetes Mini-Beispiel** mit Zahlen aus dem Skriptlauf (Toleranzen dokumentiert).
4. **Explizites Mapping** auf bestehende Begriffe (VB1, `EI_q`, T1/T2) — keine parallele Terminologie ohne Brücke.
5. **Literatur-DOIs/arXiv** verifiziert (wie in diesem Review).
6. **Johann-OK** vor Mutation von `FORMALISM.md` / `REVISION_3_2.md`.

Gemini-Export: Punkte 1–3 derzeit **nicht** erfüllt → Review-only.

---

## 7. Vorgeschlagene Reihenfolge

1. Spec + `verify_sheaf_contextuality.py` (VB1-Erweiterung).
2. Spec + `verify_pid_rb.py` (EI_q-Zerlegung); RB-Kurve als Phase 2.
3. Kurzer Anhang „Deferred: Cospans & Network Controllability“ (Formeln oben) — **ohne** Kernmutation.
4. Erst nach grünen Verify-Läufen und Johann-Freigabe: Abschnitte in `FORMALISM.md` / neue Layer-Dateien.

---

## 8. Offene Fragen an Johann

1. Soll Verträglichkeitsbedingung 1 **erweitert** werden (stochastische/kontextuelle Familien + CF) oder ein **separates optionales Modul** bleiben?
2. Welche PID-Variante ist verbindlich: Williams–Beer \(I_{\min}\), Blackwell/Kolchinsky, oder Rosas-O-Information als grobe Synergie-/Redundanz-Kennzahl?
3. Für PID: welches kanonische \((Quellen, Ziel)\)-Paar im CREP/UTAC-Kontext (Mikro→Makro, Teilsysteme→Aufgabe, …)?
4. Darf ein erstes Sheaf-Toy bewusst **nicht-physikalisch** (PR-Box) sein, nur um CF-Infrastruktur zu härten?
5. Controllability: komplett streichen oder als **Anhangformel** in einem späteren ROADMAP-Ticket?
6. Gemini-Originaldatei: Soll sie archiviert werden (Bilder behalten) und nur die Textrekonstruktion weiterleben?

---

## 9. Quellenverzeichnis (kurz)

- Abramsky & Brandenburger (2011): arXiv:1102.0264; DOI 10.1088/1367-2630/13/11/113036  
- Abramsky, Barbosa & Mansfield (2017): arXiv:1705.07918; DOI 10.1103/PhysRevLett.119.050504  
- Williams & Beer (2010): arXiv:1004.2515  
- Kolchinsky (2024): arXiv:2405.07665; PMC11276267; DOI 10.3390/e26070546  
- Rosas et al. (2020): DOI 10.1371/journal.pcbi.1008289  
- Rosas et al. (2019) O-information: arXiv:1902.11239  
- Baez & Courser (2020): arXiv:1911.04630  
- Liu, Slotine & Barabási (2011): DOI 10.1038/nature10011  

Lokale Anker: `REVISION_3_2.md`, `context_transformations.md`, `FORMALISM.md`, `LITERATURE_CONNECTIONS.md`, `verification/`.

---

*Ende Review. Keine Formalismus-Mutation vorgenommen.*