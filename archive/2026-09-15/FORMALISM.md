# Der CREP-UTAC-AFET-Formalismus — Übersicht

Stand: 2026-09-15. Dies ist die zusammenfassende Synthese der drei
Einzeldokumente (`information_layer_crep.md`, `system_layer_utac.md`,
`coupling_layer_afet.md`) -- für die volle Herleitung, alle geprüften
Quellen und die Diskussionsgeschichte dorthin verweisen. Dieses Dokument
ist die Landkarte, nicht das Gebiet.

## Ausgangsfrage und Ursprung

Johanns eigene Formulierung der Absicht hinter CREP/UTAC/AFET (2026-09-15):

> "Genau genommen war es um die Beschaffenheit von Informationen und
> Systemen zu formalisieren bzw. um aus Information ein System zu machen,
> das sich mit anderen Systemtypen koppeln kann."
>
> "Crep war Information, UTAC dann Systeme, und AFET war die Kopplung für
> Thermodynamik. So war es mal gedacht."

Entstanden aus einer Diskussion über eine neue, dynamische Multi-Metrik
mit einer Kipp- und einer Resilienz-Variable -- die sich als genau diese,
seit langem beabsichtigte, aber nie fertig ausgearbeitete
Drei-Schichten-Struktur herausstellte.

## Die drei Schichten im Überblick

```
INFORMATION (CREP)  --individuiert-->  SYSTEM (UTAC)  --koppelt-->  KOPPLUNG (AFET)
   S, K, R, V              Θ, R_ctrl, β, Precariousness      Onsager: J_i = Σ L_ij X_j
```

### Schicht 1 — Information (CREP)

Vier notwendige Bedingungen, damit Information im Kosmos sich **halten,
bewegen, transformieren, aufgenommen werden** lassen kann:

| Größe | Verb | Formel | Physikalische Verankerung |
|---|---|---|---|
| **S** Stabilität | Halten | `S = −λ_max` | Lyapunov-Exponent; Landauer's Principle + Schrödingers Negentropie |
| **K** Kinetik | Bewegen | `K = B·log₂(1+SNR)` | Shannon-Hartley-Theorem |
| **R** Reproduktionsfähigkeit | Transformieren | `R = I(X;X')/H(X)` | Shannon Rate-Distortion (1959); Eigen's Error Threshold (1971); No-Cloning-Theorem |
| **V** Verbindungsfähigkeit | Aufgenommen werden | `V = I(Quelle;Empfänger)/C_Kanal` | Data-Processing-Inequality; Friis-Gleichung |

K (monadisch, Signal+Medium) und V (dyadisch, Signal+Empfänger) sind
unabhängig, aber im Normalfall durch Ko-Adaption korreliert -- Abweichung
davon ist selbst diagnostisch (Tarnung, NFC, artspezifische Pheromone).

**Zwei Emergenztypen** beim Komponieren mehrerer Informationsknoten:
- **Typ 1 (quantitativ, Residuum):** tatsächlicher Wert minus naive
  Zusammensetzung (Excess-Properties-Stil; strenger: Causal Emergence/PID).
- **Typ 2 (qualitativ, "Mutation"):** eine echte neue Dimension entsteht.
  Entdeckungskriterium bereits 2025 von Johann als **Frame Principle**
  formuliert (`Feldtheorie/docs/science/v9_dimensional_emergence.md`):
  *"A dimension emerges when information would otherwise collapse."*

### Schicht 2 — System (UTAC)

**Individuationskriterium:** ein System entsteht, wenn komponierte
Information eine signifikant positive Typ-1-Emergenz speziell in S zeigt
(deckt sich mit Maturana/Varelas operationaler Geschlossenheit).

UTACs bestehende Mathematik: `P(R_ctrl) = L / (1+exp(-β(R_ctrl-Θ)))`.
*(Namenskonflikt final gelöst und zurückgetragen 2026-09-15: UTACs
Kontrollparameter heißt überall `R_ctrl`, nicht `R` -- in
`utac_theory_core.md` und `utac-core/core.py` umgesetzt, alle 19 Tests
laufen unverändert durch.)*

