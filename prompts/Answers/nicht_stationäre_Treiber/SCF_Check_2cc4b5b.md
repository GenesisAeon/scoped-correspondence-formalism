# Nachprüfung von 2cc4b5b

23. September 2026 · `GenesisAeon/scoped-correspondence-formalism` · Commit `2cc4b5b1cd61f40b283bd8f48f9a61479990a7fc`.

**Der numerische Puffer-Fix ist bestätigt. Die korrigierten Ergebnisaussagen sind deutlich besser. Der Profil-API-Punkt ist noch nicht vollständig geschlossen.**

Gezielt geprüft wurden die Änderungen gegenüber `1231f64`: neun geänderte Quell-, Dokumentations- und Testdateien lokal übernommen und gegen ihre Git-Blob-SHAs verifiziert. Fünf relevante Verifikationsskripte wurden erneut ausgeführt; alle bestanden: `verify_multidim_tipping_maps.py`, `verify_profile_likelihood_core.py`, `verify_rate_viability_control_cases.py`, `verify_structural_bridges_b7_b8.py`, `verify_energy_balance.py`. Die gemeldeten 69/69 Suiten und beide Link-Checker wurden in dieser fokussierten Nachprüfung nicht vollständig erneut ausgeführt. Keine Änderungen am GitHub-Repository.

**1. Kontinuierliches Pufferminimum: bestätigt**

Die unabhängige Gegenrechnung verwendet die analytische Faltung und bestimmt ihre Extremstelle mit einer Nullstellensuche der Ableitung. Damit verwendet sie weder den ODE-Löser noch dieselbe Minimumsuchroutine wie die Implementierung.

| Größe | Nachgerechneter Wert |
|---|---:|
| Analytisches Minimum | −0,6947532810696937 |
| Minimum der Implementierung | −0,6947532810695638 |
| Absoluter Unterschied | 1,30 × 10⁻¹³ |
| Prüfgrenze b | −0,694753066685 |
| Neues Ergebnis | `switched`, korrekt |

Der ursprüngliche Rasterfehler ist für diesen Gegenfall behoben und durch den neuen Regressionstest abgesichert. Der Unterschied zweier numerischer Lösungen bleibt ein Fehlerindikator, kein rigoroser mathematischer Gesamtfehlerbeweis. Das schmälert die hier erfolgreiche Korrektur nicht.

**2. Unterabdeckung und Überclaim: angemessen nachgezogen**

Die Prognoseintervalle werden jetzt mit ihren korrigierten Zahlen und ausgelassenen Fällen dargestellt. Die Unterabdeckung ist als Hauptergebnis sichtbar: EBM 21/40 = 52,5 %, COVID-Renewal 5/19 = 26,3 %, jeweils bei nominell 80 %. Der positive Dispersionsfit wird nicht mehr als bereits durchgeführter Signifikanztest ausgegeben; Mittelwertfehler werden als alternative Erklärung genannt. Das vertauschte above/below im Puffer-Docstring ist korrigiert.

Kleine redaktionelle Korrektur: Die COVID-Überschrift in `docs/mechanistic_probabilistic_evaluation.md` behauptet nun „the point-forecast winner is not the interval winner“. Direkt darunter besitzt Renewal weiterhin den besten Intervallscore. Treffend wäre etwa: **„Best interval score, but severe undercoverage“**. Score-Rang und Kalibrierung beantworten unterschiedliche Fragen.

**3. Noch offen: `flat_profile` beweist keine globale Unbeschränktheit**

Die neue API behandelt das alte quadratische Gegenbeispiel korrekt mit `established_unbounded=False`. Im Zweig `flat_profile` setzt sie dieses Feld jedoch automatisch auf `True`.

Das lässt sich aus einem endlichen Zahlenraster grundsätzlich nicht ableiten. Ein exakt flacher Ausschnitt kann außerhalb des Scans steigen. Das folgende Gegenbeispiel ist stetig differenzierbar und konvex:

\[
\chi^2(\theta)=\max(|\theta|-1,0)^2.
\]

Auf dem Scan `[-1, -0.5, 0, 0.5, 1]` sind sämtliche Profilwerte exakt null. Bei Schwelle 1 ist die vollständige Menge aber **[−2, 2]**, also beschränkt. Die aktuelle Funktion gibt dennoch aus:

```python
likelihood_interval(
    [(-1.0, 0.0), (-0.5, 0.0), (0.0, 0.0), (0.5, 0.0), (1.0, 0.0)],
    threshold=1.0,
)
# classification: "flat"
# established_unbounded: True  <-- global nicht gerechtfertigt
```

Auch ohne exaktes Plateau tritt das Problem auf: Das analytische Polynom χ²(θ)=θ⁴ wird auf `[-0.1, 0, 0.1]` wegen der Varianzschwelle als flach klassifiziert und als nachgewiesen unbeschränkt gemeldet. Bei Schwelle 1 ist die tatsächliche Menge [−1, 1]. Beide Gegenproben wurden ausgeführt.

**Empfohlene kleine Korrektur:** Aus gescannten Werten allein `established_unbounded` nicht auf `True` setzen. `flat_in_scanned_range` bzw. `no_endpoint_found` bezeichnet genau das Beobachtete. Eine globale Unbeschränktheit benötigt zusätzliche analytische oder strukturelle Evidenz und sollte getrennt erfasst werden. Der bestehende Test des Produktmodells kann dessen echte Nichtidentifizierbarkeit weiterhin zeigen; das folgt dort aus der Struktur θ₁θ₂=6, nicht allein aus fünf gleichen Profilwerten. Die alten Boolean-Felder können bei nötiger Rückwärtskompatibilität bleiben, ihre eingeschränkte Bedeutung muss klar sein.

**Nächster Schritt:** Diesen letzten semantischen Punkt korrigieren und danach den Schwerpunkt auf die vorab festgelegte, zeitlich korrekte Intervallkalibrierung legen. Die Klimareferenz-/Initialisierungsfrage bleibt laut Roadmap bewusst offen; sie wurde durch diesen Commit nicht gelöst und sollte weiter als eigener Modellschritt geführt werden.

**Reproduktion:** Das Begleitarchiv enthält `independent_probes.py`, `independent_results.json`, `suite_summary.json` und fünf Prüfprotokolle. Einen Checkout des fixierten Commits unter `repo/` neben das Prüfprogramm legen und `python independent_probes.py` ausführen. Die Assertions bestätigen sowohl den reparierten Pufferfall als auch die aktuell reproduzierbaren API-Gegenbeispiele. Keine Repositoryquellen oder Rohdaten sind im Archiv enthalten.
