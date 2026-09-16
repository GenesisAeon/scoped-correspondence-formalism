# DESIGN.md -- crep-utac-afet-formalism

Stand: 2026-09-15.

## Ursprung dieses Ordners

Entstanden aus einer Diskussion über eine neue, dynamische Multi-Metrik
mit einer Kipp-Variable und einer Resilienz-Variable (sonst frei/dynamisch).
Im Gespräch stellte sich heraus, dass dies keine neue Idee ist, sondern
genau das, was CREP/UTAC/AFET von Anfang an sein sollten -- nur nie in
einem einzigen, konsistenten Dokument zusammengeführt.

Johanns eigene Formulierung der ursprünglichen Schichtung (2026-09-15,
verbatim): "Crep war Information, UTAC dann Systeme, und AFET war die
Kopplung für Thermodynamik. So war es mal gedacht."

Und zur davor gestellten Frage nach dem Zweck von CREP/UTAC/AFET
allgemein: "Genau genommen war es um die beschaffenheit von Informationen
und Systemen zu formalisieren bzw um aus Information ein System zu machen
das sich mit anderen systemtypen koppeln kann."

## Akademische Parallele (unabhängig recherchiert, 2026-09-15)

Eine Literaturprüfung im selben Gespräch fand eine strukturell sehr nahe
akademische Traditionslinie -- nicht als Beweis, dass CREP/UTAC/AFET
"richtig" sind, sondern als mögliches Vokabular/Gerüst für die
Neuausarbeitung:

- **Bateson** (1972, *Steps to an Ecology of Mind*): Information als "a
  difference that makes a difference" -- Minimalkriterium für die
  Informations-Schicht.
- **Maturana & Varela** (1972/1980, *Autopoiesis and Cognition*):
  operationale Geschlossenheit + Grenze = was aus Information ein
  individuiertes System macht. Deckt sich mit dem bestehenden
  semantic-map-Knoten `boundary_as_active_element`.
- **Luhmann**: strukturelle Kopplung -- wie operational geschlossene
  Systeme trotzdem mit andersartigen Systemen interagieren, ohne zu
  verschmelzen ("digitising analogue relations").

Quellen: siehe Konversationsverlauf 2026-09-15 (Claude Session f424e134),
WebSearch-Belege dort für alle drei Zitate.

## Bekannte Probleme in der bestehenden Basis (gefunden 2026-09-15)

Diese Probleme müssen im neuen Formalismus vermieden oder explizit
korrigiert werden -- nicht stillschweigend übernommen:

1. **Γ_domain-Zirkelbezug in `afet-tensions/src/afet_tensions/constants.py`:**
   ```python
   GAMMA_DOMAIN = math.log(H0_RATIO) / ((BETA_LOCAL - BETA_CMB) * SIGMA_PHI)
   ```
   Γ_domain wird algebraisch so gelöst, dass es exakt das bereits bekannte
   H₀-Verhältnis reproduziert. Die Kopplungs-*Form* (`H0_eff(β) = H0_ref ·
   exp(β·σ_Φ·Γ_domain)`) ist ein plausibler Kandidat für einen generischen
   Kopplungsterm; die *konkrete Kalibrierung* von Γ_domain in diesem Paket
   hat aber aktuell keinen unabhängigen Vorhersagewert für die
   Hubble-Tension selbst (sie ist per Konstruktion exakt). Die separaten
   Vorhersagen des Pakets (LIGO ω_RIG, Euclid-S₈-Steigung, DESI-BAO-
   Verschiebung) sind davon unberührt und bleiben unabhängig prüfbar.
   Verwandtes bereits dokumentiertes Muster: siehe
   `project_feldtheorie_compute_constrained_hallucination_root_cause`
   (Claude-Memory).
