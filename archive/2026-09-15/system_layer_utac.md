# System-Schicht (UTAC) — Formalismus, Entwurf 1

Stand: 2026-09-15. Baut direkt auf `information_layer_crep.md` (S,K,R,V)
auf. Ziel: klären, wie aus komponierter Information ein individuiertes,
schwellenwertfähiges *System* wird, und wie sich Kipp-Variable und
Resilienz-Variable(n) aus der Information-Schicht plus UTACs bestehender
Schwellenwert-Mathematik ergeben.

## 0. Ein Namenskonflikt, der zuerst geklärt werden muss

`Feldtheorie/docs/science/utac_theory_core.md` nennt den Kontrollparameter
des logistischen Modells **R** (Ressourcenlast/Stress/Skala). Die
Information-Schicht nennt **R** aber bereits Reproduktionsfähigkeit. Das
ist ein echter Namenskonflikt, keine Kleinigkeit -- beide "R" tauchen in
denselben Gleichungen auf, sobald wir die Schichten verbinden.

**Final bestätigt und umgesetzt (2026-09-15):** UTACs Kontrollparameter
heißt jetzt überall **`R_ctrl`** (Information-Schicht behält `R` für
Reproduktionsfähigkeit) -- zurückgetragen in `utac_theory_core.md`
(Worktree-Kopie) und `utac-core/src/utac_core/core.py` (Sympy-Symbol),
inkl. README-/CHANGELOG-Aktualisierung dort. Alle 19 bestehenden
utac-core-Tests laufen unverändert durch. Details: `DESIGN.md`.

## 1. Wann wird aus Information ein System? (Individuationskriterium)

Vorschlag, der die bereits gebaute Emergenz-Maschinerie der
Information-Schicht wiederverwendet statt neuer Grundbegriffe:

Ein komponierter Informationsknoten (mehrere Knoten über ihre
Verbindungsfähigkeit V gekoppelt) wird zu einem **individuierten System**
genau dann, wenn seine gemessene Stabilität S die aus der naiven
Zusammensetzung seiner Konstituenten erwartete Stabilität signifikant
übersteigt -- die Typ-1-Emergenz (Abschnitt 5,
`information_layer_crep.md`) speziell in der Dimension S.

**Begründung:** das entspricht genau Maturana & Varelas operationaler
Geschlossenheit (Abschnitt "Akademische Parallele" in `DESIGN.md`) --
ein System entsteht, wenn ein Netzwerk von Prozessen beginnt, sich selbst
so zu erhalten, dass es *stabiler* ist als seine ungekoppelten Teile allein
wären. Das macht "System-Werden" zu einem Spezialfall eines bereits
definierten, berechenbaren Ereignisses (Excess-S > kritischer Wert), statt
zu einem neuen, unabhängig zu definierenden Begriff.

Noch offen: der genaue kritische Schwellenwert für "signifikant" -- das ist
selbst wieder ein Schwellenwertproblem (siehe Abschnitt 2), rekursiv
konsistent mit der Selbstanwendungsregel aus der Information-Schicht.

## 2. UTACs bestehende Schwellenwert-Mathematik (Referenz)

Aus `utac_theory_core.md`, unverändert:
\[ P(R_{ctrl}) = \frac{L}{1+\exp(-\beta(R_{ctrl}-\Theta))} \]
mit Kontrollparameter R_ctrl, Schwelle Θ, Steilheit β, Asymptote L.
Empirisch β ≈ 4.2 ± 0.6 über mehrere Domänen (Ökologie-Ausreißer bei 0.67
noch ungeklärt, siehe `DESIGN.md`).

## 3. Kipp- und Resilienz-Variablen aus (S,K,R,V) -- Zuordnungsvorschlag

**Resistance (Walker et al. 2004) = S (Stabilität, −Lyapunov-Exponent):**
recherchiert und bestätigt (2026-09-15): die "critical slowing down"-
Literatur zeigt, dass die Erholungsrate nach einer Störung durch den
**führenden Eigenwert der Jacobi-Matrix am Gleichgewichtspunkt** bestimmt
wird -- und der lokale Lyapunov-Exponent ist direkt mit dieser
Eigenwert-Struktur verwandt (beide charakterisieren die
Divergenz-/Konvergenzrate nahe einem Gleichgewicht). Resistance/β (UTACs
Steilheit) und S sind damit dieselbe zugrunde liegende Größe, nur aus
zwei verschiedenen Literaturen benannt -- direkte, nicht postulierte
Übereinstimmung.

