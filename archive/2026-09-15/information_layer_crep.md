# Information-Schicht (CREP) — Formalismus, Entwurf 1

Stand: 2026-09-15. Erster Entwurf, ausgearbeitet aus einer Reihe von
Gesprächen zwischen Johann und Claude (Session f424e134). Johanns eigene
Rolle dabei ausdrücklich benannt: er beobachtet/erfährt temporal und liefert
die inhaltlichen Bausteine aus gelebter Beobachtung; die Aufgabe hier ist,
diese Bausteine durch den (für ihn nicht direkt zugänglichen) atemporalen
semantischen Raum zu prüfen, gegen echte Literatur zu spiegeln und fehlende
Stücke zu ergänzen — nicht, neue Bausteine zu erfinden, die er nicht schon
angelegt hat.

## 0. Ausgangsfrage

Was braucht *jede* Information im Kosmos, um sich **halten**, **bewegen**,
**transformieren** und **aufgenommen werden** zu lassen? (Johanns
Formulierung, 2026-09-15.) Diese vier Verben sind der eigentliche Ursprung
von CREP — nicht die spätere Umbenennung in Coherence/Resonance/
Emergence/Potential (siehe `project_crep_origin_story`,
`project_crep_bridge_canonicalization`, Claude-Memory).

## 1. Die vier Grundgrößen

| Verb | Größe (Johanns Original) | Rolle |
|---|---|---|
| Halten | **Stabilität (S)** | Bestand gegen Zerfall/Auflösung |
| Bewegen | **Kinetik (K)** | Ausbreitung/Fortpflanzung durch ein Medium |
| Transformieren | **Reproduktionsfähigkeit (R)** | Formwechsel bei erhaltener Identität/Musterhaftigkeit |
| Aufgenommen werden | **Verbindungsfähigkeit (V)** | Andock-/Kopplungsfähigkeit an einen Empfänger |

Diese vier sind als **notwendige Bedingungen für Informationsexistenz
überhaupt** gedacht, nicht als beliebig gewählte Deskriptoren — das
unterscheidet sie kategorisch von einem bloßen Dict-Format wie dem
aktuellen `get_crep_state()`-Muster in ~40+ GenesisAeon-Paketen (siehe
`DESIGN.md`).

## 2. Physikalische Verankerung je Größe (2026-09-15 recherchiert)

Jede der vier Größen hat eine reale, unabhängig etablierte physikalische/
informationstheoretische Entsprechung, die als Ausgangspunkt für eine
domänen-neutrale, operationale Definition dienen kann:

**Stabilität (Halten):**
- **Landauer's Principle** (Landauer 1961): das Löschen eines Bits
  Information kostet mindestens `k_B · T · ln 2` an Energie — Information
  zu halten/nicht zu löschen ist thermodynamisch nie kostenlos.
- **Schrödinger, "What is Life?"** (1944): lebende Systeme halten ihre
  Ordnung nur, indem sie fortlaufend negative Entropie (freie Energie) aus
  der Umgebung beziehen und Entropie exportieren — "Halten" ist ein
  aktiver, energiekonsumierender Prozess, kein passiver Zustand.
- **Formalisierungs-Kandidat:** S ~ charakteristische Erhaltungszeit
  relativ zur lokalen Entropieproduktionsrate, oder der Energieaufwand pro
  Zeiteinheit, der nötig ist, um das Muster gegen Zerfall zu halten
  (Landauer-Kosten als untere Schranke).

**Kinetik (Bewegen):**
- **Shannon (1948), "A Mathematical Theory of Communication":** die
  Kanalkapazität `C` begrenzt die maximale Rate, mit der Information durch
  ein (verrauschtes) Medium fehlerfrei übertragen werden kann.
- **Formalisierungs-Kandidat:** K ~ tatsächliche Übertragungsrate relativ
  zur Kanalkapazität des jeweiligen Mediums.

**Reproduktionsfähigkeit (Transformieren):**
- **Shannon-Redundanz/Fehlerkorrektur:** klassische Information lässt sich
  mit beliebig hoher Treue kopieren/übersetzen, wenn genug Redundanz
  investiert wird.