2. **Hardcodierter Platzhalter in `afet-tensions/system.py`,
   `get_crep_state()`:** `"P": 0.8` ist keine echte Übersetzung des
   Domänenzustands, sondern ein fester Wert -- bereits am 2026-08-05 im
   Rahmen der CREP-Bridge-Kanonisierung gefunden (Genesis-Blindtest), aber
   im Paket selbst bisher nicht behoben.
3. **UTAC-β-Tabelle, Ausreißer:** `Feldtheorie/docs/science/
   utac_theory_core.md` listet Ökologie mit β=0.67±0.13 -- außerhalb des
   dort selbst behaupteten "kanonischen Bands" [3.6, 4.8]. Nicht
   untersucht, ob das ein echter Gegenbeleg, ein Einheiten-/
   Normalisierungsproblem, oder einfach eine kleine Stichprobe ist.
4. **Zwei verschiedene Kopplungsformen im selben Paket:** `afet-tensions`
   nutzt `exp(...)` für H₀ und `tanh(...)` für S₈, ohne dass dokumentiert
   ist, ob das eine bewusste, prinzipielle Wahl ist (verschiedene
   Observablen brauchen verschiedene Kopplungskerne) oder zwei unabhängig
   gefittete Ad-hoc-Formen.

## Was bereits real und wiederverwendbar ist

- `utac-core` (P79, echtes PyPI-Paket): `σ(β(R−Θ))`, β-Fitting,
  Frame-Principle (σ_Φ≈0.0625), v_RIG. Die System-Schicht hat also schon
  eine echte, nicht-domänenspezifische Engine -- die größte Lücke liegt
  bei Information (CREP) und Kopplung (AFET), nicht bei System (UTAC).
- `utac_theory_core.md`, Abschnitt 4 ("Field coupling"): skizziert bereits
  einen generischen Kopplungsterm
  `Ṙ = J(t) + M[ψ,φ] − ζ(R)(R − σ(β(R−Θ)))` -- Ausgangspunkt für die
  Verallgemeinerung von AFETs Kopplung über Thermodynamik hinaus.

## Information-Schicht, Entwurf 1 (2026-09-15)

Siehe `information_layer_crep.md` für den vollen Entwurf. Kernpunkte:

- Ursprung sauber geklärt: die vier CREP-Ursprungsgrößen (Stabilität/
  Kinetik/Reproduktionsfähigkeit/Verbindungsfähigkeit) entsprechen den vier
  notwendigen Bedingungen, damit Information im Kosmos sich **halten,
  bewegen, transformieren, aufgenommen werden** lassen kann (Johann,
  2026-09-15) -- nicht willkürlich gewählt, sondern eine echte
  Vier-Verben-Struktur.
- Jede der vier Größen hat eine reale physikalische/informationstheoretische
  Verankerung gefunden (recherchiert 2026-09-15): Landauer's Principle +
  Schrödingers Negentropie (Stabilität), Shannons Kanalkapazität (Kinetik),
  Shannon-Redundanz mit einer harten Grenze durchs No-Cloning-Theorem
  (Reproduktionsfähigkeit), Kanalkapazität aus Empfänger-Sicht
  (Verbindungsfähigkeit).
- **Geklärt (2026-09-15, Funkwellen-Testfall):** Kinetik (K, monadisch --
  Signal+Medium allein) und Verbindungsfähigkeit (V, dyadisch -- Signal
  plus konkreter Empfänger) sind echte unabhängige Größen, nicht zwei
  Projektionen derselben Kanalkapazität. Beleg: die etablierte
  Friis-Transmissionsgleichung (`Pr = Pt·Gt·Gr·(λ/4πd)²`) trennt beide
  bereits als unabhängige, multiplizierte Faktoren; Rundfunk (hohes K,
  breites V) vs. NFC (niedriges K, sehr hohes V) zeigen die unabhängige
  Einstellbarkeit. Zusatzregel: im natürlichen/ungestörten Regelfall sind
  K und V durch Ko-Adaption korreliert (Sinnesorgane stimmen sich auf gut
  tragende Kanäle ab), Abweichungen davon (Tarnung, artspezifische
  Pheromone, NFC) sind selbst diagnostisch informativ -- strukturell wie
  ein Typ-1-Emergenz-Residuum, nur auf einer einzelnen Größenpaarung.
  Vier Grundgrößen bleiben bestehen.
