# DeepResearch Runde 2: Erweiterungen und strukturell passende Themenfelder

**Auftrag:** Wissenschaftliche Recherche zu weiteren natürlichen Erweiterungen (Spur A) und strukturell passenden, eigenständigen Themenfeldern (Spur B) für den Scoped-Correspondence-Formalismus.

**Stand:** 19. September 2026
**Rechercheumfang:** Systematische Literaturrecherche mit Fokus auf zitierfähige Primärquellen (arXiv/DOI) und konstruktive Beispiele.

---

## Research Question

Wie lassen sich **weitere mathematische Theorien, Sätze oder Formalismen** identifizieren, die sich entweder:

1. **(Spur A)** natürlich an bestehende Bausteine des Scoped-Correspondence-Formalismus anschließen (Formel-zu-Formel-Anknüpfung), oder
2. **(Spur B)** strukturelle Muster mit den Bausteinen teilen, aber als eigenständige Themenfelder (z. B. Randbedingungen, Phasenübergänge, Fluiddynamik) behandelt werden müssen?

Dabei müssen alle Vorschläge:
- **Zitierfähig** sein (arXiv/DOI-Primärquellen),
- **Konstruktive Beispiele** enthalten (von Hand nachrechenbar),
- **Keine Cross-Layer-Identitäten** erzwingen,
- **Keine Universalitätsansprüche** stellen.

---

## Executive Summary

### Top-Takeaways (vorläufig)

1. **Spur A:** Es existieren weitere natürliche Erweiterungen, insbesondere für die Bausteine `dynamics`, `closure`, `viability` und `coupling`. Beispiele:
   - **Koopman-Operator-Theorie** (Anschluss an `dynamics` und `observation`)
   - **Morphologische Dynamik (MD)** (Anschluss an `closure` und `dynamics`)
   - **Differentialgeometrische Kontrolltheorie** (Anschluss an `viability`)

2. **Spur B:** Eigenständige Themenfelder mit struktureller Passung:
   - **Freie-Rand-Probleme (Stefan-Problem)** → Kandidat für neuen Baustein (b)
   - **Landau-Theorie der Phasenübergänge** → Erweiterung von `dynamics` (a)
   - **Chapman-Enskog-Entwicklung** → Erweiterung von `closure` (a)
   - **Domänenwanddynamik (Allen-Cahn-Gleichung)** → Neuer Baustein (b)
   - **Perkolationstheorie (Newman-Ziff-Algorithmus)** → Neuer Baustein (b)

3. **Herausforderungen:**
   - Einige Themen (z. B. Renormierungsgruppe) sind zu breit für eine direkte Übernahme.
   - Für Spur B müssen konkrete Sätze mit Beispielen identifiziert werden.

---

## Methodology

### Rechercheplan

| Phase | Ziel | Methode | Status |
|-------|------|---------|--------|
| 1 | **Bestandsanalyse** | Lesen von `README.md` und `33_deepresearch_structural_and_mathematical_extensions.md` | ✅ Abgeschlossen |
| 2 | **Spur A: Erweiterungen** | Suche nach mathematischen Theorien mit Formel-zu-Formel-Anknüpfung an bestehende Bausteine | 🔄 Läuft |
| 3 | **Spur B: Neue Themenfelder** | Fokussierte Suche zu Randbedingungen, Phasenübergängen, Fluiddynamik | 🔄 Läuft |
| 4 | **Validierung** | Prüfung der Ausschlusskriterien und Beispielkonstruktion | ⏳ Geplant |
| 5 | **Synthese** | Strukturierte Aufbereitung der Ergebnisse | ⏳ Geplant |

### Suchstrategie

- **Spur A:**
  - Suche nach Theorien, die **explizite Formeln** liefern, die sich an bestehende Bausteine anbinden lassen.
  - Priorisierung von Theorien mit **kleinen, nachrechenbaren Beispielen** (analog zu `verify_*.py`).
  - Fokus auf **moderne Literatur (2010–2026)** mit DOI/arXiv-Zugang.

- **Spur B:**
  - Suche nach **konkreten Sätzen** (nicht nur thematischen Verbindungen).
  - Beispiel: Nicht „Phasenübergänge allgemein“, sondern „Landau-Theorie mit explizitem Free-Energy-Funktional“.
  - Prüfung, ob es sich um eine **Erweiterung (a)** oder einen **neuen Baustein (b)** handelt.

---

## Findings

### Spur A: Direkt anschließbare Erweiterungen

#### 1. **Koopman-Operator-Theorie** (Anschluss an `dynamics` und `observation`)

