# Mittelwert gegen Verteilung (Kosmische Vererbung, SCF-Seite)

Teil von [`KOSMISCHE_VERERBUNG_SCF_ROADMAP.md`](../KOSMISCHE_VERERBUNG_SCF_ROADMAP.md).
Plan: [`KOSMISCHE_VERERBUNG_BESTANDSAUFNAHME_UND_PLAN.md`](../prompts/Answers/nicht_stationäre_Treiber/KOSMISCHE_VERERBUNG_BESTANDSAUFNAHME_UND_PLAN.md), §6.2 und §8.
Lizenz: CC BY 4.0.

## Frage

Zwei Gaszustände können dieselbe **mittlere** Metallizität haben und sich trotzdem im Anteil **unberührten** Gases unterscheiden. Zwei Fragen hängen daran:
- Reicht eine Beobachtung des Mittelwerts aus, um diesen Anteil festzulegen?
- Reicht der Mittelwert als makroskopischer Zustand, um die weitere Entwicklung vorherzusagen?

SCF prüft beides als **endliche, exakte Struktur**. Ob ein realer Anreicherungsprozess einem der Fälle gleicht, ist eine Domänenfrage. Sie wird in Feldtheorie bearbeitet (Plan V3/V5).

## Kontrollmodell

- Zwei gleich schwere Gaspakete; Metallizität z ∈ {0, 1, 2} in Einheiten von 0,01; Mikrozustand (z₁, z₂).
- Beobachtung h = (z₁ + z₂)/2.
- Zielgröße f₀ = Anteil der Masse mit z = 0.
- Ein Sternbildungsschritt wählt ein Paket mit Wahrscheinlichkeit ½ und setzt z → g(z).

| Fall | Was er zeigt |
|---|---|
| MV-K1 | Bei h = 0,01 (y = 1) sind (0, 0,02), (0,01, 0,01) und (0,02, 0) nicht zu unterscheiden. f₀ ist nur als **Menge** {0, ½} bestimmt, ausdrücklich nicht als Intervall. Ein Wert außerhalb des Modellraums (y = 5/2) ergibt eine leere Faser, also eine Fehlanpassung und keine Identifikation. |
| MV-K2 | Ertrag, der auf unberührtes Gas besonders reagiert (g(0) = 2): Der Mittelwert ist **kein** ausreichender Zustand (Lumpability-Defekt 1). Mittelwert plus f₀ reicht hier. |
| MV-K3 | Z-blinder, aber gesättigter Ertrag g(z) = min(z+1, 2): Auch hier reicht der Mittelwert **nicht** (Defekt ½). |
| MV-K4 | Summenerhaltende Mischung: Die Dynamik des Mittelwerts ist exakt. Das Ereignis „unberührtes Gas vorhanden“ bleibt trotzdem makroskopisch unbeobachtbar. |

## Lesart

1. **Unzureichender Mittelwert ist kein Mechanismusbeleg.** MV-K3 erzeugt dieselbe Art von Unzureichendheit ohne jede Pop-III-Sonderregel, allein durch Sättigung. Eine Aussage der Form „der Mittelwert reicht nicht, also wirkt Mechanismus X“ braucht ein Gegenmodell, das X ausschließt.
2. **Exakte Makrodynamik ist nicht dasselbe wie die Beobachtbarkeit einer Zielaussage** (MV-K4). Beides wird getrennt berichtet.
3. Dass (h, f₀) hier alle Mikroklassen bis auf Vertauschung trennt, gilt nur für zwei Pakete auf drei Rasterpunkten. Allgemein gilt es nicht.

## Prüfung

```
python verification/verify_kv_mean_vs_distribution.py
python verification/plan_controls/kv_series_independent_controls.py   # unabhängige Fraction-Rechnung
```

Status: `evidence_kind = exhaustive_finite`, `empirical_status = synthetic_only`. Es gibt keine astrophysikalische und keine JWST-Aussage.