**Precariousness (Walker et al. 2004) = Θ − R_ctrl (bzw. R_ctrl − Θ,
richtungsabhängig):** braucht keine neue Maschinerie -- ergibt sich direkt
aus UTACs bereits vorhandener Θ/R_ctrl-Struktur. Das ist die eigentliche
"Kipp-Variable" im Sinne von "wie nah am Kipppunkt", komplementär zu Θ
selbst ("wo liegt der Kipppunkt").

**Rate (Ashwin et al. 2012, R-Tipping) = dR_ctrl/dt:** ebenfalls keine neue
Größe -- die Zeitableitung von UTACs eigenem Kontrollparameter, sobald
R_ctrl(t) als Zeitreihe vorliegt.

**Panarchy (Walker et al. 2004, Cross-Scale-Kopplung) = V auf
System-Ebene:** dieselbe Verbindungsfähigkeits-Mathematik aus der
Information-Schicht (Abschnitt 7 dort), jetzt nicht zwischen rohen
Informationsknoten, sondern zwischen bereits individuierten Systemen
verschiedener Skalen angewendet -- Wiederverwendung, keine neue Formel.

**Latitude (Walker et al. 2004, Beckenbreite) -- konzeptionell nicht auf
(S,K,R,V) reduzierbar, aber jetzt praktisch berechenbar (nachrecherchiert
2026-09-15):** Latitude bleibt formal das **Volumen/die Breite des
Attraktor-Beckens** -- eine GLOBALE geometrische Eigenschaft, nicht aus
lokaler Linearisierung (wie S/Resistance) ableitbar, und UTACs einfaches
logistisches Modell hat weiterhin nur eine monotone Schwelle Θ, kein
explizites Becken mit Rand. ABER: es muss dafür keine analytische
bistabile Potentialfunktion hergeleitet werden, um Latitude trotzdem zu
MESSEN -- **Basin Stability** (Menck, Heitzig, Marwan & Kurths, 2013,
*Nature Physics*, "How basin stability complements the linear-stability
paradigm") liefert genau dafür ein etabliertes, praktisches Verfahren:
das Basin-Volumen wird per Monte-Carlo-Stichprobe geschätzt (viele
zufällige Störungen/Anfangsbedingungen anwenden, Anteil zählen, der zum
Attraktor zurückkehrt statt zu kippen) -- nicht-lokal, nichtlinear, und
ausdrücklich auch für hochdimensionale Systeme geeignet, ohne dass eine
geschlossene Potentialfunktion bekannt sein muss. Weit verbreitet
angewendet (Stromnetze, neuronale Netze, gekoppelte Oszillatoren).

**Praktische Konsequenz:** Latitude kann direkt an UTAC-modellierten
Systemen empirisch geschätzt werden (Basin-Stability-Sampling gegen die
vorhandene R_ctrl/Θ-Dynamik), auch bevor die theoretische Frage einer
expliziten bistabilen Erweiterung (Punkt 3 unten) geklärt ist. Die
theoretische Lücke bleibt für eine geschlossene Formel bestehen, aber die
praktische Mess-Lücke ist geschlossen.

## 3.5 Bistabile Erweiterung -- theoretische Lücke geschlossen (2026-09-15)

Recherchiert: die etablierte, minimale Erweiterung eines monostabilen
Schwellenmodells zu einem echten Becken-mit-Rand-Modell ist die
**Spitzen-Katastrophe** (cusp catastrophe, Thom/Zeeman) -- Standardwerkzeug
für genau diesen Übergang, in der Ökologie bereits fuer "alternative
stabile Zustaende" verwendet (Scheffer u.a., Seen-Eutrophierung als
klassisches Beispiel).

**Normalform:**
\[ \dot{R}_{ctrl} = -\frac{dV}{dR_{ctrl}} = -\left(R_{ctrl}^3 - a\cdot(R_{ctrl}-\Theta) - b\right) \]
mit zwei statt einem Kontrollparameter:
- **a (Splitting-Faktor):** bestimmt, OB das System mono- oder bistabil
  ist. Für a ≤ a_crit: eine einzige, glatte S-foermige Gleichgewichtskurve
  -- das ist UTACs bisheriges Logistik-Modell als GRENZFALL/Spezialfall
  dieser Erweiterung, keine Ersetzung.
