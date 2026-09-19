# Round-3 DeepResearch — Agent B (unabhängig)

**Repo:** GenesisAeon/scoped-correspondence-formalism  
**Datum:** 2026-09-19 (Europe/Berlin, UTC+2)  
**Modus:** reine Literaturrecherche — kein Code, keine Domänenentscheidung  
**Arbeitsverzeichnis:** `/workspace/research_round3_B/`  
**Hinweis Spur A:** Nach 25 bereits gemergten Erweiterungen (siehe `ALREADY_DONE.md`) ist die Spur dünn. Zwei konkrete, noch offene Formelanschlüsse werden vorgeschlagen; weitere Kandidaten ohne handprüfbares Mini-Beispiel wurden verworfen.

---

## Spur A — weitere natürliche Erweiterungen bestehender Bausteine

### A1. Fenichel / Geometric Singular Perturbation Theory (GSPT) → `dynamics`

1. **Name + Quelle + Verifikation**  
   Neil Fenichel, *Geometric singular perturbation theory for ordinary differential equations*, Journal of Differential Equations **31**, 53–98 (1979).  
   DOI: `10.1016/0022-0396(79)90152-9`  
   **Verifikation:** Crossref-API `https://api.crossref.org/works/10.1016/0022-0396(79)90152-9` am 2026-09-19: Titel, Autor Fenichel, Jahr 1979, Band 31, Seiten 53–98 bestätigt. (In `ALREADY_DONE.md` explizit als **OPEN** auf `dynamics` geführt — hier erstmals mit DOI und Mini-Beispiel ausgearbeitet.)