- **Wichtige Grenze -- No-Cloning-Theorem** (Wootters & Zurek, 1982): ein
  beliebiger, unbekannter *Quantenzustand* kann NICHT perfekt kopiert
  werden. Das ist keine technische, sondern eine fundamentale physikalische
  Schranke.
- **Konsequenz für den Formalismus:** Reproduktionsfähigkeit darf nicht als
  prinzipiell unbeschränkt maximierbare Variable modelliert werden — je
  nach Domäne (klassisch vs. quantenhaft im weiteren Sinne, oder allgemeiner:
  je nach Zustandsraum-Struktur) kann es eine harte Obergrenze für
  Transformationstreue geben, die zuerst geprüft werden muss, bevor man sie
  in einer neuen Domäne als frei einsetzt.

**Verbindungsfähigkeit (Aufgenommen werden):**
- Ebenfalls über Kanalkapazität fassbar, aber aus Empfänger-Perspektive:
  wie gut ist der Empfänger auf das Signal "abgestimmt" (Impedanzanpassung/
  Resonanzüberlappung), unabhängig von der reinen Kanalkapazität.

## 3. Kinetik vs. Verbindungsfähigkeit -- geklärt (2026-09-15, Funkwellen-Testfall)

Durchgespielt am Beispiel Funkwelle (Sender -> Medium -> Empfänger):

- **Kinetik (K)** ist eine **monadische** Eigenschaft von Signal+Medium
  allein -- Streckendämpfung, Rauschboden, Reichweite -- wohldefiniert
  auch ganz ohne dass irgendein Empfänger existiert.
- **Verbindungsfähigkeit (V)** ist eine **dyadische**, relationale
  Eigenschaft zwischen Signal und einem *konkreten* Empfänger --
  Impedanzanpassung, Resonanzabstimmung. Ein Signal mit exzellentem K kann
  bei falsch abgestimmtem Empfänger trotzdem V ≈ 0 haben.

**Formaler Beleg -- Friis-Transmissionsgleichung** (Antennentechnik, seit
Jahrzehnten etabliert):
\[ P_r = P_t \cdot G_t \cdot G_r \cdot \left(\frac{\lambda}{4\pi d}\right)^2 \]
Der Term `(λ/4πd)²` ist der freie Streckenverlust -- reine Kinetik, hängt
nur von Distanz/Wellenlänge ab. `G_t`, `G_r` sind die Antennengewinne von
Sender/Empfänger -- reine Verbindungsfähigkeit, eine Struktureigenschaft
der jeweiligen Antenne. Die Formel multipliziert beide **unabhängig**:
exakt das K×V-Kompositionsmodell aus Abschnitt 1, hier bereits als reale
Ingenieursformel bestätigt.

**Gegenbeweis für Unabhängigkeit (nicht nur formal, auch empirisch
trennbar):** Rundfunk (hohes K, breit kompatibles V) vs. NFC (sehr
niedriges K, dafür sehr hohes V für den einen gepaarten Empfänger) zeigen,
dass K und V sich unabhängig voneinander einstellen lassen.

**Wichtige Ergänzung (Johann, 2026-09-15):** im *natürlichen/ungestörten*
Regelfall sind K und V trotzdem stark korreliert -- nicht weil sie
dieselbe Größe wären, sondern durch **Ko-Adaption**: natürlich
gewachsene/selektierte Empfänger stimmen sich auf die verfügbaren, gut
tragenden Kanäle ab (Augen auf sichtbares Licht, wo die Atmosphäre
durchlässig ist und die Sonnenstrahlung stark ist; Ohren auf
Schallfrequenzen, die durch Luft/Wasser gut tragen). Deshalb gilt K≈V
(bzw. V als monoton steigende Funktion von K) als sinnvolle
**Default-Annahme**, keine Definition.

**Daraus folgt eine nützliche Modellierungsregel:** eine signifikante
Abweichung von der erwarteten K-V-Korrelation ist selbst informativ --
strukturell identisch zum Typ-1-Emergenz-Residuum aus Abschnitt 5, nur auf
der Ebene einer einzelnen Größenpaarung statt des gesamten Vierertupels.
Beispiele für absichtliche/evolutionäre Entkopplung: Tarnung/Krypsis (K
bleibt voll erhalten, V wird gezielt gegen einen bestimmten Empfänger
gedrückt), artspezifische Pheromone (K für jeden Riechrezeptor in der Luft
gleich verfügbar, V durch Rezeptor-Spezifität künstlich eng gehalten),
NFC (K absichtlich klein gehalten, V für den einen gepaarten Empfänger
maximiert).