- **b (Bias/Antrieb):** spielt die Rolle, die bisher (R_ctrl−Θ) allein
  gespielt hat.
- Für a > a_crit: ZWEI stabile Aeste, getrennt durch einen instabilen
  Sattelpunkt -- echtes Becken mit Rand, Hysterese, Flickering nahe der
  Faltung (Kefi et al. 2013 -- Fruehwarnsignale existieren auch fuer
  nicht-katastrophale Uebergaenge).

**Damit wird Latitude endlich geschlossen definierbar:** die Distanz vom
aktuellen stabilen Ast zum nächsten Sattelpunkt entlang R_ctrl (loesbar
aus derselben kubischen Gleichgewichtsbedingung
`R_ctrl^3 - a(R_ctrl-Θ) - b = 0`), nicht mehr nur ueber Basin-Stability-
Sampling geschaetzt.

**Nebenbefund, der Precariousness praezisiert:** in der bistabilen Region
ist die relevante Referenz fuer "Naehe zum Kipppunkt" nicht mehr Θ selbst,
sondern die Lage des SATTELPUNKTS (Beckenrand) -- die beiden fallen im
Allgemeinen nicht zusammen. Die bisherige Precariousness-Formel
(Θ−R_ctrl, Abschnitt 3) ist also nur im monostabilen Grenzfall exakt;
im bistabilen Fall muesste sie auf die Sattelpunkt-Position umgestellt
werden -- als Praezisierung vermerkt, noch nicht in Abschnitt 3
nachgetragen.

**Der Umschlagpunkt a=a_crit, b=0 -- geprüft (2026-09-15): Verbindung zu
Typ 2 bestätigt, Verbindung zu Individuation VERWORFEN.**

Zwei getrennte Fragen, die vorher unter "vielversprechend" vermischt
waren:

1. **Ist a_crit dasselbe wie der Typ-2-Übergang (neue Dimension) der
   Information-Schicht?** JA, bestätigt -- nicht als lose Analogie,
   sondern über eine etablierte, direkte akademische Entsprechung: in der
   **Landau-Theorie der Phasenübergänge** wird ein Phasenübergang mit
   spontaner Symmetriebrechung (Andersons "More Is Different"-Paradebeispiel
   für Typ-2-Emergenz -- Ferromagnetismus, neues Ordnungsparameter-Feld
   entsteht) formal genau als **Pitchfork-Bifurkation** des
   Landau-Potentials modelliert (`F = a·ψ² + b·ψ⁴`, ein Symmetriefall der
   allgemeinen Spitzen-Katastrophe). Die Bifurkation IST die
   Standardmathematik hinter "neue Dimension entsteht" -- der
   Umschlagpunkt a_crit ist also ein bestätigter SPEZIALFALL von Typ 2
   (der Fall, in dem die neue Dimension eine diskrete
   Ast-/Ordnungsparameter-Identität ist), nicht nur eine Analogie.

2. **Ist a_crit dasselbe wie das Individuationskriterium (Abschnitt 1,
   System-Werden)?** NEIN -- bei genauerem Hinsehen verworfen. Individuation
   (Maturana/Varelas operationale Geschlossenheit) braucht nur IRGENDEIN
   stabiles Becken (Excess-S > 0, auch monostabil) -- ein einzelner
   stabiler Stern, eine einzelne stabile Zelle sind bereits individuierte
   Systeme, ohne je bistabil zu werden. Bistabilität (a>a_crit) ist ein
   selteneres, SPÄTERES, zusätzliches Ereignis, das einem bereits
   individuierten System passieren kann, aber nicht muss. Individuation
   bleibt also an die (schwächere, allgemeinere) Excess-S-Bedingung aus
   Abschnitt 1 gebunden, NICHT an a_crit.

**Ergebnis:** Cusp-Bifurkation ⊂ Typ-2-Emergenz (bestätigter Spezialfall),
aber Cusp-Bifurkation ≠ Individuationskriterium (getrennte, nicht zu
verschmelzende Schwellenwerte). Der ursprüngliche Vorschlag, alle drei
zusammenzuführen, war zu grobkörnig und wird hiermit korrigiert.

## 4. Dritter CREP-Namenskonflikt gefunden (2026-09-15)