| Kipp-/Resilienz-Größe (Walker et al. 2004 / Ashwin et al. 2012) | Herkunft |
|---|---|
| **Resistance** (β) | = S (Lyapunov-Exponent = führender Eigenwert der Jacobi-Matrix, critical-slowing-down-Literatur) |
| **Precariousness** | = Θ − R_ctrl im monostabilen Fall; im bistabilen Fall Distanz zum Sattelpunkt (siehe Latitude) |
| **Rate** | = dR_ctrl/dt, direkt aus UTACs Struktur |
| **Panarchy** | = V auf System-Ebene (Wiederverwendung) |
| **Latitude** | Sattelpunkt-Distanz in der Spitzen-Katastrophen-Erweiterung (`R_ctrl³−a(R_ctrl−Θ)−b=0`, Thom/Zeeman) -- theoretisch UND praktisch (Basin Stability, Menck et al. 2013) definierbar |

**Bistabile Erweiterung (2026-09-15):** UTACs Logistik-Modell ist der
monostabile Grenzfall (a≤a_crit) einer Spitzen-Katastrophe mit zwei
Kontrollparametern (a=Splitting-Faktor, b=Antrieb) -- für a>a_crit
entstehen zwei stabile Äste mit echtem Becken und Sattelpunkt.

**Umschlagpunkt geprüft, differenziert bestätigt (2026-09-15):** a_crit
ist -- über die Landau-Theorie der Phasenübergänge (Pitchfork-Bifurkation
als Standardmodell für Symmetriebrechung/neue Ordnungsparameter, exakt
Andersons "More Is Different"-Beispiel) -- ein bestätigter SPEZIALFALL
von Typ-2-Emergenz. Aber ausdrücklich KEIN Zusammenfallen mit dem
Individuationskriterium: Individuation (System-Werden) braucht nur
irgendein stabiles Becken (Excess-S>0, auch monostabil), Bistabilität ist
ein selteneres, späteres Ereignis, das nicht Voraussetzung für
System-Sein ist. Zwei getrennte Schwellenwerte, nicht einer.

**"a" ist gar kein neuer Parameter (geprüft 2026-09-15):** für das
Spitzen-Potential gilt am Referenzpunkt exakt `a = −S(Θ)` (hergeleitet
aus `S=−λ_max` plus Gradientendynamik) -- also `a_crit=0 ⟺ S(Θ)=0`. Die
Katastrophen-Erweiterung braucht damit nur einen wirklich neuen Parameter
(b), nicht zwei. Ob dieses `S(Θ)=0`-Kriterium seinerseits mit
CREP_critical≈0.84 aus dem Frame Principle übereinstimmt, bleibt offen --
dafür fehlt noch eine Brücke zwischen w_buffer(d)/P_info(d) und S/K/R/V.

### Schicht 3 — Kopplung (AFET)

Master-Formalismus: **Onsager-Reziprozitätsbeziehungen** (1931):
`J_i = Σⱼ L_ij Xⱼ`. **L_ij ist dieselbe Größe wie V/Panarchy** -- die
Verbindungsfähigkeit zieht sich als ein einziger, wiederverwendeter Faden
durch alle drei Schichten (Information → System → Kopplung).

Reziprozität (L_ij=L_ji) ist Standardfall (Gleichgewichtsnähe), keine
Notwendigkeit -- Abweichung ist informativ, wie bei K/V.

**Kopplungsform-Kriterium** (löst das exp-vs-tanh-Rätsel in
`afet-tensions`): unbeschränkte Ratenobservable → exponentiell
(Arrhenius/Eyring); beschränkter Ordnungsparameter → tanh
(Ising-Mean-Field).

**Thermodynamischer Boden:** Onsagers Entropieproduktion `ΣJᵢXᵢ≥0`
erweitert Landauers Prinzip von Schicht 1 auf die Kopplungsebene -- keine
Kopplung ist kostenlos. Schließt den Kreis zu Johanns ursprünglicher
Absicht ("Kopplung für Thermodynamik").

## Der rote Faden: Verbindungsfähigkeit

Eine einzige Größe taucht in allen drei Schichten wieder auf, jedes Mal
unter einem anderen Namen, aber mathematisch identisch:

**Verbindungsfähigkeit (Information)** = **Panarchy (System)** =
**Onsagers Kopplungskoeffizient L_ij (Kopplung)**