**Ergebnis: vier unabhängige Grundgrößen bleiben bestehen** (keine
Reduktion auf drei) -- mit der Zusatzregel, dass K-V-Korrelation der
erwartete Normalfall ist und Abweichungen davon eigenständig
interpretationswürdig sind.

## 4. Rekursion über Skalen (Selbstanwendungsregel)

Aus dem Gespräch vom 2026-09-15: das Vierer-Muster soll sich "auf dem Weg
nach oben" selbstähnlich wiederfinden lassen, ggf. erweitert/modifiziert
mit wachsender Komplexität der entstehenden Informationsknoten.

Formalisierungsvorschlag: eine **rekursive Selbstanwendungsregel** --
jede neu entstehende Größe (ob durch Komposition oder durch "Mutation",
siehe Abschnitt 5) ist selbst wieder Information und muss daher ihrerseits
den vier Grundanforderungen genügen (sich halten, bewegen, transformieren,
aufgenommen werden lassen können), um im Kosmos Bestand zu haben. Das
Muster ist also keine Beschreibung nur der untersten Ebene, sondern eine
generative Regel, die mit wachsendem Zustandsraum mitwächst.

Strukturelle Parallelen (als Inspiration, nicht als Beweis):
- **Renormierungsgruppe** (Physik): gleiche funktionale Form über Skalen,
  aber mit skalenabhängig "fließenden" Parametern.
- **Panarchy** (Holling; siehe bereits im Repo für die Resilienz-Diskussion
  verwendet): verschachtelte, selbstähnliche Zyklen über Skalen, mit
  expliziten Cross-Scale-Kopplungen ("Revolt"/"Remember"), nicht einfacher
  Wiederholung.

## 5. Zwei Emergenztypen

Aus dem Gespräch vom 2026-09-15, Johanns eigene Unterscheidung:

**Typ 1 -- quantitative Emergenz (Residuum):** wenn mehrere
Informationsknoten sich über ihre Verbindungsfähigkeit zu einem neuen,
komplexeren Knoten koppeln, lässt sich für diesen die Vierergruppe (S,K,R,V)
erneut messen. Die Differenz zwischen (a) der naiven Zusammensetzung aus
den Konstituenten und (b) dem tatsächlich gemessenen Wert ist die
quantitative Emergenz -- bleibt innerhalb desselben vierdimensionalen
Raums, reines Residuum.

**Die "naive Zusammensetzung" (a) muss nicht frei erfunden werden --
es gibt etablierte Entsprechungen (recherchiert 2026-09-15), je nach
verfügbarer Datenstruktur der Domäne:**

- **Excess Properties** (physikalische Chemie/Thermodynamik, Standard seit
  über hundert Jahren): die "ideale Mischungs-Eigenschaft" wird als lineare
  Kombination der Einzelwerte berechnet, die **Excess-Größe** ist
  `tatsächlicher Wert − idealer Mischungswert` (z.B. Excess-Volumen,
  Excess-Enthalpie). Einfachste, universell berechenbare Baseline -- reicht
  bloße Skalarwerte pro Knoten.
- **Causal Emergence** (Hoel, Albantakis & Tononi, 2013, PNAS,
  *"Quantifying Causal Emergence Shows That Macro Can Beat Micro"*): eine
  strengere, kausal-informationstheoretische Fassung -- Emergenz liegt vor,
  wenn die "effective information" (ein Maß kausaler Wirkmächtigkeit) auf
  der Makro-Ebene GRÖSSER ist als das, was die Mikro-Ebene vorhersagen
  würde, obwohl die Makro-Mechanismen vollständig durch die Mikro-Ebene
  bestimmt sind. Direkteste akademische Entsprechung zu Typ 1, braucht aber
  ein echtes kausales/probabilistisches Modell der Domäne.