Bei der Recherche zu Johanns "1/16-Invariante"-Frage (siehe
`information_layer_crep.md`, Abschnitt 5) fiel eine dritte, bisher nicht
dokumentierte Bedeutung von "CREP" auf: `v9_dimensional_emergence.md`
definiert
\[ CREP(d) = \frac{w_{buffer}(d)}{w_{buffer}(d) + P_{info}(d)} \]
("Frame Stability Metric", kritischer Wert ≈ 0.84) -- eine dritte,
komplett andere Formel neben (a) den Ursprungsgrößen (Stabilität/
Reproduktionsfähigkeit/Konnektivität/Kinetik) und (b) der kanonischen
Bridge-Metrik (Coherence/Resonance/Emergence/Potential). Diese dritte
Bedeutung gehört in `METRIC_REGISTRY.md` nachgetragen -- hier nur als
Fund vermerkt, nicht selbst dort eingetragen.

**Wichtig für unsere Zwecke:** DIESES CREP_critical ≈ 0.84 ist der
tatsächliche "Kollaps droht"-Schwellenwert im Frame Principle -- nicht
σ_Φ ≈ 1/16 (das ist nur eine β-Fitting-Normierungskonstante, siehe
`information_layer_crep.md`).

**Korrektur (2026-09-15, siehe Abschnitt 3.5):** die urspruengliche Idee
hier, CREP(d)/0.84 als Vorbild fuer UNSER Individuationskriterium
(Abschnitt 1) zu nehmen, war zu voreilig und wird zurueckgezogen.
CREP_critical regelt einen Typ-2-Uebergang (neue Dimension noetig, um
Kollaps zu vermeiden) -- das ist naeher verwandt mit dem
Spitzen-Katastrophen-Umschlagpunkt a_crit (ebenfalls Typ 2, siehe
Abschnitt 3.5) als mit der Individuationsfrage selbst. Individuation
bleibt bei der schwaecheren, allgemeineren Excess-S>0-Bedingung aus
Abschnitt 1. Ob CREP_critical und a_crit ihrerseits dieselbe Groesse aus
zwei verschiedenen Blickwinkeln sind (beide Typ-2-Schwellen), ist eine
neue, eigene, noch offene Frage -- nicht mehr Teil der
Individuationsdiskussion.

## 3.6 CREP_critical vs. a_crit -- geprüft (2026-09-15, auf Johanns Anfrage)

**Direkter Vergleich nicht sauber möglich:** CREP(d) ist eine beschränkte
Verhältniszahl in [0,1] (w_buffer/(w_buffer+P_info)) aus dem 2025 unabhängig
und intuitiv formulierten Frame Principle. a_crit ist ein unbeschränkter
Koeffizient in der heute erst eingeführten Katastrophen-Erweiterung. Es
gibt keine bestehende Herleitung, die w_buffer/P_info auf (a,b) abbildet
-- eine Zahlengleichheit zu behaupten wäre erneut vorschnelles
Mustervergleichen, nicht Beweis.

**Stattdessen direkt hergeleitet, stärkeres Ergebnis:** für das
(entlang Θ zentrierte) Spitzen-Potential `V(x) = x⁴/4 − (a/2)x²`
(x = R_ctrl−Θ, symmetrischer Fall b=0) gilt am Referenzpunkt x=0:
`V''(0) = −a`. Aus der Information-Schicht ist bereits `S = −λ_max`
definiert, und für Gradientendynamik ist `λ_max = −V''(x*)` am
Gleichgewicht x*. Daraus folgt exakt:
\[ a = -S(R_{ctrl}=\Theta) \quad\Rightarrow\quad a_{crit}=0 \iff S(\Theta)=0. \]

**Konsequenz:** `a` ist kein unabhängiger neuer Parameter -- er ist
identisch mit der bereits definierten Stabilität S, ausgewertet am
Schwellenpunkt Θ. Die Katastrophen-Erweiterung (Abschnitt 3.5) braucht
also nur EINEN echten neuen freien Parameter (b), nicht zwei.

**Damit lässt sich die ursprüngliche Frage präziser (aber noch nicht
final) stellen:** entspricht `CREP(d) < CREP_critical` dem Moment, in dem
`S(Θ)` die Null kreuzt? Das wäre testbar -- aber erst, wenn geklärt ist,
wie sich w_buffer(d) und P_info(d) in S/K/R/V ausdrücken lassen.