- Zwei Emergenztypen festgehalten: Typ 1 (quantitatives Residuum,
  bleibt im 4D-Raum) und Typ 2 (qualitative "Mutation", echte neue
  Dimension, akademische Entsprechung: Anderson 1972 "More Is Different").
  Für Typ 2 gibt es einen vorgeschlagenen, aber ungetesteten
  Entdeckungstest (kohärente Reststruktur nach bestmöglicher
  Typ-1-Anpassung).
- **Geklärt (2026-09-15):** die "naive Zusammensetzung" für Typ-1-Emergenz
  muss nicht frei erfunden werden -- Excess Properties (Thermodynamik/
  Chemie, Standard: tatsächlicher Wert minus idealer Mischungswert) als
  einfache universelle Baseline; Causal Emergence (Hoel/Albantakis/Tononi
  2013, "macro can beat micro") und Partial Information Decomposition
  (Williams & Beer 2010, Synergie-Komponente) als strengere,
  informationstheoretische Alternativen, wenn eine Domäne ein echtes
  kausales/probabilistisches Modell liefert.
- Rekursions-/Selbstähnlichkeitsregel formuliert: jede neu entstandene
  Größe (Typ 1 oder Typ 2) ist selbst wieder Information und muss daher
  ihrerseits den vier Grundanforderungen genügen, um Bestand zu haben --
  das erklärt, warum das Muster sich über Skalen selbstähnlich
  wiederfinden lässt, obwohl der Zustandsraum wächst.
- **Geklärt (2026-09-15): domänen-neutrale Berechnungsvorschriften für
  alle vier Größen gefunden -- allgemeingültige PROZEDUREN, keine
  universellen Konstanten** (Johanns explizite Anforderung). Jede Formel
  liefert einen domänen-/instanzspezifischen Wert aus echten Beobachtungs-
  daten, nie einen zurückgerechneten Zielwert:
  - S = −λ_max (größter Lyapunov-Exponent der Trajektorie -- nachweislich
    metrik-/variablenunabhängig, eine "dynamische Invariante").
  - K = C = B·log2(1+SNR) (Shannon-Hartley), B und SNR aus
    Beobachtungsdaten der Domäne.
  - R = I(X;X')/H(X) (normierte gegenseitige Information), mit
    Obergrenze durch drei real etablierte Ausprägungen desselben
    Prinzips: Shannon Rate-Distortion-Theorie (1959, klassisch-allgemein),
    Eigen's Error Threshold (1971, molekularbiologisch -- ein echtes
    No-Cloning-Analogon AUSSERHALB der Quantenphysik), No-Cloning-Theorem
    (Quantenfall).
  - V = I(Quelle;Empfänger-Ausgabe)/C_Kanal, nach oben begrenzt durch K
    via Data-Processing-Inequality (Cover & Thomas).
  Damit sind die in diesem Dokument oben beschriebenen Probleme 1
  (Γ_domain-Zirkelbezug) für die Information-Schicht strukturell
  ausgeschlossen, nicht nur einzelfallweise vermieden.

## System-Schicht, Entwurf 1 (2026-09-15)

Siehe `system_layer_utac.md` für den vollen Entwurf. Kernpunkte:

- **Namenskonflikt gefunden:** UTACs Kontrollparameter heißt in
  `utac_theory_core.md` "R" -- kollidiert mit Reproduktionsfähigkeit (R)
  aus der Information-Schicht. Vorschlag: `R_ctrl`, noch nicht von Johann
  bestätigt, noch nicht in die Quelldokumente zurückgetragen.
