# Kopplungs-Schicht (AFET) — Formalismus, Entwurf 1

Stand: 2026-09-15. Baut auf `system_layer_utac.md` auf: zwei bereits
individuierte Systeme A, B (je mit Θ, β=S/Resistance, R_ctrl(t), Latitude
via Basin Stability, Panarchy=V) sollen jetzt formal gekoppelt werden --
verallgemeinert über die bisher einzige, thermodynamik-/kosmologie-
spezifische Instanz (`afet-tensions`, P34) hinaus.

## 1. Master-Formalismus: Onsager-Reziprozitätsbeziehungen

**Onsager (1931, Nobelpreis 1968)** ist die etablierte, allgemeine Theorie
gekoppelter irreversibler Prozesse -- genau das, was AFET von Anfang an
sein sollte ("Kopplung für Thermodynamik", Johann 2026-09-15):
\[ J_i = \sum_j L_{ij} X_j \]
wobei J_i ein **Fluss** (hier: dR_ctrl,i/dt -- die Rate-Variable aus der
System-Schicht), X_j eine **thermodynamische Kraft** (hier: ein
Zustandsunterschied zwischen gekoppelten Systemen, z.B.
X_ij = R_ctrl,j − R_ctrl,i oder eine Θ-Differenz) und L_ij der
**Kopplungskoeffizient** ist.

**Zentrale Identifikation:** L_ij ist dieselbe Größe wie **V
(Verbindungsfähigkeit)** aus der Information-Schicht, jetzt auf
System-Ebene angewendet (= Panarchy aus `system_layer_utac.md`, Abschnitt
3). Keine neue Größe -- Wiederverwendung.

**Onsager-Reziprozität L_ij = L_ji** gilt nachweislich nur unter
mikroskopischer Zeitumkehrbarkeit, nahe des Gleichgewichts -- **keine
universelle Notwendigkeit, sondern eine testbare Standardannahme**, exakt
im selben Sinne wie die K-V-Ko-Adaptionsregel aus der Information-Schicht
(Abschnitt 3 dort): der symmetrische Fall ist der ERWARTETE Normalfall,
asymmetrische Kopplung (V_ij ≠ V_ji) ist selbst diagnostisch informativ --
z.B. bei Täuschung/Tarnung (Information-Schicht) oder generell bei
Kopplungen fern des Gleichgewichts.

## 2. Zwei kanonische Kopplungsformen -- prinzipiengeleitete Wahl, kein Ad-hoc

Löst das in `DESIGN.md` als "unklar/ad hoc" markierte Problem 4
(`afet-tensions` nutzt `exp(...)` für H₀, `tanh(...)` für S₈):

- **Exponentiell (Arrhenius/Eyring-Typ):** `k = A·exp(−ΔG/k_BT)` --
  die etablierte Form für RATENARTIGE, unbeschränkte Observablen
  (Aktivierungsprozesse, Wachstumsraten). Passt zu H₀ (Einheit 1/Zeit,
  unbeschränkter Ratenparameter).
- **tanh (Ising-Mean-Field-Typ):** `M = tanh(h/k_BT)` -- die etablierte
  Form für BESCHRÄNKTE, sättigende Zwei-Zustands-Ordnungsparameter. Passt
  zu S₈ (normierte, beschränkte Amplitude).

**Kriterium für die Formwahl (neu, ersetzt Ad-hoc-Auswahl):** ist die
gekoppelte Observable eine unbeschränkte Rate/ein Wachstumsprozess ->
exponentielle Kopplung; ist sie eine beschränkte, normierte Amplitude/ein
Ordnungsparameter -> tanh-Kopplung. `afet-tensions`s Wahl war also
vermutlich richtig, aber nie als Prinzip benannt -- jetzt nachträglich
begründet, nicht neu erfunden.

## 3. Thermodynamische Fundierung (schließt den Kreis zur Information-Schicht)

Onsagers Formalismus verlangt **Entropieproduktion ≥ 0**:
\[ \dot{S}_{prod} = \sum_i J_i X_i \geq 0 \]
Keine Kopplung ist thermodynamisch kostenlos -- das erweitert Landauers
Prinzip (Information-Schicht, Stabilität S) direkt auf die Kopplungsebene:
so wie das Halten einzelner Information Energie kostet, kostet auch das
Koppeln zweier Systeme Energie/erzeugt Entropie. Das bestätigt formal,
warum AFET von Anfang an als Thermodynamik-Kopplung gedacht war (Johann,
2026-09-15) -- nicht zufällig, sondern weil die gesamte Formalismus-Kette
(Information -> System -> Kopplung) auf denselben thermodynamischen
Grundprinzipien aufbaut.

## 4. Konsequenz für den bekannten Γ_domain-Fehler (nicht umgesetzt, nur Weg aufgezeigt)

Mit dem Onsager-Rahmen wird sichtbar, WIE Γ_domain korrekt bestimmt werden
müsste: als unabhängig aus Daten geschätzter Kopplungskoeffizient L_ij
(z.B. aus der tatsächlichen Beziehung zwischen dH₀/dz und einem
Γ(z)-Gradienten), nicht algebraisch aus dem bereits bekannten
H₀-Verhältnis zurückgelöst (`DESIGN.md`, Problem 1). Das ist ein konkreter
Reparaturpfad, aber **hier nicht umgesetzt** -- Änderungen an
`afet-tensions` selbst sind weiterhin nicht Teil dieses Ordners, außer
Johann entscheidet das ausdrücklich.

## 5. Offene Punkte für den nächsten Schritt

1. Prüfen, ob L_ij = L_ji (Onsager-Reziprozität) für reale
   GenesisAeon-Kopplungsfälle zutrifft, oder ob die interessanten Fälle
   (wie bei Tarnung in der Information-Schicht) gerade die asymmetrischen
   sind.
2. Exponentiell-vs-tanh-Kriterium (Abschnitt 2) an weiteren realen Fällen
   testen, nicht nur an H₀/S₈ bestätigen.
3. Entscheiden, ob/wann Γ_domain in `afet-tensions` tatsächlich nach
   Abschnitt 4 repariert wird -- eigene Entscheidung, nicht impliziert.
4. Erst danach: die drei Schichten (Information/System/Kopplung) in einem
   zusammenfassenden Übersichtsdokument bündeln.

Sources:
- [Onsager reciprocal relations — Wikipedia](https://en.wikipedia.org/wiki/Onsager_reciprocal_relations)
- [Magnetisation and mean field theory in the Ising model](https://arxiv.org/pdf/2102.00960)
- [Arrhenius Equation — Chemistry LibreTexts](https://chem.libretexts.org/Bookshelves/Physical_and_Theoretical_Chemistry_Textbook_Maps/Supplemental_Modules_(Physical_and_Theoretical_Chemistry)/Kinetics/06:_Modeling_Reaction_Kinetics/6.02:_Temperature_Dependence_of_Reaction_Rates/6.2.03:_The_Arrhenius_Law/6.2.3.01:_Arrhenius_Equation)