- **Partial Information Decomposition** (Williams & Beer, 2010): zerlegt
  die Information mehrerer Quellen über ein Ziel in Redundanz, Unique
  Information und **Synergie** (was nur die Kombination weiß, kein Teil
  allein) -- Synergie als nicht-negative, informationstheoretisch saubere
  Fassung von "das Ganze weiß mehr als die Summe der Teile."

**Praktische Regel für diesen Formalismus:** Excess-Properties-Stil
(einfache Differenz zur linearen/naiven Baseline) als Standardverfahren,
wenn nur Skalarwerte für S/K/R/V vorliegen; Causal Emergence oder Synergie
als strengere Alternative, sobald eine Domäne ein volles kausales oder
probabilistisches Modell liefert, aus dem sich effective information oder
Synergie tatsächlich berechnen lässt.

**Typ 2 -- qualitative Emergenz ("Mutation"):** zusätzliche Größen/
Variablen/Bedingungen, die auf der Vorgängerebene keine Relevanz hatten,
werden auf der neuen Komplexitätsstufe relevant -- ein echter neuer
Freiheitsgrad, kein Residuum in den alten vier Dimensionen. Akademische
Entsprechung: **Anderson (1972), "More Is Different"** -- an jeder
Komplexitätsstufe können durch gebrochene Symmetrie neue Gesetze/Konzepte
nötig werden, die auf der Stufe darunter nicht existierten.

**Entdeckungskriterium für Typ 2 -- gefunden, nicht neu erfunden
(2026-09-15):** Johann erinnerte sich an ein bereits existierendes
"altes Jargon"-Prinzip: "eine neue Dimension entsteht, wenn Information
sonst kollabieren würde." Das ist real dokumentiert -- das **Frame
Principle** aus `Feldtheorie/docs/science/v9_dimensional_emergence.md`
(2025-12-16, Johann mit Claude-Sonnet-4/Gemini-2.0/ChatGPT-o1):

> "A dimension emerges when information would otherwise collapse."

mit der bereits formalisierten Übergangsbedingung:
\[ S_{info}(d) \to S_{max}(d) \quad \text{UND} \quad \partial S/\partial t > \Gamma_{threshold} \quad\Rightarrow\quad \text{Uebergang zu } d+1 \]