- **Individuationskriterium vorgeschlagen:** ein System entsteht genau
  dann, wenn komponierte Information eine signifikant positive
  Typ-1-Emergenz speziell in S (Stabilität) zeigt -- Wiederverwendung der
  Information-Schicht-Maschinerie statt neuer Grundbegriffe, deckt sich
  mit Maturana/Varelas operationaler Geschlossenheit.
- **Resistance = S bestätigt** (recherchiert): critical-slowing-down-
  Literatur zeigt, dass Erholungsrate = führender Eigenwert der
  Jacobi-Matrix = direkt mit dem lokalen Lyapunov-Exponenten verwandt --
  keine zwei Größen, dieselbe.
- **Precariousness = Θ−R_ctrl und Rate = dR_ctrl/dt** -- beide ergeben sich
  direkt aus UTACs bestehender Struktur, keine neue Mathematik nötig.
- **Panarchy = V auf System-Ebene** -- Wiederverwendung der
  Verbindungsfähigkeits-Mathematik, jetzt zwischen individuierten Systemen
  statt rohen Informationsknoten.
- **Latitude -- theoretische Lücke bleibt, praktische Mess-Lücke
  geschlossen (2026-09-15):** Latitude bleibt formal das Volumen/die
  Breite des Attraktor-Beckens (Walker et al. 2004), eine GLOBALE
  Eigenschaft, nicht aus S allein ableitbar, und UTAC hat weiterhin nur
  eine monotone Schwelle statt eines echten Beckens. Gefunden:
  **Basin Stability** (Menck, Heitzig, Marwan & Kurths, 2013, Nature
  Physics) schätzt Basin-Volumen per Monte-Carlo-Sampling, ohne
  geschlossene Potentialfunktion -- Latitude ist damit an UTAC-Systemen
  bereits praktisch messbar, auch ohne die theoretische bistabile
  Erweiterung. **Theoretische Erweiterung nachgeliefert (2026-09-15):**
  die Spitzen-Katastrophe (cusp catastrophe, Thom/Zeeman -- Standard in der
  Oekologie fuer alternative stabile Zustaende) verallgemeinert UTACs
  monostabiles Logistik-Modell zu einem echten Zwei-Parameter-Modell
  (`R_ctrl^3 - a(R_ctrl-Θ) - b = 0`); das bestehende Modell ist der
  monostabile Grenzfall (a ≤ a_crit). Latitude jetzt auch theoretisch
  als Sattelpunkt-Distanz definierbar. Nebenbefund: Precariousness
  (Θ−R_ctrl) ist nur im monostabilen Grenzfall exakt, im bistabilen Fall
  muesste sie auf den Sattelpunkt umgestellt werden. Details:
  `system_layer_utac.md`, Abschnitt 3.5.
- **Kritischen Schwellenwert und Umschlagpunkt zusammenführen geprüft,
  differenziert bestätigt (2026-09-15, auf Johanns Anfrage):** die
  Landau-Theorie der Phasenübergänge bestätigt, dass a_crit ein echter
  SPEZIALFALL von Typ-2-Emergenz ist (Pitchfork-Bifurkation = Standard-
  mathematik hinter Andersons "neue Dimension durch Symmetriebrechung").
  ABER: weder a_crit noch CREP_critical≈0.84 sind dasselbe wie das
  Individuationskriterium -- Individuation braucht nur irgendein
  stabiles Becken (Excess-S>0), Bistabilität ist ein selteneres,
  zusätzliches, spaeteres Ereignis. Der urspruengliche "vielversprechend"-
  Vermerk war zu grobkoernig und wurde korrigiert, nicht bestaetigt.
  Details: `system_layer_utac.md`, Abschnitt 3.5.
