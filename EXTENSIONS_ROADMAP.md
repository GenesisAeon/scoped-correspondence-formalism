# Extensions Roadmap — natürliche mathematische Erweiterungen

Konsolidiert zwei unabhängige DeepResearch-Antworten auf
[prompts/16_deepresearch_natural_extensions.md](prompts/16_deepresearch_natural_extensions.md):
[ChatGPTAstra3.md](prompts/Answers/ChatGPTAstra3.md) (10 Vorschläge) und
["Mathematische Erweiterungen Scoped Correspondence.docx"](prompts/Answers/Mathematische%20Erweiterungen%20Scoped%20Correspondence.docx)
(7 Vorschläge, vermutlich Gemini). Beide unabhängig von Claude verifiziert
(Zahlenbeispiele von Hand nachgerechnet, alle Zitate per Fork gegen
DOI/arXiv geprüft — siehe F26/F28 in `FOLLOWUP_TICKETS.md`). Eine dritte
Einreichung (`ChatGPTAstra4.md`) wurde als erkennbar halluziniert
**verworfen** (F28) — kein Bezug zum echten Repo, erfundene Dateistruktur.

**Harte Regel für jeden Eintrag (aus dem DeepResearch-Auftrag selbst):**
jede Erweiterung hängt an GENAU EINEM bestehenden Baustein, keine
Cross-Layer-Identität, keine Universalitätsbehauptung, echte
DOI/arXiv-Quelle, nach Möglichkeit von Hand nachrechenbares Beispiel.

## Status je Baustein

| Baustein | Kandidat | Quelle | Status |
|---|---|---|---|
| `correspondence` | Approximation Certificates (fixed-map-Spezialfall) | Girard & Pappas 2007, DOI 10.1109/TAC.2007.895849 | ✅ **M10, gemergt** |
| `observation` | Directed Information (Rückkopplungskapazität) | Massey 1990; Permuter, Weissman, Goldsmith 2009 | offen |
| `dynamics` | Fenichels Theorem / GSPT (langsame invariante Mannigfaltigkeit) | Fenichel 1979, DOI 10.1016/0022-0396(79)90152-9; Kuehn 2015, DOI 10.1007/978-3-319-12316-5 | offen |
| `dynamics` | Contraction Analysis | Lohmiller & Slotine 1998, DOI 10.1016/S0005-1098(98)00019-3 | ✅ **M14, gemergt** |
| `coupling` | Dirac-Struktur-Komposition | Cervera, van der Schaft & Baños 2007, DOI 10.1016/j.automatica.2006.08.014 | ✅ **M12, gemergt** |
| `coupling` | Dissipativity / Supply Rates | Willems 1972, DOI 10.1007/BF00276493 | ✅ **M15, gemergt** |
| `closure` | CTMC-Generator-Lumpability (`QC=CQ_macro`) | Buchholz 1994, DOI 10.1017/S0021900200107338; Michel & Siegle, DOI 10.1016/j.peva.2024.102464 | ✅ **M11, gemergt** |
| `closure` | Formal Reduction Error Bounds (allgemeine Fehlerschranken) | Michel & Siegle 2025 (dieselbe Quelle, andere Aussage) | offen |
| `viability` | Control Barrier Functions | Ames et al. 2017, DOI 10.1109/TAC.2016.2638961; Ames et al. 2019, DOI 10.23919/ECC.2019.8796030 — **von beiden Recherchen unabhängig vorgeschlagen** | ✅ **M16, gemergt** |
| `membership` | — | (gewichtete/kontinuierliche Zugehörigkeit bewusst zurückgestellt, Semantik unklar) | kein Kandidat |
| `identifiability` | Profile Likelihood | Raue et al. 2009, DOI 10.1093/bioinformatics/btp358 | offen |
| `identifiability` | Fisher-Information-Sloppiness | Transtrum, Machta & Sethna 2011, DOI 10.1103/PhysRevE.83.036701; Raju et al. 2018 | offen |
| `validation` | Split Conformal Prediction | Lei, G'Sell, Rinaldo, Tibshirani, Wasserman 2018, DOI 10.1080/01621459.2017.1307116 | ✅ **M13, gemergt** |
| `contextuality` | Čech-Cohomology-Witness | Abramsky, Mansfield & Barbosa 2012, arXiv 1111.3620 | offen |
| `contextuality` | CSW-Grapheninvarianten | Cabello, Severini & Winter 2014, DOI-bestätigt (PRL 112, 040401) | offen |
| `information_decomposition` | BROJA bivariate Unique Information | Bertschinger, Rauh, Olbrich, Jost & Ay 2014, DOI 10.3390/e16042161 | offen |
| `thermo` | Schnakenberg Network Thermodynamics | Schnakenberg 1976, DOI 10.1103/RevModPhys.48.571 | offen |
| `metarules` (kein Originalbaustein, F25) | — | context_transformations.md §6 | ✅ **M9, gemergt** |

**Bewusst kein Kandidat identifiziert (mit Begründung):** `validation`
(neue Theoreme würden den empirischen Testcharakter verfälschen —
`validation` bleibt Protokoll, nicht Theorie); `thermo` als Ganzes
(bestehende Abdeckung durch M8 bereits vollständig, Schnakenberg oben
ist die einzige verbleibende offene Vertiefung); `information_decomposition`
über BROJA hinaus (N-Quellen-PID bleibt bewusst offenes Forschungsfeld,
nicht spekulativ vorwegnehmen).

## Reihenfolge / Priorisierung

Kein festes Ranking — die drei aktuell in Arbeit befindlichen (M11–M13)
wurden nach Astra3s eigener Einschätzung "geringster Aufwand" bzw.
bereits vollständig durchgerechnetem Beispiel gewählt. Für die
verbleibenden zwölf Kandidaten gilt dieselbe Logik: kleinere,
gut belegte Fälle zuerst, größere (Čech-Kohomologie, BROJA, Schnakenberg)
später. Reihenfolge wird bei Bedarf mit Johann abgestimmt, nicht
automatisch abgearbeitet.

## Arbeitsweise (unverändert für jeden Eintrag)

1. Prompt für Aeon schreiben (Referenzen gegen echten Code/Doku-Stand
   verifizieren, bevor gesendet wird).
2. Aeon liefert auf eigenem Branch (`aeon/m<n>-<name>`).
3. Claude reviewed unabhängig: Diff-Scope prüfen (nur additive Module,
   keine Kernmutation), Skript selbst nachrechnen, mindestens eine Zahl
   von Hand gegenprüfen.
4. Merge erst nach Johanns explizitem OK.
5. `FOLLOWUP_TICKETS.md` und diese Datei aktualisieren.

Mehrere Einträge können parallel an Aeon gehen, wenn sie unterschiedliche
Module betreffen (kein Merge-Konflikt-Risiko) — aktuell M11/M12/M13
gleichzeitig in Arbeit.