2. **Kernformel**  
   Fast-slow-System
   \[
   \varepsilon \dot x = f(x,y),\qquad \dot y = g(x,y).
   \]
   Kritische Mannigfaltigkeit \(M_0=\{f(x,y)=0\}\). Ist \(M_0\) kompakt und **normal hyperbolisch** (Eigenwerte von \(D_x f|_{M_0}\) haben Realteil \(\neq 0\)), so existiert für kleines \(\varepsilon>0\) eine lokal invariante slow manifold \(M_\varepsilon = O(\varepsilon)\)-nah an \(M_0\) (Fenichel).  
   Van-der-Pol-Normalform: \(S(x)=x^3/3-x\), \(S'(x)=x^2-1\); anziehende Äste für \(|x|>1\).

3. **Anschluss**  
   Baustein **`dynamics`**. Formel-zu-Formel: Reduktion auf die slow manifold liefert eine effektive makroskopische Vektorfeld-Dynamik; die transversale Kontraktionsrate \(|\operatorname{Re}\lambda_{\mathrm{fast}}|/\varepsilon\) ist die handprüfbare Größe neben bereits vorhandener Kontraktionsanalyse (M14) — **ohne** Gleichsetzung mit `beta_response` oder anderen Layern.

4. **Mini-Beispiel**  
   Van der Pol: \(S'(2)=3>0\) (anziehend), \(S'(0)=-1<0\) (abstoßend), \(S'(1.5)=1.25>0\) (anziehend). Falten bei \(x=\pm 1\), wo Normalhyperbolizität scheitert (canards möglich) — von Hand prüfbar ohne Simulation.

5. **Aufwand:** **mittel** (slow-manifold-Residual + Normalhyperbolizitäts-Check + ein van-der-Pol-Verify-Skript).

---

### A2. Crooks-Fluktuationstheorem → `thermo`

1. **Name + Quelle + Verifikation**  
   Gavin E. Crooks, *Entropy production fluctuation theorem and the nonequilibrium work relation for free energy differences*, Phys. Rev. E **60**, 2721–2726 (1999).  
   DOI: `10.1103/PhysRevE.60.2721`  
   arXiv: `cond-mat/9901352`  
   **Verifikation:** Crossref-API bestätigt Titel/Autor/Jahr/Zeitschrift; ar5iv-Volltext der Formeln (2),(3),(10),(11) gegengelesen.

2. **Kernformel**  
   \[
   \frac{P_F(+\omega)}{P_R(-\omega)}=e^{+\omega},\qquad
   \omega=-\beta\Delta F+\beta W,\qquad
   \langle e^{-\beta W}\rangle=e^{-\beta\Delta F}.
   \]

3. **Anschluss**  
   Baustein **`thermo`** (Erweiterung neben Schnakenberg M18). Formel-zu-Formel: Crooks liefert eine **trajektorienweise** Relation für die Entropieproduktion \(\omega\), die Schnakenbergs Netzwerkwärme/Affinitäten im stochastischen Pfad-Ensemble ergänzt — **ohne** Onsager-\(L_{ij}\) mit `A_ij` zu identifizieren und ohne Meta-Theorie.

4. **Mini-Beispiel**  
   \(\beta=1\), \(\Delta F=0\), \(W=1\): \(P_F(+1)/P_R(-1)=e\approx 2.71828\). Handprüfbar; im Paper mit Metropolis-Toy veranschaulicht.

5. **Aufwand:** **klein–mittel** (Verteilungsschätzer + Ratio-Check gegen \(e^{\beta(W-\Delta F)}\)).

---

### Spur-A-Ehrlichkeit

Weitere oft genannte Kandidaten (Tikhonov 1952 ohne DOI, Mori–Zwanzig, Oseledets) wurden geprüft: entweder keine leicht verifizierbare Primär-DOI, oder nur thematische Nähe ohne handprüfbares Astra-Beispiel. Nach 25 Merges bleiben **A1 und A2** die belastbarsten Neuanschlüsse.

---

## Spur B — strukturell passende, eigenständige Themenfelder

### B1. GENERIC ↔ Navier–Stokes (Öttinger & Grmela)

1. **Name + Quelle + Verifikation**  
   - M. Grmela & H. C. Öttinger, *Dynamics and thermodynamics of complex fluids. I*, Phys. Rev. E **56**, 6620–6632 (1997). DOI `10.1103/PhysRevE.56.6620`  
   - H. C. Öttinger & M. Grmela, *… II. Illustrations…*, Phys. Rev. E **56**, 6633–6655 (1997). DOI `10.1103/PhysRevE.56.6633`  
   **Verifikation:** beide Crossref-API-Abrufe 2026-09-19: Titel, Autoren, Band 56, Seiten und Jahre bestätigt. APS-Abstract zu II: GENERIC-Bausteine \(E,S,L,M\) und Friction-Matrix für Nichtgleichgewichtsbeispiele.

2. **Kernformel**  
   \[
   \dot x = L(x)\,\frac{\delta E}{\delta x}+M(x)\,\frac{\delta S}{\delta x},
   \]
   mit \(L=-L^T\), \(M=M^T\succeq 0\), Degeneriertheit \(L\,\delta S/\delta x=0\), \(M\,\delta E/\delta x=0\).  
   Hydrodynamik: \(L\) erzeugt Euler/Druck; \(M\) erzeugt viskose/thermische Dissipation → Navier–Stokes-Spannung \(\tau\approx 2\eta D+\zeta(\nabla\cdot u)I\).

3. **Anschluss**  
   Direkt an **`coupling.check_generic_structure`** (und optional `thermo`): dieselbe Strukturprüfung \(J\equiv L\) antisymmetrisch, \(M\) SPD, \(J\nabla S=0\), \(M\nabla E=0\). Eigenständiges Themenfeld „viskose Hydrodynamik als GENERIC-Instanz“, **kein** Zusammenlegen von Bausteinen und **kein** \(A_{ij}\equiv L_{ij}\).

4. **Mini-Beispiel (0D-Reduktion viskoser Dämpfung, handprüfbar)**  
   Zustand \((q,p,S)\), \(m=k=T=1\), \(\gamma=0.5\), \(p=2\):
   \[
   J=\begin{pmatrix}0&1&0\\-1&0&0\\0&0&0\end{pmatrix},\quad
   a=(0,T,-v),\ v=p/m,\quad M=\gamma\,aa^T.
   \]
   Residuen: \(\|J^T+J\|_\infty=0\), \(J\nabla S=0\), \(M\nabla E=0\), \(\min\mathrm{eig}(M)=0\) (PSD).  
   Irreversible Rate: \(\dot p_{\mathrm{irr}}=-\gamma T v=-1\), \(\dot S_{\mathrm{irr}}=\gamma v^2=2\) — 0D-Analogon von \(\tau=-\eta\partial_x u\).

5. **Aufwand:** **mittel** (1D/2-Zellen-Diskretisierung + Aufruf von `check_generic_structure` + JSON-Report). Volle 3D-NS: **groß**.

---

### B2. Chapman–Enskog → `closure` (\(PC=CQ\))

1. **Name + Quelle + Verifikation**  
   S. Chapman & T. G. Cowling, *The Mathematical Theory of Non-Uniform Gases*, Cambridge University Press (3. Aufl. 1970/1990 Cambridge Mathematical Library, ISBN `0-521-40844-X`).  
   **Verifikation:** Buch (keine Artikel-DOI); Formel gegen arXiv `1702.06313` (zitiert Chapman & Cowling 1952) und Standard-Hard-Sphere-CE-Literatur abgeglichen. Buch-Identität über WorldCat/Cambridge bestätigt.

2. **Kernformel** (Hard Spheres, erste Sonine-Ordnung, \(k_B=1\))  
   \[
   \eta_{\mathrm{CE}}=\frac{5}{16\sqrt{\pi}}\,\frac{\sqrt{mT}}{d^2}.
   \]
   Chapman–Enskog: Boltzmann-\(f\) → hydrodynamische Momente \((\rho,u,T)\) mit geschlossenem Stress; das ist strukturell ein Closure.

3. **Anschluss**  
   Baustein **`closure`**: Mikro-Kernel/Operator \(\leftrightarrow P\), Momentenprojektion \(\leftrightarrow C\), hydrodynamischer Generator \(\leftrightarrow Q\); exakte Closure-Idee \(PC=CQ\) bzw. Defekt \(\delta_{cl}\). CE liefert die konkrete Transportzahl \(\eta\) als Ergebnis des Closure — Formel-zu-Formel, ohne Bausteine gleichzusetzen.

4. **Mini-Beispiel**  
   \(m=T=d=1\): \(\eta_{\mathrm{CE}}=5/(16\sqrt{\pi})\approx 0.176309\). Handrechner + `math.sqrt`.

5. **Aufwand:** **mittel** (CE-Viskositätsformel + Mapping-Dokument \(P,C,Q\) im kinetischen Sinn; volle Boltzmann-Solver: **groß**).

---

### Spur B — weitere Kandidaten (kurz)

**Aktive Materie / Nichtgleichgewichts-Phasenübergänge:** bekannte Sätze (z. B. Vicsek), aber kein für Astra hinreichend kleines, primärquellen-scharfes Mini-Beispiel ohne großen Simulationsaufwand gefunden → **nicht** als eigener Vorschlag erzwungen.

---

## Spur C — CREP/UTAC/AFET-Inspirationsliteratur (alle vier)

### C1. Panarchy / Adaptive Cycle

1. **Primärquellen**  
   - C. S. Holling, *Resilience and Stability of Ecological Systems*, Annu. Rev. Ecol. Syst. **4**, 1–23 (1973). DOI `10.1146/annurev.es.04.110173.000245` (Crossref OK).  
   - L. H. Gunderson & C. S. Holling (Eds.), *Panarchy*, Island Press (2002), ISBN `1-55963-857-5` (Buch, keine DOI).  
   - **Formale Operationalisierung:** M. Zwick & J. Hughes, *Formalizing the Panarchy Adaptive Cycle with the Cusp Catastrophe*, Proc. CSS 2017. DOI `10.1145/3145574.3145591` (Crossref OK).  

   **Kernformel (Cusp / Thom, bei Zwick & Hughes):**
   \[
   V=\tfrac14 y^4-ny-\tfrac12 s y^2,\qquad
   \frac{\partial V}{\partial y}=0\;\Rightarrow\; y^3-n-s y=0.
   \]
   Falten/Hysterese: Bifurkationsmenge \(27n^2=4s^3\).

2. **(a) oder (b)?**  
   **(a) Erweiterung von `dynamics`** (Fold/Hysterese als dynamisches System) — **nicht** neuer Baustein „Panarchy“, und **explizit nicht** die verworfene Identität \(V\equiv\mathrm{Panarchy}\equiv\mathrm{Onsager}\text{-}L\).

3. **Mini-Beispiel**  
   \(s=3\): \(n_{\mathrm{crit}}=\pm 2\), Falte bei \(y=\pm\sqrt{s/3}=\pm 1\). Trajektorie von \(n\) hin und zurück → Hysterese. Handprüfbar.

4. **Aufwand:** **klein–mittel**.  
5. **Warnung:** Nur die Cusp-Dynamik anschließen; Panarchy-Begriffe bleiben Labels der Interpretation, keine Cross-Layer-Konstante.

---

### C2. Autopoiesis

1. **Quellen**  
   - H. R. Maturana & F. J. Varela, *Autopoiesis and Cognition*, 1980. DOI Buch `10.1007/978-94-009-8947-4`.  
   - W. Fontana & L. W. Buss, *„The arrival of the fittest“*, Bull. Math. Biol. **56**, 1–64 (1994). DOI `10.1007/BF02458289` / `10.1016/S0092-8240(05)80205-8` (Crossref OK); PNAS-Kurzfassung DOI `10.1073/pnas.91.2.757`.  
   - P. Dittrich & P. Speroni di Fenizio, *Chemical Organisation Theory*, Bull. Math. Biol. **69**, 1199–1231 (2007). DOI `10.1007/s11538-006-9130-8` (Crossref OK).  

2. **Kernformel (COT — anerkannte mathematische Teil-Operationalisierung)**  
   Eine Menge \(O\) von Spezies ist eine **Organisation**, wenn sie  
   - **abgeschlossen** ist: Reaktionen mit Edukten in \(O\) erzeugen keine Spezies außerhalb \(O\);  
   - **selbsterhaltend** ist: es existiert ein strikt positiver Fluss, der alle Spezies in \(O\) erhält.  

3. **(a)/(b) und Ehrlichkeit**  
   - **Klassische Autopoiesis (Maturana/Varela)** inkl. topologischer Membran/Randproduktion: **keine** allgemein anerkannte, kleine, handprüfbare Formel gefunden, die Astra-tauglich an einen Baustein andockt → **ehrliches „nichts Vollständiges zitierfähig“** für den historischen Begriff.  
   - **Teil-Operationalisierung** existiert: COT (und Fontana–Buss-Selbstwartung ohne Membran). Das rechtfertigt eher **(b) Kandidat neuer Baustein** `organization`/`autopoietic_closure` **oder** vorsichtige Erweiterung von `membership`/`closure` — **ohne** Autopoiesis mit Viability/Thermo gleichzusetzen.

4. **Mini-Beispiel (COT)**  
   Spezies \(\{A,B\}\), Reaktionen \(A\to B\), \(B\to A\): abgeschlossen und selbsterhaltend → Organisation. \(\{A\}\) allein mit derselben Menge: nicht selbsterhaltend, falls \(A\to B\) \(B\) erzeugt und \(B\notin\{A\}\). Handprüfbar.

5. **Aufwand:** COT-Checker **klein–mittel**; „volle Autopoiesis“ **nicht empfohlen**.

---

### C3. Strukturelle Kopplung als Mathematik (Pecora & Carroll)

1. **Quelle**  
   L. M. Pecora & T. L. Carroll, *Synchronization in chaotic systems*, Phys. Rev. Lett. **64**, 821–824 (1990).  
   DOI: `10.1103/PhysRevLett.64.821` (Crossref OK).

2. **Kernformel**  
   Master–Slave: Drive \(x\), Response \(z\). Variationsgleichung längs der Response:
   \[
   \delta\dot z = D_z H\bigl(y(t),z(t)\bigr)\,\delta z.
   \]
   **Bedingung:** alle bedingten Lyapunov-Exponenten (CLE) \(<0\) ⇒ asymptotische Synchronisation \(z(t)\to x(t)\) (bzw. auf dem Sync-Manifold).

3. **(a) oder (b)?**  
   **(a) Erweiterung von `coupling`** (`PairwiseCoupling` / master–slave-Drive). Formel-zu-Formel: Kopplungsterm + CLE-Kriterium. Das ist eine mathematische Fassung **generalisierter Synchronisation**, nicht Luhmann-Soziologie — ehrlich als solche labeln.

4. **Mini-Beispiel**  
   Skalar: Drive-Linearisierung \(\lambda=0.5\), Kopplungsstärke \(K=1\) ⇒ CLE \(\approx\lambda-K=-0.5<0\) ⇒ Sync. Handprüfbar.

5. **Aufwand:** **klein–mittel**.

---

### C4. Early-Warning / kritisches Verlangsamen

1. **Quellen**  
   - M. Scheffer et al., *Early-warning signals for critical transitions*, Nature **461**, 53–59 (2009). DOI `10.1038/nature08227` (Crossref OK).  
   - H. Held & T. Kleinen, *Detection of climate system bifurcations by degenerate fingerprinting*, Geophys. Res. Lett. **31**, L23207 (2004). DOI `10.1029/2004GL020972` (Crossref OK) — schärfere Formel.  
   - V. Dakos et al., PNAS **105**, 14308–14312 (2008). DOI `10.1073/pnas.0802430105` (Autokorrelation vor Klimasprüngen).

2. **Kernformel**  
   Nahe einer Bifurkation: führender Eigenwert \(\lambda\to 0^-\). Für AR(1)/Ornstein–Uhlenbeck:
   \[
   \rho_1 = e^{\lambda\,\Delta t}\;\xrightarrow{\lambda\to 0^-}\; 1,
   \]
   und Varianz \(\propto 1/|\lambda|\) steigt. Scheffer et al. fassen steigende Varianz/Autokorrelation als Early-Warning.

3. **(a) oder (b)?**  
   **(a) Erweiterung von `dynamics`** (an `recovery_rate_from_relaxation` / Spektrum) — optional Indikator-Pipeline nahe `identifiability`, aber **eine** primäre Anbindung an `dynamics`.  
   **Harte Abgrenzung:** Das ist ein **Indikator** kritischen Verlangsamens, **keine** Wiederauflage von \(\beta\equiv\mathrm{Stabilität}\) und keine Layer-übergreifende Konstante.

4. **Mini-Beispiel**  
   \(\lambda=-0.1\), \(\Delta t=1\): \(\rho_1\approx 0.9048\); \(\lambda=-0.01\): \(\rho_1\approx 0.9900\) (näher an 1). Handprüfbar.

5. **Aufwand:** **klein**.

---

## Übersicht Bewertung (Agent B)

| ID | Thema | Spur | Anschluss | Aufwand | Status |
|----|-------|------|-----------|---------|--------|
| A1 | Fenichel/GSPT | A | `dynamics` | mittel | vorschlagen |
| A2 | Crooks FT | A | `thermo` | klein–mittel | vorschlagen |
| B1 | GENERIC↔NS | B | `coupling.check_generic_structure` | mittel (1D) | vorschlagen |
| B2 | Chapman–Enskog | B | `closure` \(PC=CQ\) | mittel | vorschlagen |
| C1 | Panarchy/Cusp | C | (a) `dynamics` | klein–mittel | vorschlagen (ohne V≡Panarchy) |
| C2 | Autopoiesis | C | Teil: COT (b); voll: **nichts** | — | ehrlich gespalten |
| C3 | Pecora–Carroll Sync | C | (a) `coupling` | klein–mittel | vorschlagen |
| C4 | Early-Warning CSD | C | (a) `dynamics` | klein | vorschlagen |

**Spur-C-Ehrlichkeit:** Einzig C2 (volle Autopoiesis) scheitert als komplette Astra-Formel; die COT-Teilfassung ist der einzige belastbare mathematische Rest.