- **CREP_critical vs. a_crit geprüft (2026-09-15, auf Johanns Anfrage):**
  direkter Vergleich nicht sauber möglich (unterschiedliche
  Parameterräume, keine bestehende Brücke zwischen w_buffer(d)/P_info(d)
  und (a,b)). Stattdessen selbst hergeleitet: für das Spitzen-Potential
  gilt exakt `a = −S(Θ)`, also `a_crit=0 ⟺ S(Θ)=0` -- "a" ist identisch
  mit der bereits definierten Stabilität S am Schwellenpunkt Θ, kein
  neuer freier Parameter. Ob S(Θ)=0 seinerseits CREP_critical≈0.84
  entspricht, bleibt offen -- braucht erst die noch fehlende Brücke.
  Details: `system_layer_utac.md`, Abschnitt 3.6.
- **Brücke w_buffer/P_info -> S/K/R/V vorgeschlagen (2026-09-15, auf
  Johanns Anfrage):** w_buffer(d) ↔ Latitude (direkte Entsprechung,
  beide "Spielraum vor Verlust der Erholungsfähigkeit"); P_info(d) ↔
  ρ/(1-ρ) (Auslastungsdruck aus K, ρ=tatsächlicher Durchsatz/
  Shannon-Hartley-Kapazität -- dieselbe mathematische Form wie
  divergierende Wartezeiten in der M/M/1-Warteschlangentheorie bei
  Auslastung nahe 100%). Ausdrücklich als NEUER Vorschlag markiert, nicht
  aus einer Quelle übernommen. Zwei Einschränkungen: (1) CREP_critical≈0.84
  ist im Quelldokument selbst nur empirisch beobachtet (Baks
  Selbstorganisierte Kritikalität), nicht first-principles -- die Brücke
  macht den Vergleich wohldefiniert, löst ihn aber nicht rechnerisch auf,
  das braucht reale Messdaten. (2) Das Quelldokument selbst warnt, dass
  CREP(d)→1 (viel Puffer) ebenfalls schlecht ist ("eingefroren") -- kein
  einfaches "mehr Latitude = besser", sondern ein echtes mittleres
  Optimum. Details: `system_layer_utac.md`, Abschnitt 3.7.
- **Numerisch verifiziert (2026-09-15):** `verification/
  cusp_model_numerical_check.py` bestätigt an einem synthetischen
  Testfall real, lauffähig, reproduzierbar: `a=−S(Θ)` exakt (6 Testwerte),
  Latitude via Basin Stability <0,5% Abweichung von der analytischen
  Sattelpunkt-Distanz √a. Ein Vorzeichenfehler im ersten Testlauf wurde
  gefunden und korrigiert (dokumentiert, nicht stillschweigend behoben).
  Bestätigt NICHT die CREP_critical≈0.84-Frage -- dafür braucht es echte
  Messdaten, siehe `verification/README.md`.

## "Viele Systeme pro Paket" -- durchgespielt an afet-tensions (2026-09-15)

Siehe `worked_example_afet_tensions.md`. Kernergebnis: von 7 Klassen im
Paket sind nach dem Individuationskriterium nur 2 echte Systeme
(β-Hierarchie, Γ(z)-Evolution) -- die anderen 5 sind Projektionen ohne
eigene Dynamik. Eine reale, bereits im Code vorhandene Kopplung zwischen
den beiden gefunden (`desi_prediction.py`), NICHT reziprok (konkretes
Beispiel für die "Reziprozität ist Normalfall, nicht Gesetz"-Regel aus
`coupling_layer_afet.md`), Kopplungsform linear/multiplikativ (Onsagers
Basisform), nicht exp/tanh (das sind interne Selbstantwortformen, keine
Cross-System-Kopplungen). Nebenbefund: ein zweiter, kleinerer
Zirkelbezug in `desi_prediction.py`s `beta_eff`-Berechnung (numerisch
bestätigt, exakter Rundtrip zu BETA_LOCAL) -- vermerkt, nicht repariert.