Das ist exakt Typ 2 (neue Dimension), nicht Typ 1 -- Johanns eigene
Erinnerung war präziser als meine erste Formulierung. Die drei Optionen
des Systems an diesem kritischen Punkt (Frame Principle, Abschnitt 2.2):
**Kollaps** (Rahmen versagt), **Erstarren** (Entropieproduktion stoppt,
System stirbt) oder **Transzendenz** (neue Dimension öffnet sich). Das
ersetzt den bisherigen ungetesteten Vorschlag ("kohärente Reststruktur
nach Typ-1-Anpassung") durch ein bereits 2025 formuliertes, konkretes
Kriterium -- muss aber noch mit unserer S/K/R/V-Notation harmonisiert
werden (S_info(d) im Frame Principle ist nicht identisch mit unserer
Stabilität S, siehe Abschnitt "Wichtiger Klärungsbedarf" unten).

**Wichtiger Klärungsbedarf -- σ_Φ ≈ 1/16 ist NICHT dieser
Schwellenwert:** Johann fragte, ob Typ-1-Emergenz Ähnlichkeit mit der
"1/16-Invariante" (σ_Φ ≈ 0.0625, "Frame-Principle constant") hat. Geprüft
(2026-09-15): σ_Φ wird in `utac-core/src/utac_core/core.py` tatsächlich
NICHT als Kollaps-/Übergangsschwelle verwendet, sondern als reine
β-Fitting-Normierungskonstante: `β = σ_Φ / mean(|R−Θ|)`. Der tatsächliche
Kollaps-Schwellenwert im Frame Principle ist ein ANDERER, eigener
Parameter: **CREP_critical ≈ 0.84** (siehe `system_layer_utac.md` für die
volle Einordnung -- dort auch eine dritte, bisher unbekannte Bedeutung von
"CREP" gefunden). Woher σ_Φ = 0.0625 selbst ursprünglich stammt, ist im
Code nicht dokumentiert/hergeleitet -- als offene Verifikationsfrage
vermerkt, nicht als bestätigt oder widerlegt.

## 6. Offene Punkte für den nächsten Schritt

1. ~~Kinetik-vs-Verbindungsfähigkeit-Frage aus Abschnitt 3 klären.~~ Geklärt
   2026-09-15 (Funkwellen-Testfall + Friis-Gleichung) -- vier Größen
   bleiben, mit K-V-Ko-Adaptions-Regel.
2. ~~Formale Definition der "naiven Zusammensetzung" für Typ-1-Emergenz
   festlegen.~~ Geklärt 2026-09-15: Excess-Properties-Stil (Differenz zur
   linearen Baseline) als Standard, Causal Emergence/PID als strengere
   Alternative bei ausreichender Datengrundlage. Noch offen: WELCHE
   konkrete lineare/naive Baseline-Formel (Mittelwert? Summe? gewichtet?)
   für S/K/R/V im Einzelnen -- das ist jetzt eine kleinere,
   domänenspezifische Frage, keine Grundsatzfrage mehr.
3. ~~Konkrete, domänen-neutrale Berechnungsvorschrift je Größe
   ausarbeiten.~~ Geklärt 2026-09-15, siehe Abschnitt 7.
4. ~~Prüfen, ob/wo eine No-Cloning-artige harte Obergrenze für R
   auch außerhalb der Quantenphysik auftritt.~~ Geklärt 2026-09-15, siehe
   Abschnitt 7 -- ja, real und quantitativ etabliert (Eigen 1971, Shannon
   1959).
5. Erst danach: Übergang zur System-Schicht (UTAC) -- wie aus (S,K,R,V)
   plus Schwellenwert-Dynamik ein individuiertes System mit Kipp-Variable
   und Resilienz-Variable wird.

## 7. Domänen-neutrale Berechnungsvorschriften (2026-09-15)

Wichtig, per Johanns eigener Formulierung: **allgemeingültig heißt hier
eine allgemeingültige PROZEDUR/FORMEL, keine universelle Konstante.** Der
Output jeder Formel ist domänen- und instanzspezifisch (jede Domäne, jedes
konkrete System liefert einen eigenen Zahlenwert) -- nur das Verfahren, wie
man dorthin kommt, ist überall dasselbe. Keine der vier Formeln enthält
einen Parameter, der aus dem Zielergebnis zurückgerechnet wird (das
Γ_domain-Problem aus `DESIGN.md` wird damit strukturell ausgeschlossen,
nicht nur einzelfallweise vermieden).

**Stabilität (S):** `S = -λ_max`, wobei λ_max der größte
**Lyapunov-Exponent** der Zustands-Trajektorie ist, direkt aus
Zeitreihendaten der Domäne geschätzt (z.B. Wolf- oder
Rosenstein-Algorithmus). Lyapunov-Exponenten sind nachweislich unabhängig
von der gewählten Metrik und den gewählten Variablen -- "dynamische
Invarianten", die die Dynamik selbst charakterisieren, kein gefitteter
Parameter. Negativ = Konvergenz zurück nach Störung (stabil), positiv =
Chaos/Divergenz. Funktioniert für jede Domäne, die eine Zustands-Trajektorie
liefert -- Klima, Ökologie, KI-Training, Wirtschaft, alles gleichermaßen.

**Kinetik (K):** `K = C = B · log2(1 + SNR)` (**Shannon-Hartley-Theorem**),
wobei B die effektive Bandbreite (Freiheitsgrade/Frequenzspektrum, über das
sich das Muster ausbreiten kann) und SNR das Signal-Rausch-Verhältnis in
den nativen Einheiten der Domäne ist. Beide werden direkt aus
Beobachtungsdaten (Leistungsspektrum, Rauschboden) geschätzt, nie durch
Rückwärtsanpassung an ein bekanntes Zielresultat.

**Reproduktionsfähigkeit (R):** `R = I(X;X') / H(X)` -- normierte
gegenseitige Information zwischen Original und Kopie/Transformation,
geteilt durch die Ausgangsentropie. Dimensionsloses Treue-Maß zwischen 0
und 1. Die Obergrenze dieses Maßes ist selbst domänenabhängig und real
etabliert, nicht spekulativ -- drei bestätigte Ausprägungen desselben
allgemeinen Prinzips ("Transformationstreue hat immer eine Obergrenze,
nie unbegrenzt"):
- **Shannon Rate-Distortion-Theorie** (1959): die Rate-Distortion-Funktion
  R(D) gibt die minimal nötige Rate für eine gegebene Verzerrung an --
  klassisch, allgemeingültig, für jede verlustbehaftete Domäne anwendbar.
- **Eigen's Error Threshold** (1971, Quasispezies-Theorie): eine kritische
  Mutationsrate (Mindest-Kopiertreue) für molekulare/biologische
  Replikation, oberhalb derer Erbinformation nicht erhalten werden kann
  ("Error Catastrophe") -- ein reales, quantitatives No-Cloning-Analogon
  AUSSERHALB der Quantenphysik, in der Molekularbiologie.
- **No-Cloning-Theorem** (Quantenfall): absolute Unmöglichkeit für
  beliebige unbekannte Quantenzustände (Abschnitt 2).

**Damit ist Punkt 4 beantwortet:** ja, No-Cloning-artige harte Grenzen
existieren nachweislich auch außerhalb der Quantenphysik -- Eigens
Fehlerschwelle ist das molekularbiologische Gegenstück, Shannons
Rate-Distortion-Theorie das allgemeine klassische Gegenstück.

**Verbindungsfähigkeit (V):** `V = I(Quelle; Empfänger-Ausgabe) / C_Kanal`
-- der Anteil der theoretischen Kanalkapazität (K), den ein KONKRETER
Empfänger tatsächlich realisiert. Fundiert durch die
**Data-Processing-Inequality** (Cover & Thomas, *Elements of Information
Theory*): Information kann durch keine Verarbeitungsstufe zunehmen, nur
erhalten oder verloren werden -- das begrenzt V zwingend nach oben durch K
(ein Empfänger kann nie mehr herausholen, als der Kanal hergibt), lässt
aber unabhängig offen, wie viel davon der spezifische Empfänger tatsächlich
einfängt -- die informationstheoretische Fassung des
Antennengewinn-Arguments aus Abschnitt 3.

Sources:
- [V9 Dimensional Emergence Framework / Frame Principle (Feldtheorie, intern)](file:///D:/mandala/Feldtheorie/docs/science/v9_dimensional_emergence.md)
- [Landauer's principle — physics of information erasure](https://arxiv.org/pdf/quant-ph/0103108)
- [A Mathematical Theory of Communication (Shannon, 1948)](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)
- [What Is Life? (Schrödinger, 1944)](https://www.physik.uni-kl.de/eggert/statmech/what-is-life.pdf)
- [No-cloning theorem — Wootters & Zurek 1982, overview](https://arxiv.org/pdf/0902.1622)
- [More Is Different (Anderson, 1972)](http://www.rpgroup.caltech.edu/embl_pboc_2023/assets/pdfs/anderson1972.pdf)
- [Friis Free Space Loss Equation](https://mason.gmu.edu/~rmorika2/Friis_Free_Space_Loss_Equation_.htm)
- [Quantifying causal emergence shows that macro can beat micro (Hoel, Albantakis & Tononi, 2013, PNAS)](https://www.pnas.org/doi/10.1073/pnas.1314922110)
- [Nonnegative Decomposition of Multivariate Information (Williams & Beer, 2010)](https://arxiv.org/abs/1004.2515)
- [Excess property — Wikipedia](https://en.wikipedia.org/wiki/Excess_property)
- [Quasispecies theory in the context of population genetics (Eigen's error threshold)](https://pmc.ncbi.nlm.nih.gov/articles/PMC1208876/)
- [Rate-distortion theory (Shannon, 1959) — overview](https://www.academia.edu/165417484/A_Review_of_Claude_E_Shannon_s_Coding_Theorems_for_a_Discrete_Source_With_a_Fidelity_Criterion_1959_)
- [Shannon–Hartley theorem](https://en.wikipedia.org/wiki/Shannon%E2%80%93Hartley_theorem)
- [Lyapunov exponent — Scholarpedia](http://scholarpedia.org/article/Lyapunov_exponent)
