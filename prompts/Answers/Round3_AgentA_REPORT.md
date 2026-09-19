# DeepResearch Runde 3 — Agent A (unabhängig)

**Datum:** 2026-09-19 (CEST)  
**Repo-Kontext:** GenesisAeon/scoped-correspondence-formalism — 15 Bausteine, verbunden durch Konjugation `T∘Φ≈Φ∘T`, **keine** vereinheitlichte Theorie.  
**Auftrag:** reine Literaturrecherche; keine Code-/Milestone-/Domänenentscheidung.  
**Abgrenzung:** keine Kenntnis von Agent B; nichts aus `/workspace/research_round3_B` gelesen.  
**Bereits erledigt:** siehe `ALREADY_DONE.md` (M9–M29 + neue Bausteine); Hard Rejects β≡Stabilität, V≡Panarchy≡Onsager-L, σ≈2.2, A_ij≡L_ij.

**Ehrlicher Vorbemerken zu Spur A:** Nach 25 gemergten Erweiterungen ist die Spur **knapp**. Zwei konkrete, bisher nicht umgesetzte Formel-zu-Formel-Kandidaten (Fenichel/GSPT war explizit OPEN; Floquet als zweites) — keine erzwungenen „Universalitäts“-Vorschläge.

---

# Spur A — weitere natürliche Erweiterungen bestehender Bausteine

## A1. Fenichel / Geometric Singular Perturbation Theory (GSPT)

1. **Name + Quelle.** Neil Fenichel, *Geometric singular perturbation theory for ordinary differential equations*, J. Differential Equations **31**, 53–98 (1979). DOI `10.1016/0022-0396(79)90152-9`. Vorgänger: Persistenz glatter invarianter Mannigfaltigkeiten, Indiana Univ. Math. J. **21**, 193–226 (1971/72), DOI `10.1512/iumj.1972.21.21017`. **Verifikation:** Crossref API 2026-09-19 — Titel/Autor/Jahr/Zeitschrift bestätigt. Beispiel-Referenz: Kuehn, *Multiple Time Scale Dynamics*, DOI `10.1007/978-3-319-12316-5`.

2. **Kernformel.** Fast-langsam-System
   \[
   \varepsilon \dot x = f(x,y),\qquad \dot y = g(x,y)
   \]
   (äquivalent \(\dot x = f\), \(\dot y = \varepsilon g\)). Die **kritische Mannigfaltigkeit**
   \[
   \mathcal{C}_0 = \{(x,y): f(x,y)=0\}
   \]
   sei kompakt und **normal hyperbolisch** (Eigenwerte von \(D_x f|_{\mathcal{C}_0}\) haben Realteil \(\neq 0\)). Dann existiert für hinreichend kleines \(\varepsilon>0\) eine glatte, \(\mathcal{O}(\varepsilon)\)-nahe **langsame Mannigfaltigkeit** \(\mathcal{C}_\varepsilon\), die lokal invariant ist und die Fluss-Dynamik auf \(\mathcal{C}_0\) fortsetzt (Fenichel 1979). An Faltpunkten (Verlust der normalen Hyperbolizität) gilt die Aussage lokal nicht — dort beginnt Canard-/Blow-up-Analyse.

3. **Anschluss.** Baustein **`dynamics`**. Formel-zu-Formel: `dynamics` hat bereits lokale Erholungsrate
   \[
   S_{\mathrm{rec}} = -\partial_x f\big|_{x^\ast}
   \]
   (`recovery_rate_at_equilibrium` / `recovery_rate_from_relaxation`). Fenichel liefert die **geometrische** Rechtfertigung, wann eine reduzierte langsame Dynamik auf einer Mannigfaltigkeit die volle Dynamik approximiert — also wann eine makroskopische \(S_{\mathrm{rec}}\)-Beschreibung auf der kritischen Mannigfaltigkeit legitim ist. **Nicht** identisch mit Contraction (M14) oder Landau-Vergleich (M29). Status laut `ALREADY_DONE.md`: **noch OPEN**.