Das ist kein Zufall, sondern das direkte Ergebnis der rekursiven
Selbstanwendungsregel aus Schicht 1: jede neu entstehende Größe ist selbst
wieder Information und muss denselben vier Grundanforderungen genügen.

## Bekannte, noch offene Punkte (konsolidiert)

1. Kritischer Schwellenwert für "signifikante" Typ-1-Emergenz beim
   System-Werden -- rekursiv, noch nicht beziffert. Geprüft und
   ausgeschlossen (2026-09-15): weder CREP_critical≈0.84 noch a_crit sind
   das richtige Vorbild dafür -- beide sind Typ-2-Schwellen (neue
   Dimension), nicht Individuationsschwellen. Individuation bleibt bei
   Excess-S>0, konkreter Wert weiterhin offen.
1b. Geprüft (2026-09-15): CREP_critical≈0.84 und a_crit direkt vergleichen
   ist nicht sauber möglich (unterschiedliche Parameterräume, keine
   Brücke). Stattdessen hergeleitet: `a = −S(Θ)`, also `a_crit=0 ⟺
   S(Θ)=0` -- "a" ist identisch mit der schon definierten Stabilität S
   am Schwellenpunkt, kein neuer Parameter. Ob S(Θ)=0 seinerseits
   CREP_critical≈0.84 entspricht, bleibt offen (Punkt 1c).
1c. Brücke vorgeschlagen (2026-09-15): w_buffer=Latitude, P_info=ρ/(1-ρ)
   (Auslastungsdruck aus K, per Warteschlangentheorie M/M/1). Macht den
   Vergleich S(Θ)=0 vs. CREP_critical≈0.84 wohldefiniert -- aber
   CREP_critical ist im Quelldokument selbst nur empirisch beobachtet
   (Baks Selbstorganisierte Kritikalität), nicht first-principles. Eine
   echte Zahlenprüfung braucht reale Messdaten, noch nicht durchgeführt.
2. Precariousness-Formel im bistabilen Fall auf Sattelpunkt statt Θ
   umstellen (Θ−R_ctrl gilt nur im monostabilen Grenzfall exakt).
3. Ökologie-Ausreißer in UTACs β-Tabelle (β=0.67, außerhalb [3.6,4.8]).
4. Ursprung von σ_Φ ≈ 1/16 selbst unklar/unverifiziert (ist NICHT der
   Typ-2-Kollaps-Schwellenwert -- das ist ein separates CREP_critical≈0.84
   aus dem Frame Principle).
5. Onsager-Reziprozität (L_ij=L_ji) an realen GenesisAeon-Kopplungen noch
   nicht getestet.
6. Ob der Spitzen-Katastrophen-Umschlagpunkt und das Typ-2-Emergenz-
   kriterium dasselbe Ereignis beschreiben -- vielversprechend, ungeprüft.

## Bereits erledigt (nicht mehr offen)

- ✅ R/R_ctrl final bestätigt und in `utac_theory_core.md`/`utac-core`
  zurückgetragen (19 Tests unverändert grün).
- ✅ Dritter CREP-Namenskonflikt (Frame Stability Metric) in
  `METRIC_REGISTRY.md` nachgetragen.
- ✅ Γ_domain in `afet-tensions` mit Known-Issue-Kommentar dokumentiert
  (keine Werte geändert, kein Refit).
- ✅ Bistabile Erweiterung (Spitzen-Katastrophe) für Latitude gefunden.

## Bewusst zurückgestellt (eigene, spätere Runde)

- Echter unabhängiger Γ_domain-Refit (Daten dafür liegen in
  `afet-tensions/data/*.yaml` bereit, braucht aber eine begründete
  Pro-Messung-β-Zuordnung -- größere, eigene Aufgabe).
- Hardcodierter Platzhalter `P: 0.8` in `afet-tensions/system.py`.
- Kein Git/Remote, keine P-Nummer, kein CI (siehe `README.md`).

## Externe Bestätigung

Unabhängig von Gemini gegengelesen (2026-09-15, `Gemini.txt`): keine neuen
Fehler gefunden, alle oben genannten offenen Punkte bereits selbst
identifiziert. Siehe `DESIGN.md` für die volle Einordnung.