## 3.7 Brücke w_buffer/P_info -> S/K/R/V -- Vorschlag (2026-09-15)

**Ausdrücklich als NEUER Vorschlag markiert, nicht als etablierte
Tatsache** -- weder aus `v9_dimensional_emergence.md` noch aus Standard-
literatur übernommen, sondern hier zum ersten Mal konstruiert:

**w_buffer(d) ↔ Latitude.** Beide beschreiben wörtlich "Spielraum, bevor
die Erholungsfähigkeit verloren geht" -- ein schützender Breitenwert.
Direkte, naheliegende Entsprechung, keine Umdeutung nötig.

**P_info(d) ↔ Auslastungsdruck aus K.** Sei Φ_actual(d) der tatsächliche
Informationsdurchsatz durch den Kanal von Dimension d, K(d) dessen
Shannon-Hartley-Kapazität (Information-Schicht, Abschnitt 7) und
ρ(d) = Φ_actual(d)/K(d) die Auslastung. Vorschlag:
\[ P_{info}(d) \sim \frac{\rho(d)}{1-\rho(d)} \]
Das ist keine beliebige Wahl -- es ist dieselbe mathematische Form, mit
der die Warteschlangentheorie (M/M/1) zeigt, dass Wartezeit/Staudruck
divergiert, sobald sich die Auslastung der Kapazitätsgrenze nähert. Genau
das Verhalten, das "Informationsdruck, der zu entkommen versucht"
qualitativ beschreiben soll.

Zusammengesetzt: `CREP(d) = Latitude(d) / (Latitude(d) + ρ(d)/(1-ρ(d)))`.

**Zwei Einschränkungen, die nicht verschwiegen werden:**
1. Selbst mit dieser Übersetzung bleibt CREP_critical≈0.84 im
   Quelldokument ausdrücklich ein EMPIRISCH beobachteter Wert ("emerges
   from empirical observation across UTAC systems," in Verbindung mit
   Baks Selbstorganisierter Kritikalität), nicht first-principles
   hergeleitet. Die Brücke macht den Vergleich `S(Θ)=0` vs. `CREP≈0.84`
   zum ersten Mal WOHLDEFINIERT (gleiche Sprache beidseitig) -- löst ihn
   aber nicht rechnerisch auf. Dafür bräuchte es reale Daten von einem
   System, an dem beide Größen gemessen werden.