4. **Mini-Beispiel (van der Pol, handprüfbar).**
   \[
   \varepsilon\dot x = y - \tfrac{x^3}{3} + x,\qquad \dot y = -x
   \]
   (äquivalente Standardform). Kritische Mannigfaltigkeit \(y = x^3/3 - x\). Falten bei \(\partial_x(x^3/3-x)=0 \Rightarrow x=\pm 1\), also
   \[
   (x,y) = \bigl(1,-\tfrac{2}{3}\bigr),\quad \bigl(-1,+\tfrac{2}{3}\bigr).
   \]
   Auf den normal hyperbolischen Ästen \(|x|>1\) (attraktiv bzw. repulsiv je nach Zweig) persistiert \(\mathcal{C}_\varepsilon\). Numerische Kontrolle der Faltkoordinaten: \(1^3/3-1=-2/3\), \((-1)^3/3-(-1)=+2/3\).

5. **Aufwand:** **mittel** (Textformeln + `verify_*` mit van-der-Pol-Falten und Distanz \(\mathrm{dist}(\mathcal{C}_\varepsilon,\mathcal{C}_0)=\mathcal{O}(\varepsilon)\) an einem Punkt; volle Canard-Theorie = groß — weglassen).

---

## A2. Floquet-Multiplier für periodische Orbits

1. **Name + Quelle.** G. Floquet, *Sur les équations différentielles linéaires à coefficients périodiques*, Ann. sci. Éc. Norm. Sup. **12**, 47–88 (1883), DOI `10.24033/asens.220`. Moderne Formulierung/Numerik: Castelli & Lessard, SIAM J. Appl. Dyn. Syst. (2013), DOI `10.1137/120873960`. **Verifikation:** Crossref für beide DOIs 2026-09-19 OK.

2. **Kernformel.** Sei \(x^*(t)\) eine \(T\)-periodische Lösung von \(\dot x=f(x)\). Die Variationsgleichung
   \[
   \dot\Phi = Df\bigl(x^*(t)\bigr)\,\Phi,\qquad \Phi(0)=I
   \]
   liefert die **Monodromiematrix** \(M=\Phi(T)\). Eigenwerte \(\mu_i\) von \(M\) sind die **Floquet-Multiplier**; \(\mu_i=e^{\lambda_i T}\) mit Floquet-Exponenten \(\lambda_i\). Bei autonomem System ist stets ein Multiplier \(\mu=1\) (Phasenrichtung). **Orbitale asymptotische Stabilität**, wenn alle übrigen \(|\mu_i|<1\); Instabilität, wenn ein \(|\mu_i|>1\).

3. **Anschluss.** Baustein **`dynamics`**. Formel-zu-Formel: bisher deckt `dynamics` **Gleichgewicht**-Linearisierung ab (\(S_{\mathrm{rec}}=-\mathrm{Re}\,\lambda\) bzw. \(-Df\)). Floquet ist die **kanonische** Verallgemeinerung derselben Linearisierungsidee auf periodische Orbits: Stabilität \(\Leftrightarrow\) Multiplier im Einheitskreis (außer der trivialen 1). Keine Überschneidung mit M14 Contraction (globale metrische Kontraktion) oder M29 Landau.

4. **Mini-Beispiel (skalar, periodischer Koeffizient).** Hill/Mathieu-artig reduziert auf 1D-Variation mit \(T=2\pi\):
   Sei die Monodromie einer 2D-Variationsgleichung mit \(\operatorname{tr} M = 1.5\), \(\det M=1\) (Flächenform). Dann
   \[
   \mu_\pm = \frac{1.5 \pm \sqrt{2.25-4}}{2} = \frac{1.5 \pm i\sqrt{1.75}}{2},
   \]
   also \(|\mu_\pm|=1\) (neutrale Stabilität im konservativen Fall). Dagegen \(\operatorname{tr} M=2.5\), \(\det M=1\):
   \[
   \mu_\pm = \frac{2.5\pm\sqrt{6.25-4}}{2} = \frac{2.5\pm\sqrt{2.25}}{2} \in \{2,\,0.5\},
   \]
   also ein Multiplier \(2>1\) ⇒ instabil. Handrechnung: \(\sqrt{2.25}=1.5\), \(\mu_+=(2.5+1.5)/2=2\), \(\mu_-=(2.5-1.5)/2=0.5\).