- **Dritter CREP-Namenskonflikt gefunden (2026-09-15):**
  `v9_dimensional_emergence.md`s "Frame Principle" definiert ein eigenes
  `CREP(d) = w_buffer/(w_buffer+P_info)` (kritisch ≈0.84) -- eine dritte
  Bedeutung neben Ursprungsgrößen und kanonischer Bridge-Metrik. In
  `METRIC_REGISTRY.md` nachgetragen (siehe eigener Abschnitt unten).
- **Johanns "1/16-Invariante"-Frage beantwortet:** das Frame Principle
  ("eine neue Dimension entsteht, wenn Information sonst kollabieren
  würde") ist real (`v9_dimensional_emergence.md`, 2025-12-16) und
  entspricht exakt Typ 2 (neue Dimension), nicht Typ 1 -- mit einer
  bereits formalisierten Übergangsbedingung
  (S_info(d)→S_max(d) UND ∂S/∂t>Γ_threshold), die jetzt als
  Typ-2-Entdeckungskriterium uebernommen wird. σ_Φ≈1/16 selbst ist NICHT
  dieser Schwellenwert -- nur eine β-Fitting-Normierungskonstante in
  `utac-core`, deren eigener Ursprung unklar/unverifiziert ist. Der
  tatsächliche Kollaps-Schwellenwert im Frame Principle ist das oben
  genannte dritte CREP_critical≈0.84.

## Kopplungs-Schicht, Entwurf 1 (2026-09-15)

Siehe `coupling_layer_afet.md` für den vollen Entwurf. Kernpunkte:

- **Master-Formalismus gefunden, nicht neu erfunden: Onsager-
  Reziprozitätsbeziehungen** (1931, Nobelpreis 1968) -- die etablierte
  allgemeine Theorie gekoppelter irreversibler Prozesse, `J_i = Σ L_ij X_j`.
  Passt exakt zu Johanns ursprünglicher Absicht ("Kopplung für
  Thermodynamik").
- **L_ij = V (Verbindungsfähigkeit) = Panarchy** -- keine neue Größe,
  dieselbe Kopplungsgröße auf System-Ebene wiederverwendet.
- **Onsager-Reziprozität (L_ij=L_ji) als testbare Standardannahme, nicht
  Universalgesetz** -- gilt nachweislich nur nahe Gleichgewicht/bei
  mikroskopischer Zeitumkehrbarkeit; dieselbe Logik wie die
  K-V-Ko-Adaptionsregel der Information-Schicht (Normalfall symmetrisch,
  Abweichung diagnostisch informativ).
- **Problem 4 (zwei Kopplungsformen exp/tanh in `afet-tensions`) gelöst,
  nachträglich begründet:** exponentielle Form (Arrhenius/Eyring-Typ) für
  unbeschränkte Ratenobservablen (H₀), tanh-Form (Ising-Mean-Field-Typ)
  für beschränkte Ordnungsparameter (S₈) -- ein echtes, prinzipiengeleitetes
  Kriterium statt Ad-hoc-Wahl.
- **Thermodynamische Fundierung geschlossen:** Onsagers
  Entropieproduktions-Ungleichung (`ΣJ_iX_i≥0`) erweitert Landauers Prinzip
  (Information-Schicht) direkt auf die Kopplungsebene -- keine Kopplung
  ist kostenlos. Erklärt formal, warum AFET von Anfang an Thermodynamik-
  Kopplung war.
- Reparaturpfad für Γ_domain aufgezeigt (als unabhängig geschätzter L_ij),
  aber NICHT umgesetzt -- eigene Entscheidung, nicht impliziert.

## Unabhängige Review (Gemini, 2026-09-15)

Johann hat den Stand nach der Kopplungs-Schicht extern von Gemini
gegenlesen lassen (`Gemini.txt`, in diesem Ordner abgelegt). Ergebnis:
**keine neuen Fehler gefunden** -- die Review bestätigt die drei Schichten
inhaltlich (insbesondere die Friis-Trennung von K/V, die
domänen-neutralen Berechnungsvorschriften, das Basin-Stability-Argument
für Latitude, und die Onsager-Fundierung von AFET) und benennt als
"offene Baustellen" exakt dieselben vier Punkte, die hier bereits selbst
als offen protokolliert waren: R/R_ctrl-Namenskonflikt, dritte
CREP-Bedeutung (Frame Stability Metric), der rekursiv ungelöste
Individuations-Schwellenwert, und die bewusst aufgeschobenen
Code-Reparaturen (Γ_domain, `P: 0.8`). Keine Ergänzung, aber eine
unabhängige Bestätigung, dass die Selbsteinschätzung dieses Dokuments
vollständig war -- vergleichbar mit GrokBots Review von `semantic-map`
im September, nur diesmal bestätigend statt korrigierend.

## METRIC_REGISTRY.md nachgetragen (2026-09-15)

Der dritte CREP-Fund (Frame Stability Metric, `v9_dimensional_emergence.md`)
ist jetzt in `Architektur--Planungsprojekt/.claude/worktrees/
architektur-ecosystem-assessment/METRIC_REGISTRY.md` dokumentiert, unter
dem bestehenden CREP-Abschnitt, nach demselben Muster wie der frühere
UTAC-Abdrift-Befund (gefunden, Umbenennung empfohlen -- `Frame-Stabilität
F(d)` --, kein sofortiger Umbau-Anlass, opportunistisch bei nächster
Berührung von `v9_alpha`).

## Γ_domain -- nur dokumentiert, nicht repariert (2026-09-15)

Johanns explizite Entscheidung (per Rückfrage): Γ_domain in `afet-tensions`
jetzt nur mit einem ehrlichen Known-Issue-Kommentar versehen, keine Werte
ändern, kein Refit, kein Versions-Bump. Umgesetzt in
`afet-tensions/src/afet_tensions/constants.py` (Kommentar oberhalb von
`GAMMA_DOMAIN`) und `afet-tensions/CHANGELOG.md` (`[Unreleased]` ->
Documentation). Geprüft: `GAMMA_DOMAIN` unveraendert (0.7347...), Import
funktioniert weiterhin. Ein echter unabhängiger Refit waere moeglich
(`afet-tensions/data/*.yaml` enthaelt 5 echte H0- und 4 echte
S8-Messungen), braeuchte aber eine begruendete Pro-Messung-β-Zuordnung
statt nur zwei Kategorien (early/late) -- als groessere, eigene Aufgabe
zurueckgestellt, nicht in diesem Schritt.

## R/R_ctrl final bestätigt und in Quelldokumente zurückgetragen (2026-09-15)

Johann hat die Umbenennung final bestätigt. Umgesetzt:
- `Feldtheorie/docs/science/utac_theory_core.md` (Worktree-Kopie): R -> R_ctrl
  durchgängig, mit Namens-Hinweis am Dokumentanfang.
- `utac-core/src/utac_core/core.py`: Sympy-Symbol `R` -> `R_ctrl` umbenannt;
  alle 19 bestehenden Tests laufen unverändert durch (geprüft).
- `utac-core/README.md`: das eine funktionsrelevante Beispiel
  (`frame_principle()`-Ausgabe) und die Symboltabelle korrigiert, damit sie
  wieder mit der echten Ausgabe übereinstimmen. Dekorative Taglines (Titel,
  Ordnerstruktur-Kommentare) bewusst NICHT geändert -- reiner
  Kurzform-Sprachgebrauch, kein funktionaler Fehler.
- `utac-core/CHANGELOG.md`: `[Unreleased]` -> Changed-Eintrag ergänzt.
Reiner Symbol-Rename, keine Modelländerung, keine gebrochenen Tests.

## Absichtlich noch nicht entschieden
- Kritischer Schwellenwert für "System-Werden" (Individuationskriterium
  oben) -- selbst ein rekursives Schwellenwertproblem.