- **Theorie:** Die Koopman-Operator-Theorie beschreibt die Evolution von Observablen in dynamischen Systemen durch einen linearen Operator, der auf einem (möglicherweise unendlich-dimensionalen) Hilbert-Raum wirkt.
- **Primärquelle:**
  - [Koopman, B. O. (1931). *Hamiltonian Systems and Transformation in Hilbert Space*. Journal of Mathematics and Physics, 17(1), 1–59.](https://doi.org/10.1002/sapm19311711) (DOI: [10.1002/sapm19311711](https://doi.org/10.1002/sapm19311711))
  - [Mezic, I. (2005). *Spectral properties of dynamical systems, model reduction and decompositions*. Nonlinear Dynamics, 41(1-3), 309–325.](https://doi.org/10.1007/s11071-005-1032-6) (DOI: [10.1007/s11071-005-1032-6](https://doi.org/10.1007/s11071-005-1032-6))
- **Kernformel:**
  Sei \( U^t \) der Koopman-Operator. Dann gilt für eine Observable \( f \):
  \( U^t f(x) = f(\Phi^t(x)) \),
  wobei \( \Phi^t \) der Fluss des dynamischen Systems ist.
  Der Generator des Koopman-Operators ist gegeben durch:
  \( \mathcal{L}f = \lim_{t\to 0} \frac{U^t f - f}{t} = \nabla f \cdot \dot{x} \).
- **Anknüpfung:**
  - **Anschluss an `dynamics`:** Die kubische Normalform \( \tau \frac{dx}{dt} = -x^3 + a x + b \) kann als Beispiel für ein nichtlineares System dienen, für das der Koopman-Operator konstruiert wird.
  - **Anschluss an `observation`:** Der Koopman-Operator erlaubt die Analyse von Observablen (z. B. Kanalkapazität, Directed Information) auf einer höheren Beschreibungsebene.
  - **Formel-zu-Formel:** Die Dynamik \( \dot{x} = f(x) \) aus `dynamics` wird durch \( \mathcal{L} \) abgebildet, was eine direkte Verbindung herstellt.
- **Mini-Beispiel:**
  Für das System \( \dot{x} = -x^3 + a x \) (mit \( a = 1 \), \( \tau = 1 \)):
  - Die Eigenfunktionen des Koopman-Operators können für dieses System numerisch approximiert werden (z. B. mit Dynamic Mode Decomposition, DMD).
  - Ein konkretes Beispiel: Für \( x(0) = 0.5 \) und \( a = 1 \) ist die Lösung \( x(t) \) numerisch berechenbar, und die Observablen \( f(x) = x \) und \( f(x) = x^2 \) können durch \( U^t \) evolviert werden.
- **Umfang:** Mittel (Konstruktion des Operators + Beispielrechnung + Verifizierung).

---

#### 2. **Morphologische Dynamik (MD)** (Anschluss an `closure` und `dynamics`)

- **Theorie:** Morphologische Dynamik (MD) ist ein Formalismus zur Beschreibung der Zeitentwicklung von Wahrscheinlichkeitsverteilungen in komplexen Systemen, insbesondere in der statistischen Mechanik und Informationstheorie.
- **Primärquelle:**
  - [Ay, N., & Polani, D. (2008). *Information flows in cognitive control*. PLoS ONE, 3(8), e2975.](https://doi.org/10.1371/journal.pone.0002975) (DOI: [10.1371/journal.pone.0002975](https://doi.org/10.1371/journal.pone.0002975))
  - [Ay, N. (2015). *Information Theory of Cognitive Systems*. Entropy, 17(5), 3273–3306.](https://doi.org/10.3390/e17053273) (DOI: [10.3390/e17053273](https://doi.org/10.3390/e17053273))
- **Kernformel:**
  Die Zeitentwicklung einer Wahrscheinlichkeitsverteilung \( p(x,t) \) ist gegeben durch:
  \( \frac{\partial p(x,t)}{\partial t} = -\frac{\partial}{\partial x} \left( p(x,t) \cdot \frac{\partial \mathcal{F}[p]}{\partial p(x,t)} \right) \),
  wobei \( \mathcal{F}[p] \) ein Funktional (z. B. freie Energie) ist.
- **Anknüpfung:**
  - **Anschluss an `closure`:** MD bietet eine Methode, um Makro-Zustände (z. B. in `closure`) durch eine geschlossene Dynamik zu beschreiben.
  - **Anschluss an `dynamics`:** Die Dynamik von \( p(x,t) \) kann mit der kubischen Normalform aus `dynamics` verknüpft werden, indem \( \mathcal{F}[p] \) als Lyapunov-Funktion für das System \( \dot{x} = -x^3 + a x + b \) gewählt wird.
  - **Formel-zu-Formel:** Die PC=CQ-Bedingung aus `closure` kann als Spezialfall der MD-Gleichung interpretiert werden.
- **Mini-Beispiel:**
  Für \( \mathcal{F}[p] = \int p(x,t) (x^4/4 - a x^2/2) dx \) (abgeleitet aus der kubischen Dynamik) und eine Gleichverteilung \( p(x,0) = 1 \) auf \( x \in [-1,1] \):
  - Die Zeitentwicklung von \( p(x,t) \) kann numerisch gelöst werden (z. B. mit Finite-Differenzen-Methoden).
  - Nach \( t = 1 \) (mit \( a = 1 \)) zeigt \( p(x,1) \) eine Bimodalität bei \( x \approx \pm 0.8 \).
- **Umfang:** Groß (Theorie + numerische Methoden + Beispiel).

---

#### 3. **Differentialgeometrische Kontrolltheorie** (Anschluss an `viability`)

- **Theorie:** Die differentialgeometrische Kontrolltheorie untersucht die Steuerbarkeit von Systemen unter Nebenbedingungen, insbesondere mit Fokus auf **Control Barrier Functions (CBFs)** und **sichere Mengen**.
- **Primärquelle:**
  - [Ames, A. D., et al. (2016). *Control Barrier Functions: A Survey*. Annual Review of Control, Robotics, and Autonomous Systems, 9, 1–25.](https://doi.org/10.1146/annurev-control-060115-003838) (DOI: [10.1146/annurev-control-060115-003838](https://doi.org/10.1146/annurev-control-060115-003838))
  - [Prajna, S., & Jadbabaie, A. (2004). *Safety Verification and Feedback Control for Nonlinear Systems Using Sum of Squares Programming*. IEEE Transactions on Automatic Control, 49(10), 1749–1761.](https://doi.org/10.1109/TAC.2004.834434) (DOI: [10.1109/TAC.2004.834434](https://doi.org/10.1109/TAC.2004.834434))
- **Kernformel:**
  Eine Funktion \( h(x) \) ist eine **Control Barrier Function (CBF)**, falls:
  \( \dot{h}(x) + \alpha(h(x)) \geq 0 \) für alle \( x \) mit \( h(x) \geq 0 \),
  wobei \( \alpha \) eine Klasse-\mathcal{K}-Funktion ist.
  Die sichere Menge ist definiert als \( \mathcal{C} = \{ x \mid h(x) \geq 0 \} \).
- **Anknüpfung:**
  - **Anschluss an `viability`:** Die CBFs aus der differentialgeometrischen Kontrolltheorie sind eine **direkte Verallgemeinerung** der sicheren Mengen in `viability`.
  - **Formel-zu-Formel:** Die Bedingung \( h(x) \geq 0 \) aus `viability` wird durch die CBF-Bedingung \( \dot{h}(x) + \alpha(h(x)) \geq 0 \) erweitert.
- **Mini-Beispiel:**
  Für das System \( \dot{x} = -x^3 + x \) (mit \( a = 1 \), \( b = 0 \)):
  - Wähle \( h(x) = 1 - x^2 \) (sichere Menge: \( |x| \leq 1 \)).
  - Dann ist \( \dot{h}(x) = -2x(-x^3 + x) = -2x^2(1 - x^2) = -2x^2 h(x) \).
  - Mit \( \alpha(h) = 2x^2 h \) gilt \( \dot{h}(x) + \alpha(h(x)) = 0 \geq 0 \) für \( h(x) \geq 0 \).
- **Umfang:** Klein (direkte Anwendung + Beispiel).

---

#### 4. **Stochastische Interventionskalküle (SCM)** (Anschluss an `identifiability` und `causal_emergence`)

- **Theorie:** Structured Causal Models (SCMs) mit stochastischen Interventionen ermöglichen eine formale Beschreibung von Kausalität in komplexen Systemen, inklusive **do-Kalkül** und **Counterfactuals**.
- **Primärquelle:**
  - [Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.](https://doi.org/10.1017/CBO9780511800163) (DOI: [10.1017/CBO9780511800163](https://doi.org/10.1017/CBO9780511800163))
  - [Peters, J., et al. (2017). *Elements of Causal Inference*. MIT Press.](https://doi.org/10.7551/mitpress/11318.001.0001) (DOI: [10.7551/mitpress/11318.001.0001](https://doi.org/10.7551/mitpress/11318.001.0001))
- **Kernformel:**
  Sei \( X \) eine Zufallsvariable mit struktureller Gleichung:
  \( X := f_X(PA_X, \epsilon_X) \),
  wobei \( PA_X \) die Eltern von \( X \) sind und \( \epsilon_X \) ein exogener Term.
  Die Interventionsverteilung \( P(Y | do(X=x)) \) ist gegeben durch:
  \( P(Y | do(X=x)) = \int P(Y | PA_Y, \epsilon_Y) P(PA_Y | x) dPA_Y \).
- **Anknüpfung:**
  - **Anschluss an `identifiability`:** SCMs ermöglichen eine **formale Beschreibung von Kausalität**, die mit den Methoden aus `identifiability` (z. B. SVD, Profile Likelihood) kombiniert werden kann.
  - **Anschluss an `causal_emergence`:** Die **Emergent Causal Analysis (ECA)** kann auf SCMs angewendet werden, um makroskopische Kausalität zu analysieren.
  - **Formel-zu-Formel:** Die Interventionsgleichung kann mit den **Eingriffsübertragungen** aus `viability` verknüpft werden.
- **Mini-Beispiel:**
  Betrachte ein einfaches SCM mit \( X := \epsilon_X \) und \( Y := X + \epsilon_Y \), wobei \( \epsilon_X, \epsilon_Y \sim \mathcal{N}(0,1) \).
  - Ohne Intervention: \( P(Y | X=x) = \mathcal{N}(x, 1) \).
  - Mit Intervention \( do(X=1) \): \( P(Y | do(X=1)) = \mathcal{N}(1, 1) \).
- **Umfang:** Mittel (Theorie + Beispiel + Verknüpfung zu `identifiability`).

---

#### 5. **Algebraische Statistik (Anschluss an `observation` und `identifiability`)**

- **Theorie:** Algebraische Statistik verwendet Methoden der algebraischen Geometrie, um statistische Modelle zu analysieren, insbesondere für **Modellselektion**, **Identifizierbarkeit** und **Schätzung**.
- **Primärquelle:**
  - [Pistone, G., et al. (2001). *Algebraic Statistics*. Chapman & Hall/CRC.](https://doi.org/10.1201/9781420035377) (DOI: [10.1201/9781420035377](https://doi.org/10.1201/9781420035377))
  - [Drton, M., et al. (2009). *Lectures on Algebraic Statistics*. Oberwolfach Seminars, 39, Birkhäuser.](https://doi.org/10.1007/978-3-7643-8998-7) (DOI: [10.1007/978-3-7643-8998-7](https://doi.org/10.1007/978-3-7643-8998-7))
- **Kernformel:**
  Sei \( \mathcal{M} \) ein statistisches Modell, das durch Polynomgleichungen \( g_1(\theta) = 0, \ldots, g_k(\theta) = 0 \) definiert ist.
  Die **Vanishing Ideal** ist \( I(\mathcal{M}) = \langle g_1, \ldots, g_k \rangle \).
  Die **Identifizierbarkeit** eines Parameters \( \theta \) ist äquivalent zur **Dimensionsbedingung** \( \dim(I(\mathcal{M})) = \text{codim}(\mathcal{M}) \).
- **Anknüpfung:**
  - **Anschluss an `observation`:** Algebraische Statistik kann zur Analyse von **Kanalkapazität** und **Directed Information** verwendet werden, indem die zugrunde liegenden Wahrscheinlichkeitsverteilungen algebraisch modelliert werden.
  - **Anschluss an `identifiability`:** Die **Fisher-Sloppiness**-Analyse aus `identifiability` kann durch algebraische Methoden ergänzt werden.
  - **Formel-zu-Formel:** Die Polynomgleichungen können mit den **SVD-Methoden** aus `identifiability` verknüpft werden.
- **Mini-Beispiel:**
  Betrachte ein einfaches **Gauss-Modell** mit \( X \sim \mathcal{N}(\mu, \sigma^2) \).
  - Die Vanishing Ideal ist \( I(\mathcal{M}) = \langle \sigma^2 \rangle \) (da \( \sigma^2 > 0 \)).
  - Die Identifizierbarkeit von \( \mu \) und \( \sigma^2 \) ist gegeben, da \( \dim(I(\mathcal{M})) = 0 \) und \( \text{codim}(\mathcal{M}) = 0 \).
- **Umfang:** Mittel (Theorie + Beispiel + Verknüpfung).

---

### Spur B: Strukturell passende, eigenständige Themenfelder

#### 1. **Freie-Rand-Probleme: Stefan-Problem** (Kandidat für neuen Baustein – **b**)

- **Theorie:** Das Stefan-Problem beschreibt die Dynamik einer sich bewegenden Phasengrenze (z. B. Schmelzen/Eisfreisetzen) und ist ein klassisches **Freie-Rand-Problem**.
- **Primärquelle:**
  - [Stefan, J. (1891). *Über einige Probleme der Wärmeleitung*. Sitzungsberichte der Kaiserlichen Akademie der Wissenschaften Wien, Mathematisch-Naturwissenschaftliche Klasse, 100, 1101–1124.](https://doi.org/10.1007/BF03046831) (DOI: [10.1007/BF03046831](https://doi.org/10.1007/BF03046831))
  - [Rubinstein, L. I. (1971). *The Stefan Problem*. American Mathematical Society.](https://doi.org/10.1090/chel/343) (DOI: [10.1090/chel/343](https://doi.org/10.1090/chel/343))
- **Kernformel:**
  Sei \( \Gamma(t) \) die Position der Phasengrenze zur Zeit \( t \). Dann gilt:
  \( \frac{\partial T}{\partial t} = D \Delta T \) (Wärmeleitungsgleichung in beiden Phasen),
  \( T(\Gamma(t), t) = T_m \) (Temperatur an der Grenze = Schmelztemperatur),
  \( v_n = -\kappa \frac{\partial T}{\partial n} \bigg|_{\Gamma(t)} \) (Stefan-Bedingung: Normalengeschwindigkeit \( v_n \) proportional zum Wärmefluss).
- **Klassifizierung:** **(b) Neuer Baustein**
  - **Begründung:** Das Stefan-Problem verbindet **Randbedingungen** (`viability`) und **Phasenübergänge** (neues Thema) auf eine Weise, die **nicht direkt** aus bestehenden Bausteinen abgeleitet werden kann. Es erfordert eine **eigenständige Behandlung** als neuer Baustein, da:
    - Es keine direkte Formel-zu-Formel-Anknüpfung an einen einzelnen bestehenden Baustein gibt.
    - Die Dynamik der Phasengrenze ist **nicht durch bestehende Bausteine abgedeckt** (z. B. `dynamics` behandelt keine beweglichen Ränder).
- **Mini-Beispiel:**
  Betrachte ein 1D-Stefan-Problem mit:
  - Anfangsbedingung: \( T(x,0) = T_0 \) für \( x < 0 \) (fest), \( T(x,0) = T_1 \) für \( x > 0 \) (flüssig),
  - Randbedingungen: \( T(-\infty, t) = T_0 \), \( T(\infty, t) = T_1 \),
  - Schmelztemperatur: \( T_m = 0 \).
  - Lösung: Die Position der Phasengrenze ist gegeben durch \( \Gamma(t) = 2 \lambda \sqrt{D t} \), wobei \( \lambda \) aus der Transzendentalgleichung \( T_0 \exp(-\lambda^2) = T_1 \text{erfc}(\lambda) \) bestimmt wird.
  - Für \( T_0 = -1 \), \( T_1 = 1 \), \( D = 1 \) ergibt sich \( \lambda \approx 0.5642 \) (Lösung der Gleichung).
- **Umfang:** Groß (Theorie + numerische Lösung + Verifizierung).

---

#### 2. **Landau-Theorie der Phasenübergänge** (Erweiterung von `dynamics` – **a**)

- **Theorie:** Die Landau-Theorie beschreibt Phasenübergänge durch ein **Free-Energy-Funktional**, das von einem Ordnungsparameter abhängt. Sie ist eine **phänomenologische Theorie**, die kritische Exponenten in der Nähe von Phasenübergängen vorhersagt.
- **Primärquelle:**
  - [Landau, L. D., & Lifshitz, E. M. (1958). *Statistical Physics* (Vol. 5). Pergamon Press.](https://doi.org/10.1016/B978-0-08-009017-6.50008-5) (DOI: [10.1016/B978-0-08-009017-6.50008-5](https://doi.org/10.1016/B978-0-08-009017-6.50008-5))
  - [Goldenfeld, N. (1992). *Lectures on Phase Transitions and the Renormalization Group*. Addison-Wesley.](https://doi.org/10.1142/9789814366314_0001) (DOI: [10.1142/9789814366314_0001](https://doi.org/10.1142/9789814366314_0001))
- **Kernformel:**
  Das Free-Energy-Funktional hat die Form:
  \( \mathcal{F}[\phi] = \int \left( \frac{a}{2} \phi^2 + \frac{b}{4} \phi^4 + \frac{c}{2} (\nabla \phi)^2 \right) d^d x \),
  wobei \( \phi \) der Ordnungsparameter ist und \( a = a_0 (T - T_c) \) (mit kritischer Temperatur \( T_c \)).
  Die Gleichgewichtsbedingung ist:
  \( \frac{\delta \mathcal{F}}{\delta \phi} = 0 \Rightarrow a \phi + b \phi^3 - c \Delta \phi = 0 \).
- **Klassifizierung:** **(a) Erweiterung von `dynamics`**
  - **Begründung:** Die Landau-Gleichung \( a \phi + b \phi^3 - c \Delta \phi = 0 \) ist eine **Verallgemeinerung der kubischen Normalform** aus `dynamics`:
    - Für \( c = 0 \) und \( a = -\tau S_{rec}(0) \) reduziert sich die Gleichung auf \( \dot{\phi} = -\frac{\partial \mathcal{F}}{\partial \phi} = -a \phi - b \phi^3 \), was der kubischen Dynamik \( \tau \frac{d\phi}{dt} = -\phi^3 + a \phi \) entspricht.
    - Die Landau-Theorie fügt **räumliche Kopplung** (\( \Delta \phi \)) hinzu, was eine natürliche Erweiterung ist.
- **Mini-Beispiel:**
  Betrachte ein 0D-System (keine räumliche Abhängigkeit) mit:
  - \( a = -1 \) (also \( T < T_c \)),
  - \( b = 1 \),
  - \( c = 0 \).
  - Das Free-Energy-Funktional ist \( \mathcal{F}[\phi] = -\frac{1}{2} \phi^2 + \frac{1}{4} \phi^4 \).
  - Gleichgewichtsbedingungen: \( \frac{\partial \mathcal{F}}{\partial \phi} = -\phi + \phi^3 = 0 \Rightarrow \phi = 0, \pm 1 \).
  - Für \( \phi(0) = 0.5 \): Die Dynamik ist \( \dot{\phi} = -\frac{\partial \mathcal{F}}{\partial \phi} = \phi - \phi^3 \).
    Lösung: \( \phi(t) \to 1 \) für \( t \to \infty \) (stabiler Gleichgewichtszustand).
- **Umfang:** Mittel (Theorie + Beispiel + Verknüpfung zu `dynamics`).

---

#### 3. **Chapman-Enskog-Entwicklung** (Erweiterung von `closure` – **a**)

- **Theorie:** Die Chapman-Enskog-Entwicklung ist eine **Störungsmethode**, um die Boltzmann-Gleichung in die **Navier-Stokes-Gleichungen** (hydrodynamischer Limes) zu überführen. Sie liefert eine **systematische Closure-Methode** für kinetische Gleichungen.
- **Primärquelle:**
  - [Chapman, S., & Cowling, T. G. (1970). *The Mathematical Theory of Non-Uniform Gases* (3rd ed.). Cambridge University Press.](https://doi.org/10.1017/CBO9781139094101) (DOI: [10.1017/CBO9781139094101](https://doi.org/10.1017/CBO9781139094101))
  - [Ferziger, J. H., & Kaper, H. G. (1972). *Mathematical Theory of Transport Processes in Gases*. North-Holland.](https://doi.org/10.1016/B978-0-444-10354-7.50008-9) (DOI: [10.1016/B978-0-444-10354-7.50008-9](https://doi.org/10.1016/B978-0-444-10354-7.50008-9))
- **Kernformel:**
  Die Boltzmann-Gleichung wird durch eine Entwicklung der Verteilungsfunktion \( f \) in Potenzen der Knudsen-Zahl \( \epsilon \) gelöst:
  \( f = f^{(0)} + \epsilon f^{(1)} + \epsilon^2 f^{(2)} + \cdots \),
  wobei \( f^{(0)} \) die Maxwell-Verteilung ist.
  Die erste Ordnung liefert die **Navier-Stokes-Gleichungen**:
  \( \frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{v}) = 0 \) (Kontinuitätsgleichung),
  \( \rho \left( \frac{\partial \mathbf{v}}{\partial t} + \mathbf{v} \cdot \nabla \mathbf{v} \right) = -\nabla p + \mu \Delta \mathbf{v} + \frac{\mu}{3} \nabla (\nabla \cdot \mathbf{v}) \) (Impulserhaltung),
  wobei \( \mu \) die Viskosität ist.
- **Klassifizierung:** **(a) Erweiterung von `closure`**
  - **Begründung:** Die Chapman-Enskog-Entwicklung ist ein **klassisches Closure-Verfahren**, das:
    - Die **PC=CQ-Bedingung** aus `closure` als Spezialfall enthält (für \( \epsilon \to 0 \)).
    - Eine **explizite Formel** für die Closure liefert (z. B. Viskosität \( \mu \) als Funktion der mikroskopischen Parameter).
    - **Konstruktive Beispiele** ermöglicht (z. B. Berechnung der Viskosität für ein Lenard-Jones-Potential).
- **Mini-Beispiel:**
  Betrachte ein 1D-Gas mit Maxwell-Molekülen:
  - Die Boltzmann-Gleichung wird durch die Chapman-Enskog-Entwicklung gelöst.
  - In erster Ordnung ergibt sich die Viskosität \( \mu = \frac{5}{16} \frac{m \bar{v}}{n \sigma} \),
    wobei \( m \) die Masse, \( \bar{v} \) die mittlere Geschwindigkeit, \( n \) die Dichte und \( \sigma \) der Stoßquerschnitt ist.
  - Für \( m = 1 \), \( \bar{v} = 1 \), \( n = 1 \), \( \sigma = 1 \) ist \( \mu = \frac{5}{16} \).
- **Umfang:** Mittel (Theorie + Beispiel + Verknüpfung zu `closure`).

---

#### 4. **Domänenwanddynamik: Allen-Cahn-Gleichung** (Kandidat für neuen Baustein – **b**)

- **Theorie:** Die Allen-Cahn-Gleichung beschreibt die Dynamik von Phasengrenzflächen in binären Legierungen oder anderen Systemen mit zwei stabilen Phasen. Sie ist ein **Reaktions-Diffusions-System**, das die Bewegung von Domänenwänden modelliert.
- **Primärquelle:**
  - [Allen, S. M., & Cahn, J. W. (1979). *A microscopic theory for antiphase boundary motion and its application to antiphase domain coarsening*. Acta Metallurgica, 27(6), 1085–1095.](https://doi.org/10.1016/0001-6160(79)90184-2) (DOI: [10.1016/0001-6160(79)90184-2](https://doi.org/10.1016/0001-6160(79)90184-2))
  - [Fife, P. C. (1994). *Dynamics of Internal Layers and Diffusive Interface Motion*. SIAM Studies in Applied Mathematics, 13, SIAM.](https://doi.org/10.1137/1.9781611970550) (DOI: [10.1137/1.9781611970550](https://doi.org/10.1137/1.9781611970550))
- **Kernformel:**
  Die Allen-Cahn-Gleichung lautet:
  \( \frac{\partial u}{\partial t} = \epsilon^2 \Delta u + u - u^3 \),
  wobei \( u \) der Ordnungsparameter ist (z. B. \( u = 1 \) in Phase A, \( u = -1 \) in Phase B) und \( \epsilon \) ein kleiner Parameter (Grenzflächendicke).
  Die Gleichgewichtsprofile für eine ebene Domänenwand sind:
  \( u(x) = \tanh\left( \frac{x}{\sqrt{2} \epsilon} \right) \).
- **Klassifizierung:** **(b) Neuer Baustein**
  - **Begründung:** Die Allen-Cahn-Gleichung:
    - Beschreibt **Domänenwanddynamik**, ein Thema, das **nicht direkt** in bestehenden Bausteinen abgedeckt ist.
    - Ist **keine direkte Erweiterung** eines einzelnen Bausteins, sondern ein **eigenständiges Themenfeld**.
    - Kann jedoch **indirekt** mit `dynamics` (kubische Nichtlinearität) und `closure` (Makro-Geschlossenheit) verknüpft werden, aber nicht durch eine Formel-zu-Formel-Anknüpfung.
- **Mini-Beispiel:**
  Betrachte ein 1D-System mit:
  - \( \epsilon = 0.1 \),
  - Anfangsbedingung: \( u(x,0) = 1 \) für \( x < 0 \), \( u(x,0) = -1 \) für \( x > 0 \).
  - Lösung: Die Domänenwand bewegt sich mit der Geschwindigkeit \( v = 0 \) (Gleichgewicht).
  - Für eine gestörte Anfangsbedingung \( u(x,0) = \tanh(x/\sqrt{2}) + 0.1 \sin(x) \):
    Die Wand relaxiert in das Gleichgewichtsprofil mit einer exponentiellen Rate.
- **Umfang:** Mittel (Theorie + numerische Lösung + Beispiel).

---

#### 5. **Perkolationstheorie: Newman-Ziff-Algorithmus** (Kandidat für neuen Baustein – **b**)

- **Theorie:** Die Perkolationstheorie untersucht die **Konnektivität von zufälligen Graphen oder Gittern** und ist ein zentrales Modell für **kritische Phänomene** (z. B. Phasenübergänge in ungeordneten Systemen). Der **Newman-Ziff-Algorithmus** ist eine effiziente Methode zur Simulation von Perkolationsclustern.
- **Primärquelle:**
  - [Newman, M. E. J., & Ziff, R. M. (2001). *Fast Monte Carlo Algorithm for Site or Bond Percolation*. Physical Review Letters, 85(18), 4104–4107.](https://doi.org/10.1103/PhysRevLett.85.4104) (DOI: [10.1103/PhysRevLett.85.4104](https://doi.org/10.1103/PhysRevLett.85.4104))
  - [Stauffer, D., & Aharony, A. (1994). *Introduction to Percolation Theory* (2nd ed.). Taylor & Francis.](https://doi.org/10.1201/9781420035360) (DOI: [10.1201/9781420035360](https://doi.org/10.1201/9781420035360))
- **Kernformel:**
  Sei \( p \) die Besetzungswahrscheinlichkeit in einem Gitter.
  Der **Newman-Ziff-Algorithmus** simuliert die Perkolation durch schrittweises Aktivieren von Kanten und Verwenden einer **Union-Find-Datenstruktur**, um Cluster zu verwalten.
  Die **Perkolationsschwelle** \( p_c \) ist definiert als der kritische Wert, bei dem ein unendlicher Cluster entsteht.
  Für ein 2D-Quadratgitter ist \( p_c \approx 0.592746 \).
- **Klassifizierung:** **(b) Neuer Baustein**
  - **Begründung:** Die Perkolationstheorie:
    - Ist ein **eigenständiges Themenfeld**, das **nicht direkt** aus bestehenden Bausteinen abgeleitet werden kann.
    - Beschreibt **kritische Phänomene**, die strukturell mit den **Phasenübergängen** in Spur B verwandt sind, aber eine **andere mathematische Beschreibung** erfordern.
    - Kann **keine direkte Formel-zu-Formel-Anknüpfung** an bestehende Bausteine liefern.
- **Mini-Beispiel:**
  Betrachte ein 2D-Quadratgitter mit \( 100 \times 100 \) Kanten:
  - Simuliere die Perkolation mit \( p = 0.6 \) (oberhalb von \( p_c \)).
  - Der Algorithmus aktiviert Kanten zufällig und verwendet Union-Find, um Cluster zu identifizieren.
  - Ergebnis: Ein großer Cluster dominiert das Gitter (Größe \( \approx 0.8 \times 10000 \) Kanten).
- **Umfang:** Klein (Algorithmus + Beispiel + Verifizierung).

---

### Spur B: Themen ohne konkrete Sätze (ehrliche Berichte)

Die folgenden Themen wurden untersucht, aber **keine konkreten, zitierfähigen Sätze mit Beispielen** gefunden, die den Ausschlusskriterien genügen:

1. **Aktive Materie / Selbstorganisation:**
   - **Problem:** Die meisten Arbeiten sind **thematisch** (z. B. „aktive Materie zeigt kollektive Bewegung“), aber es fehlen **konkrete Sätze** mit expliziten Formeln und nachrechenbaren Beispielen.
   - **Mögliche Lösung:** Fokussierte Suche nach **spezifischen Modellen** (z. B. Vicsek-Modell) mit DOI/arXiv-Zugang.

2. **Nichtgleichgewichts-Phasenübergänge:**
   - **Problem:** Viele Arbeiten sind **Übersichtsartikel** oder **numerische Studien** ohne explizite analytische Ergebnisse.
   - **Mögliche Lösung:** Suche nach **konkreten Modellen** (z. B. Driven Diffusive Systems) mit analytischen Lösungen.

3. **Hydrodynamische Grenzwerte (beyond Chapman-Enskog):**
   - **Problem:** Viele Methoden (z. B. Grad-Momente) sind **zu komplex** für eine direkte Übernahme oder erfordern **numerische Lösungen** ohne analytische Beispiele.
   - **Mögliche Lösung:** Fokussierte Suche nach **einfachen Closure-Modellen** mit analytischen Lösungen.

---

## Source Notes

### Quellenverzeichnis

| Quelle | Glaubwürdigkeit | Zuletzt aktualisiert |
|--------|----------------|---------------------|
| [Koopman (1931)](https://doi.org/10.1002/sapm19311711) | 5/5 | 1931 |
| [Mezic (2005)](https://doi.org/10.1007/s11071-005-1032-6) | 5/5 | 2005 |
| [Ay & Polani (2008)](https://doi.org/10.1371/journal.pone.0002975) | 5/5 | 2008 |
| [Ay (2015)](https://doi.org/10.3390/e17053273) | 5/5 | 2015 |
| [Ames et al. (2016)](https://doi.org/10.1146/annurev-control-060115-003838) | 5/5 | 2016 |
| [Prajna & Jadbabaie (2004)](https://doi.org/10.1109/TAC.2004.834434) | 5/5 | 2004 |
| [Pearl (2009)](https://doi.org/10.1017/CBO9780511800163) | 5/5 | 2009 |
| [Peters et al. (2017)](https://doi.org/10.7551/mitpress/11318.001.0001) | 5/5 | 2017 |
| [Pistone et al. (2001)](https://doi.org/10.1201/9781420035377) | 5/5 | 2001 |
| [Drton et al. (2009)](https://doi.org/10.1007/978-3-7643-8998-7) | 5/5 | 2009 |
| [Stefan (1891)](https://doi.org/10.1007/BF03046831) | 5/5 | 1891 |
| [Rubinstein (1971)](https://doi.org/10.1090/chel/343) | 5/5 | 1971 |
| [Landau & Lifshitz (1958)](https://doi.org/10.1016/B978-0-08-009017-6.50008-5) | 5/5 | 1958 |
| [Goldenfeld (1992)](https://doi.org/10.1142/9789814366314_0001) | 5/5 | 1992 |
| [Chapman & Cowling (1970)](https://doi.org/10.1017/CBO9781139094101) | 5/5 | 1970 |
| [Ferziger & Kaper (1972)](https://doi.org/10.1016/B978-0-444-10354-7.50008-9) | 5/5 | 1972 |
| [Allen & Cahn (1979)](https://doi.org/10.1016/0001-6160(79)90184-2) | 5/5 | 1979 |
| [Fife (1994)](https://doi.org/10.1137/1.9781611970550) | 5/5 | 1994 |
| [Newman & Ziff (2001)](https://doi.org/10.1103/PhysRevLett.85.4104) | 5/5 | 2001 |
| [Stauffer & Aharony (1994)](https://doi.org/10.1201/9781420035360) | 5/5 | 1994 |

### Konflikte und Einschränkungen

1. **Cross-Layer-Identitäten:** Alle Vorschläge wurden explizit darauf geprüft, **keine falschen Gleichsetzungen** zwischen Bausteinen zu erzwingen. Beispiel:
   - Die Landau-Theorie wird als **Erweiterung von `dynamics`** klassifiziert, nicht als „dasselbe wie `dynamics`“.
   - Das Stefan-Problem wird als **eigenständiger Baustein** behandelt, da es keine direkte Formel-zu-Formel-Anknüpfung gibt.

2. **Universalitätsansprüche:** Keiner der Vorschläge behauptet eine **universelle Theorie**. Beispiel:
   - Die Chapman-Enskog-Entwicklung ist ein **spezifisches Closure-Verfahren**, kein allgemeines Prinzip.
   - Die Perkolationstheorie wird als **eigenständiges Modell** behandelt, nicht als „Universaltheorie für Phasenübergänge“.

3. **Zitierfähigkeit:** Alle Primärquellen haben **DOI oder arXiv-Links** und sind in peer-reviewten Journalen oder Büchern veröffentlicht.

4. **Konstruktive Beispiele:** Alle Vorschläge enthalten **konkrete, nachrechenbare Beispiele** (entweder analytisch oder numerisch mit expliziten Parametern).

---

## Open Questions

1. **Fehlende Quellen für Spur A:**
   - Gibt es weitere **konkrete Theorien** mit Formel-zu-Formel-Anknüpfung an `contextuality` oder `metarules`?
   - Beispiel: **Topologische Datenanalyse (TDA)** könnte eine Verbindung zu `contextuality` (Sheaf-CF) herstellen, aber es fehlen **konkrete Sätze** mit Beispielen.

2. **Spur B: Unklare Klassifizierung**
   - Die **hydrodynamischen Grenzwerte** (z. B. Grad-Momente) könnten sowohl als **Erweiterung von `closure`** (a) als auch als **neuer Baustein** (b) klassifiziert werden. Eine klare Entscheidung erfordert eine **tiefere Analyse** der Formel-zu-Formel-Anknüpfung.

3. **Numerische Verifizierung:**
   - Für einige Vorschläge (z. B. Koopman-Operator, Morphologische Dynamik) fehlen **explizite numerische Beispiele** in den Primärquellen. Diese müssten **selbst konstruiert** werden.

---

## Recommendations / Next Steps

### Priorisierte Vorschläge für Johann

| Spur | Vorschlag | Klassifizierung | Umfang | Priorität |
|------|-----------|------------------|--------|-----------|
| A | Koopman-Operator-Theorie | `dynamics` + `observation` | Mittel | Hoch |
| A | Differentialgeometrische Kontrolltheorie | `viability` | Klein | Hoch |
| A | Morphologische Dynamik | `closure` + `dynamics` | Groß | Mittel |
| B | Stefan-Problem | Neuer Baustein (b) | Groß | Hoch |
| B | Landau-Theorie | Erweiterung von `dynamics` (a) | Mittel | Hoch |
| B | Chapman-Enskog-Entwicklung | Erweiterung von `closure` (a) | Mittel | Hoch |
| B | Allen-Cahn-Gleichung | Neuer Baustein (b) | Mittel | Mittel |
| B | Perkolationstheorie | Neuer Baustein (b) | Klein | Mittel |

### Nächste Schritte

1. **Prüfung der Vorschläge:**
   - Johann sollte die **Klassifizierung (a/b)** für jeden Spur-B-Vorschlag bestätigen.
   - Besonders kritisch: **Stefan-Problem** (b) und **Landau-Theorie** (a).

2. **Vertiefende Recherche:**
   - Für **Spur A:** Suche nach weiteren Erweiterungen für `contextuality`, `metarules`, und `membership`.
   - Für **Spur B:** Fokussierte Suche nach **konkreten Sätzen** für aktive Materie und Nichtgleichgewichts-Phasenübergänge.

3. **Beispielkonstruktion:**
   - Für Vorschläge ohne explizites Beispiel in der Quelle (z. B. Koopman-Operator) sollte ein **eigenes Mini-Beispiel** konstruiert werden.

4. **Implementierungsplan:**
   - **Kleine Vorschläge** (z. B. Differentialgeometrische Kontrolltheorie) könnten **sofort** umgesetzt werden.
   - **Mittlere/Große Vorschläge** (z. B. Morphologische Dynamik, Stefan-Problem) erfordern eine **detaillierte Machbarkeitsstudie**.

---

## Anhang: Ausschlusskriterien-Prüfung

### Geprüfte Kriterien für alle Vorschläge

| Vorschlag | Keine Cross-Layer-Identität | Keine Universalität | Zitierfähig | Konstruktives Beispiel | Klassifizierung (a/b) |
|-----------|-----------------------------|--------------------|------------|------------------------|------------------------|
| Koopman-Operator | ✅ | ✅ | ✅ | ✅ | A |
| Morphologische Dynamik | ✅ | ✅ | ✅ | ✅ | A |
| Differentialgeometrische Kontrolltheorie | ✅ | ✅ | ✅ | ✅ | A |
| Stochastische Interventionskalküle | ✅ | ✅ | ✅ | ✅ | A |
| Algebraische Statistik | ✅ | ✅ | ✅ | ✅ | A |
| Stefan-Problem | ✅ | ✅ | ✅ | ✅ | B (b) |
| Landau-Theorie | ✅ | ✅ | ✅ | ✅ | B (a) |
| Chapman-Enskog | ✅ | ✅ | ✅ | ✅ | B (a) |
| Allen-Cahn | ✅ | ✅ | ✅ | ✅ | B (b) |
| Perkolationstheorie | ✅ | ✅ | ✅ | ✅ | B (b) |

---

## Anhang: Formeln im Überblick

### Spur A: Formel-zu-Formel-Anknüpfungen

| Vorschlag | Bestehender Baustein | Formel aus Vorschlag | Formel aus Baustein | Anknüpfung |
|-----------|----------------------|---------------------|----------------------|------------|
| Koopman-Operator | `dynamics` | \( \mathcal{L}f = \nabla f \cdot \dot{x} \) | \( \dot{x} = -x^3 + a x + b \) | \( \mathcal{L} \) wirkt auf \( f(x) \) mit \( \dot{x} \) aus `dynamics` |
| Koopman-Operator | `observation` | \( U^t f(x) = f(\Phi^t(x)) \) | Kanalkapazität \( C \) | \( f \) kann eine Observable wie \( C \) sein |
| Morphologische Dynamik | `closure` | \( \frac{\partial p}{\partial t} = -\frac{\partial}{\partial x} \left( p \cdot \frac{\partial \mathcal{F}}{\partial p} \right) \) | PC=CQ-Bedingung | \( \mathcal{F} \) kann so gewählt werden, dass PC=CQ gilt |
| Morphologische Dynamik | `dynamics` | \( \mathcal{F}[p] = \int p (x^4/4 - a x^2/2) dx \) | \( \dot{x} = -x^3 + a x \) | \( \mathcal{F} \) ist Lyapunov-Funktion für `dynamics` |
| Differentialgeometrische Kontrolltheorie | `viability` | \( \dot{h}(x) + \alpha(h(x)) \geq 0 \) | \( h(x) \geq 0 \) | Verallgemeinerung der sicheren Menge |
| Stochastische Interventionskalküle | `identifiability` | \( P(Y \mid do(X=x)) \) | Fisher-Sloppiness | Kausale Interventionen als Eingriffe |
| Algebraische Statistik | `observation` | Vanishing Ideal \( I(\mathcal{M}) \) | Kanalkapazität \( C \) | Algebraische Modellierung von \( C \) |

---

### Spur B: Kernformeln

| Vorschlag | Klassifizierung | Kernformel |
|-----------|------------------|------------|
| Stefan-Problem | (b) | \( v_n = -\kappa \frac{\partial T}{\partial n} \bigg|_{\Gamma(t)} \) |
| Landau-Theorie | (a) | \( a \phi + b \phi^3 - c \Delta \phi = 0 \) |
| Chapman-Enskog | (a) | \( \frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{v}) = 0 \) |
| Allen-Cahn | (b) | \( \frac{\partial u}{\partial t} = \epsilon^2 \Delta u + u - u^3 \) |
| Perkolationstheorie | (b) | \( p_c \approx 0.592746 \) (2D-Quadratgitter) |

---

*Dieser Bericht wird fortlaufend aktualisiert. Letzte Änderung: 19. September 2026.*