5. **Aufwand:** **klein–mittel** (Monodromie für ein explizites 2D-Beispiel mit bekannter periodischer Bahn, JSON-Report der Multiplier).

---

### Spur-A-Fazit (Knappheit)

Weitere naheliegende Kandidaten (Mori–Zwanzig-Projektion, klassische Mittelung) überlappen thematisch stark mit bereits vorhandenem Closure-Memory-Toy bzw. M21 Error Bounds und wurden **nicht** als eigene Vorschläge forciert. Zwei belastbare, formelgenaue Anschlüsse an `dynamics` reichen für Spur A; die Spur ist nach 25 Merges ehrlich **dünn**.

---

# Spur B — strukturell passende, eigenständige Themenfelder

## B1. GENERIC ↔ Navier–Stokes / viskose Dissipation

1. **Name + Quelle.** M. Grmela & H. C. Öttinger, *Phys. Rev. E* **56**, 6620 (1997), DOI `10.1103/PhysRevE.56.6620` (Teil I, Formalismus); H. C. Öttinger & M. Grmela, *Phys. Rev. E* **56**, 6633 (1997), DOI `10.1103/PhysRevE.56.6633` (Teil II, Illustrationen). **Verifikation:** Crossref + APS-Abstract-Landingpage 2026-09-19. Explizite Newton-Fluid-\(M\)-Matrix auch in Vázquez et al., arXiv:physics/0306159 (Gl. 29–31), die GENERIC I/II zitiert.

2. **Kernformel (GENERIC).**
   \[
   \dot x = L(x)\,\frac{\delta E}{\delta x} + M(x)\,\frac{\delta S}{\delta x},
   \]
   mit \(L^\top=-L\), \(M^\top=M\succeq 0\), Degenerationen
   \[
   L\,\frac{\delta S}{\delta x}=0,\qquad M\,\frac{\delta E}{\delta x}=0.
   \]
   Für ein **Newton-Fluid** liefert der irreversible Block von \(M\) genau den viskosen Spannungstensor
   \[
   \tau = -\eta\bigl(\nabla v+(\nabla v)^\top\bigr) - \bigl(\zeta-\tfrac{2}{3}\eta\bigr)(\nabla\cdot v)\,I
   \]
   und die zugehörige Entropieproduktion (Öttinger–Grmela / reproduziert in physics/0306159). Das ist die formelgenaue Brücke GENERIC \(\to\) Navier–Stokes-Dissipation.

3. **Anschluss.** Primär **`coupling.check_generic_structure`** (prüft genau \(J^\top=-J\), \(M^\top=M\succeq0\), \(J\nabla S=0\), \(M\nabla E=0\)); sekundär **`thermo`** (`project_generic_structure` ruft denselben Check). **Eigenständiges Themenfeld:** hydrodynamische \(M\)-Operatoren / 1D-Reduktion — **nicht** Gleichsetzung von `A_ij` mit `L_ij` und nicht Onsager-\(L\) mit Panarchy-\(V\).

4. **Mini-Beispiel (0D viskose Relaxation, handprüfbar).** Zustand \(x=(u,e)\), Energie \(E=e+u^2/2\), Entropie \(S=\ln e\) (Toy), \(\nabla E=(u,1)\), \(\nabla S=(0,1/e)\). Zielkinetik \(\dot u=-\gamma u\), \(\dot e=\gamma u^2\) (kinetisch \(\to\) intern). Mit \(\gamma=1\), \(u=2\), \(e=3\):
   \[
   M=\begin{pmatrix}\gamma e & -\gamma u e\\ -\gamma u e & \gamma u^2 e\end{pmatrix}
   =\begin{pmatrix}3 & -6\\ -6 & 12\end{pmatrix}.
   \]
   Prüfung: \(M\nabla E=(0,0)\), \(M\nabla S=(-2,4)=(-\gamma u,\gamma u^2)\), \(M=M^\top\), Eigenwerte \(\{0,15\}\) (PSD). Mit \(J=0\) erfüllt das exakt die fünf Checks von `check_generic_structure`. 1D-Kontinuum: \(\partial_t u=\eta\partial_{xx}u\) ist die Feldfassung derselben Dissipationsstruktur.