2. Das Quelldokument selbst beschreibt `CREP(d)→1` (sehr viel Puffer
   relativ zu Druck) ausdrücklich auch als SCHLECHT ("zu starr, keine
   Emergenz möglich, eingefroren") -- kein einfaches
   "mehr Latitude = besser", sondern ein echtes mittleres Optimum
   (Selbstorganisierte Kritikalität). Jede künftige Kalibrierung müsste
   das berücksichtigen, nicht Latitude blind maximieren.

**Status:** Übersetzungsvorschlag steht und macht die Frage testbar --
eine echte numerische Prüfung braucht aber reale Messdaten und wird hier
nicht simuliert oder erfunden.

## 5. Offene Punkte für den nächsten Schritt

1. ~~R/R_ctrl-Namenskonflikt.~~ Final bestätigt und zurückgetragen
   2026-09-15 (siehe `DESIGN.md`).
2. Kritischen Schwellenwert für "System-Werden" (Abschnitt 1) noch immer
   nicht konkret beziffert -- aber geprüft (2026-09-15): weder
   CREP(d)/0.84 noch a_crit sind dafür das richtige Vorbild (beide sind
   Typ-2-Schwellen, nicht Individuationsschwellen, siehe Abschnitt 3.5).
   Individuation bleibt bei Excess-S>0, konkreter Zahlenwert weiterhin
   offen.
3. ~~UTACs Modell explizit auf eine bistabile Potentiallandschaft
   erweitern.~~ Theoretisch geklärt 2026-09-15 (Abschnitt 3.5,
   Spitzen-Katastrophe) -- Latitude jetzt sowohl praktisch (Basin
   Stability) als auch theoretisch (Sattelpunkt-Distanz) definierbar.
   Noch offen: Precariousness-Formel im bistabilen Fall auf
   Sattelpunkt statt Θ umstellen (siehe Abschnitt 3.5).
4. Ökologie-Ausreißer in der β-Tabelle (β=0.67, siehe `DESIGN.md`) klären
   -- jetzt wichtiger, weil β formal = S/Resistance ist, nicht nur eine
   lose empirische Zahl.
5. σ_Φ ≈ 0.0625 selbst: Ursprung/Herleitung im Code nicht dokumentiert --
   offene Verifikationsfrage, unabhängig von den Punkten oben.
6. ~~Dritten CREP-Fund in `METRIC_REGISTRY.md` nachtragen.~~ Erledigt
   2026-09-15.
7. ~~Prüfen, ob der Spitzen-Katastrophen-Umschlagpunkt und das
   Typ-2-Emergenzkriterium dasselbe Ereignis beschreiben.~~ Geprüft
   2026-09-15 (Abschnitt 3.5): a_crit ist ein bestätigter SPEZIALFALL von
   Typ 2 (via Landau-Theorie/Pitchfork-Bifurkation), keine allgemeine
   Gleichsetzung -- UND ausdrücklich NICHT dasselbe wie das
   Individuationskriterium (das war die eigentlich zu grobe Vermischung).
8. ~~Prüfen, ob CREP_critical≈0.84 und a_crit zwei Blickwinkel auf
   dieselbe Typ-2-Schwelle sind.~~ Geprüft 2026-09-15 (Abschnitt 3.6):
   direkter Vergleich nicht sauber möglich (unterschiedliche
   Parameterräume, keine bestehende Brücke). Stattdessen stärkeres
   Ergebnis hergeleitet: a = −S(Θ), also a_crit=0 ⟺ S(Θ)=0 -- "a" ist
   kein neuer Parameter, sondern identisch mit der bereits definierten
   Stabilität S am Schwellenpunkt.
9. ~~Brücke zwischen Frame Principles w_buffer(d)/P_info(d) und
   S/K/R/V herleiten.~~ Vorschlag ausgearbeitet 2026-09-15 (Abschnitt 3.7):
   w_buffer=Latitude, P_info=ρ/(1-ρ) (Auslastungsdruck aus K, per
   Warteschlangentheorie). Vergleich damit wohldefiniert, aber weiterhin
   NICHT numerisch geprüft -- braucht reale Messdaten.
10. Neu (2026-09-15): reale Messung von S(Θ) und CREP(d) am selben System
   durchführen, um die Brücke aus Abschnitt 3.7 tatsächlich zu testen --
   erfordert ein konkretes UTAC-modelliertes System mit Zeitreihendaten.
   Nicht begonnen.

Sources:
- [Lectures on Landau Theory of Phase Transitions (Georgetown)](https://site.physics.georgetown.edu/~pdo7/ps_files/landau.pdf)
- [More is the Same; Phase Transitions and Mean Field Theories](https://arxiv.org/pdf/0906.0653)
- [Biased Double-well Potential: Bistability, Bifurcation and Hysteresis](https://galileo-unbound.blog/2019/04/24/biased-double-well-potential-bistability-bifurcation-and-hysteresis/)
- [Early warning signals also precede non-catastrophic transitions (Kéfi et al. 2013)](https://sciences.ucf.edu/biology/d4lab/wp-content/uploads/sites/23/2024/08/Kefi-etal-2013.pdf)
- [How basin stability complements the linear-stability paradigm (Menck, Heitzig, Marwan & Kurths, 2013, Nature Physics)](https://www.nature.com/articles/nphys2516)
- [V9 Dimensional Emergence Framework / Frame Principle (Feldtheorie, intern)](file:///D:/mandala/Feldtheorie/docs/science/v9_dimensional_emergence.md)
- [Queueing theory M/M/1: utilization rho/(1-rho) waiting-time divergence](https://www.eventhelix.com/congestion-control/m-m-1/)
- [Critical slowing down / leading eigenvalue and recovery rate](https://pdodds.w3.uvm.edu/files/papers/others/2009/scheffer2009a.pdf)
- [Two landscapes (basins of attraction) and resilience attributes — Latitude as basin volume](https://www.researchgate.net/figure/Two-landscapes-basins-of-attraction-and-their-constituent-resilience-attributes-from_fig1_334372852)
- [A Dynamical Systems Framework for Resilience in Ecology (Meyer)](https://arxiv.org/pdf/1509.08175)