5. **Aufwand:** **mittel** (0D-Verify gegen bestehenden GENERIC-Check = klein; echte 1D-Finite-Differenzen-\(M\)-Diskretisierung = mittel).

---

## B2. Chapman–Enskog-Entwicklung → Viskosität als Closure

1. **Name + Quelle.** S. Chapman & T. G. Cowling, *The Mathematical Theory of Non-Uniform Gases*, 3rd ed., Cambridge University Press (1970; CML-Reissue ISBN-13 `978-0-521-40844-8`). **Verifikation:** Kein Crossref-DOI für die Monographie (ISBN-Filter total-results=0); ISBN/Verlag über Cambridge Mathematical Library bestätigt; Formel stimmt mit Standard-Peer-Review-Zitaten der 1. CE-Approximation überein.

2. **Kernformel.** Chapman–Enskog löst die Boltzmann-Gleichung störungstheoretisch in der Knudsen-Zahl; in **erster Ordnung** entsteht Newton-Hydrodynamik mit Viskosität (harte Kugeln, Durchmesser \(\sigma\), Masse \(m\)):
   \[
   \eta_{\mathrm{CE}} = \frac{5}{16\sigma^{2}}\sqrt{\frac{m\,k_B T}{\pi}}
   \]
   (1. Approximation; höhere Sonine-Korrektur \(\approx 1.016\cdot\eta_{\mathrm{CE}}\) für starre Kugeln).

3. **Anschluss.** Baustein **`closure`**, Bedingung `PC = CQ` / `is_exact_closure`. Formel-zu-Formel-Analogie (ehrlich als **strukturell**, nicht als Identität):  
   - Mikro: Boltzmann-Kollisionsoperator \(P\) auf Verteilungsfunktion;  
   - Projektion \(C\): Momente (Dichte, Impuls, Energie);  
   - Makro: hydrodynamischer Generator \(Q\) (Euler/NS).  
   CE konstruiert systematisch ein \(Q\) (und Transportkoeffizienten), so dass der Closure-Defekt in der Knudsen-Ordnung kontrolliert ist — dasselbe Muster wie \(\delta_{cl}=\max_i\mathrm{TV}((PC)_i,(CQ)_i)\), aber kontinuierlich/kinetisch. **Kein** Claim, CE „sei“ Lumpability (M11) oder Michel–Siegle (M21).

4. **Mini-Beispiel.** \(m=1\), \(k_B T=1\), \(\sigma=1\):
   \[
   \eta_{\mathrm{CE}}=\frac{5}{16\sqrt{\pi}}\approx 0.17630924486.
   \]
   (Nachrechnung: \(5/16=0.3125\), \(\sqrt{1/\pi}\approx0.5641895835\), Produkt \(\approx0.176309\).) Interpretation: aus kinetischem Mikro-Modell folgt ein makroskopischer Transportkoeffizient — Closure mit expliziter Zahl.

5. **Aufwand:** **mittel** (Formel + Zahlenbeispiel + Mapping-Text auf `PC=CQ`; voller Boltzmann-Löser = groß, unnötig für Astra-Standard).

---

### Spur B — weitere Kandidaten (kurz, nicht forciert)

- **Aktive Materie / Vicsek–Toner–Tu:** thematisch passend zu `pattern_formation`, aber ohne in dieser Runde verifiziertes, handprüfbares Primärformel-Beispiel mit klarem Baustein-Anschluss → **nicht** als voller Vorschlag geführt.
- **Nichtgleichgewichts-Phasenübergänge:** überlappen mit Turing (bereits Baustein) und Scheffer (Spur C) — Vermeidung von Doppelzählung.

---

# Spur C — CREP/UTAC/AFET-Inspirationsliteratur (alle vier)

**Leitlinie:** keine Wiederbelebung der Hard Rejects. Wo nur Begriffsähnlichkeit existiert → ehrlich sagen.

---

## C1. Panarchy / Adaptive Cycle (Holling; Gunderson & Holling)

1. **Primärquellen + Formel.**
   - Holling 1973, DOI `10.1146/annurev.es.04.110173.000245`; Holling 2001, DOI `10.1007/s10021-001-0101-5`; Gunderson & Holling (eds.) 2002, *Panarchy*, Island Press (Monographie, kein Crossref-DOI unter Standard-ISBN) — **qualitativ**: Exploitation–Conservation–Release–Reorganization, verbundenheit/Potential/Resilienz. **Keine** kanonische ODE in Holling selbst.
   - **Formale Fassung:** Zwick & Hughes 2017, DOI `10.1145/3145574.3145591` — Adaptive Cycle als Trajektorie auf der **Cusp-Katastrophe**. Äquilibrien der Cusp-Potentialfunktion erfüllen
     \[
     \frac{\partial V}{\partial x}=0 \quad\Leftrightarrow\quad x^3 - a x - b = 0
     \]
     (Normalform; Falten bei Diskriminante \(4a^3-27b^2=0\)). Historisch verwandt: Jones 1977, DOI `10.1177/003754977702900102`. **Verifikation:** Crossref für Holling 1973/2001, Zwick 2017, Jones 1977 OK.

2. **(a) oder (b)?** **(a) Erweiterung von `dynamics`**, nicht neuer Baustein und **nicht** Identifikation \(V\equiv\mathrm{Panarchy}\equiv\mathrm{Onsager}\text{-}L\). Begründung: `dynamics` besitzt bereits `cusp_field` / `CubicNormalForm`
   \[
   \tau\dot x = -x^3 + a x + b,
   \]
   Diskriminante, `S_rec`, Fixed Points. Zwick liefert eine **Interpretation** der Kontrolltrajektorie \((a(t),b(t))\) als Adaptive-Cycle-Geometrie (Faltung/Hysterese = Release). Das ist Formel-zu-Formel am **bereits vorhandenen** Cusp — ausdrücklich **ohne** ökologisches „Potential“ mit thermodynamischer freier Energie oder Onsager-Matrix gleichzusetzen.

3. **Falls nichts?** Nicht der Fall: zitierfähige Formalisierung existiert (Zwick), aber Holling selbst bleibt qualitativ. Ehrlicher Status: **Formalisierung = Cusp-Geometrie; Panarchy-Semantik = Interpretationsschicht**.

4. **Mini-Beispiel.** \(a=3\), \(b=0\): Gleichgewichte \(x=0,\pm\sqrt{3}\). Diskriminante \(4\cdot 27=108>0\) (bistabil). Fold-Kurve \(b=\pm(2/\sqrt{27})a^{3/2}\); bei \(a=3\): \(b_c=\pm 2/\sqrt{3}\approx\pm 1.1547\). Hysterese beim langsamen Durchfahren von \(b\) über \(\pm b_c\) = mathematisches Abbild von Conservation→Release.

5. **Aufwand:** **klein** (Mapping-Dokument + Verify, dass Cycle-Kontrollpfad die bestehende Cusp-API nutzt; **kein** neues Symbol \(V_{\mathrm{panarchy}}\)).

---

## C2. Autopoiesis (Maturana & Varela; Fontana & Buss / COT)

1. **Primärquellen + Formel.**
   - Varela, Maturana & Uribe 1974, DOI `10.1016/0303-2647(74)90031-8` — begriffliche/algorithmische Charakterisierung, **kein** allgemein akzeptierter analytischer Satz mit handprüfbarer ODE-Identität.
   - Fontana & Buss 1994, DOI `10.1007/BF02458289` (und PNAS `10.1073/pnas.91.2.757`): λ-Kalkül-Chemie; selbst-erhaltende Organisationen als syntaktisch/funktionale Fixsysteme.
   - **Anerkannte algebraische Operationalisierung:** Dittrich & Speroni di Fenizio, *Chemical Organisation Theory*, DOI `10.1007/s11538-006-9130-8`. Definition: Eine Menge \(O\) von Spezies ist eine **Organisation**, wenn sie
     - **abgeschlossen** ist (Reaktionen in \(O\) erzeugen nur Spezies in \(O\)), und
     - **selbst-erhaltend** ist (es gibt einen Fluss/Produktionsvektor, der jede Spezies in \(O\) mit nichtnegativer Nettoproduktion versorgt).
     **Satz (COT):** Jeder stöchiometrische stationäre Zustand der kinetischen ODEs \(\dot x = N v(x)\) induziert eine Organisation (Träger der positiven Komponenten bildet eine Organisation). Die Umkehrung gilt im Allgemeinen **nicht**.

2. **(a) oder (b)?** Eher **(b) Kandidat für einen neuen, eigenständigen Baustein** (z. B. `organization` / chemische Organisationsstruktur) — **oder** schwache Erweiterung von `membership` (Abschluss unter Erzeugungsrelation). **Nicht** (a) an `viability` oder `dynamics` gleichsetzen: COT ist algebraisch-stöchiometrisch, Viability ist mengentheoretisch-dynamisch (sichere Mengen) — strukturelle Ähnlichkeit ≠ Identität (Hard-Ban beachten).

3. **Ehrliches Urteil.** Maturana–Varelas volle Autopoiesis (operationale Schließung **plus** räumliche Grenze/Membran) hat **keine** allgemein anerkannte, vollständige mathematische Operationalisierung mit einem einzigen kanonischen Mini-Beispiel, das alle Klauseln abdeckt. COT/Fontana–Buss operationalisieren **Selbst-Erhaltung/Abschluss** seriös — das ist ein **Teilaspekt**, nicht „Autopoiesis = COT“. Ergebnis: **teilweise zitierfähig (COT); vollständige Autopoiesis = nichts Kanonisches**. Das ist ein valides Spur-C-Ergebnis, kein Scheitern der Recherche.

4. **Mini-Beispiel (COT, 2 Spezies).** Reaktionen: \(A\to\emptyset\) (Abbau), \(A+B\to 2B\) (katalytische Umwandlung), Zufluss \(\emptyset\to A\). Organisation-Kandidaten: \(\{A,B\}\) kann unter geeigneten Raten selbst-erhaltend und abgeschlossen sein; \(\{B\}\) allein ist typischerweise **nicht** selbst-erhaltend (kein Nachschub ohne \(A\)). Stationärer Zustand mit \(x_A^\ast>0,x_B^\ast>0\) ⇒ Träger \(\{A,B\}\) ist Organisation (Dittrich-Satz). Konkrete Zahlen hängen von Raten ab; der Satz selbst ist struktural und handprüfbar an kleinen Stöchiometrie-Matrizen.

5. **Aufwand:** **groß**, falls neuer Baustein; **mittel**, falls nur COT-Closure-Check als Erweiterung von `membership`. Empfehlung: nur bei Interesse Johanns an neuem Baustein.

---

## C3. Strukturelle Kopplung als Mathematik (Pecora & Carroll)

1. **Primärquelle + Formel.** L. M. Pecora & T. L. Carroll, *Synchronization in chaotic systems*, Phys. Rev. Lett. **64**, 821 (1990), DOI `10.1103/PhysRevLett.64.821`. Ausarbeitung: Phys. Rev. A **44**, 2374 (1991), DOI `10.1103/PhysRevA.44.2374`. **Verifikation:** Crossref beide OK.

   Drive–Response-Zerlegung \(x=(v,w)\):
   \[
   \dot v = f_v(v,w),\qquad \dot w = f_w(v,w),
   \]
   Response-Kopie \(\dot w' = f_w(v,w')\). Synchronisation \(w'(t)\to w(t)\), wenn alle **bedingten Lyapunov-Exponenten** (CLEs) des Response-Variationssystems
   \[
   \delta\dot w = D_w f_w\bigl(v(t),w(t)\bigr)\,\delta w
   \]
   **negativ** sind.

2. **(a) oder (b)?** **(a) Erweiterung von `coupling`**. Formel-zu-Formel: `coupling` modelliert bereits gerichtete/paarweise Einflüsse und GENERIC-Struktur; Pecora–Carroll liefert ein **prüfbares Synchronisationskriterium** für drive-response-gekoppelte Systeme (CLE-Vorzeichen). Das ist eine mathematische Fassung „struktureller Kopplung“ im Sinne dynamischer Mitführung — **ohne** Luhmann-Soziologie und ohne Gleichsetzung mit GENERIC-\(L,M\) oder \(A_{ij}\equiv L_{ij}\).

3. **Nichts?** Nicht der Fall — klare Primärformel.

4. **Mini-Beispiel (lineares Response).** Drive \(v(t)=\sin t\), Response \(\dot w = -k(w-v)\). Variationsgleichung \(\delta\dot w=-k\,\delta w\), CLE \(=-k\). Für \(k=2>0\): CLE\(-2<0\) ⇒ Sync. Explizit: \(w(t)-v(t)\) klingt wie \(e^{-kt}\) ab. Für \(k=-0.5\): CLE \(+0.5>0\) ⇒ kein Sync.

5. **Aufwand:** **klein–mittel** (CLE für ein niedrigdimensionales Drive–Response-Paar; optional Lorenz-x-Drive als klassisches Pecora-Beispiel = mittel).

---

## C4. Early-Warning / kritisches Verlangsamen (Scheffer et al. 2009)

1. **Primärquelle + Formel.** M. Scheffer et al., *Early-warning signals for critical transitions*, Nature **461**, 53–59 (2009), DOI `10.1038/nature08227`. **Verifikation:** Crossref OK; Box 3 im Paper gegengelesen.

   AR(1)-Modell der Fluktuationen um ein Gleichgewicht:
   \[
   y_{n+1} = a\, y_n + s\,\varepsilon_n,\qquad a = e^{-\lambda\,\Delta t},
   \]
   mit Erholungsrate \(\lambda>0\) und \(\varepsilon_n\sim\mathcal{N}(0,1)\). Dann Lag-1-Autokorrelation \(\rho_1=a\) und
   \[
   \mathrm{Var}(y)=\frac{s^2}{1-a^2}.
   \]
   Bei kritischem Verlangsamen \(\lambda\to 0^+\) gilt \(a\to 1^-\), damit \(\rho_1\uparrow 1\) und \(\mathrm{Var}(y)\uparrow\infty\).

2. **(a) oder (b)?** **(a) Erweiterung von `dynamics`** (primär). Formel-zu-Formel: `dynamics` definiert bereits
   \[
   S_{\mathrm{rec}}=\lambda=-\partial_x f\big|_{x^\ast}
   \]
   (`recovery_rate_at_equilibrium`). Scheffer übersetzt \(S_{\mathrm{rec}}\to 0\) in **beobachtbare** Zeitreihen-Statistiken (Varianz, Autokorrelation). Sekundär interessant für `identifiability` nur als „Indikator schätzt \(\lambda\)“ — aber der Satz sitzt in der Dynamik, nicht in der Parameter-Identifizierbarkeit. **Explizit verboten:** \(S_{\mathrm{rec}}\) oder Varianz mit \(\beta_{\mathrm{response}}\) gleichsetzen (verschiedene Einheiten; Docstring „Independence of beta_response“).

3. **Nichts?** Nicht der Fall.

4. **Mini-Beispiel.** \(s=1\), \(\Delta t=1\):
   - \(\lambda=0.1\) ⇒ \(a=e^{-0.1}\approx 0.904837\), \(\mathrm{Var}\approx 5.5167\);
   - \(\lambda=0.01\) ⇒ \(a\approx 0.990050\), \(\mathrm{Var}\approx 50.502\).
   Varianz steigt um Faktor \(\approx 9.15\), wenn \(\lambda\) um Faktor 10 sinkt — handprüfbar.

5. **Aufwand:** **klein** (AR(1)-Synthetik + Vergleich mit `S_rec` der Cusp nahe der Fold-Kurve).

---

# Gesamtübersicht

| Spur | Vorschläge | Ehrliche Leerstellen |
|------|------------|----------------------|
| A | **2** (Fenichel→dynamics; Floquet→dynamics) | Spur nach 25 Merges knapp; Mori/MZ nicht forciert |
| B | **2** (GENERIC↔NS→coupling/thermo; Chapman–Enskog→closure) | Aktive Materie nicht als voller Vorschlag |
| C | **4/4 behandelt** | Autopoiesis: nur **Teil**-Operationalisierung (COT); volle Maturana–Varela-Autopoiesis **ohne** kanonische Formel. Panarchy: Formalisierung = Cusp (bereits in dynamics), Semantik ≠ Hard-Reject-Identität |

**Priorisierung (nur Recherche-Meinung, keine Domänenentscheidung):** C4 (klein, sehr klar) → C3 → B1 → A1 → B2 → A2 → C1 (klein, aber politisch sensibel wg. Vorgeschichte) → C2 (groß/teilweise).
