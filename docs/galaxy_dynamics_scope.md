# Galaxy Dynamics — Quellen-, Einheiten- und Hypothesenregister (G0)

**Status:** G0-Register, review package — noch nicht von README/GLOSSARY als
akzeptierter "core" verlinkt. Kein Code in diesem Paket, nur Register und
unabhängige Nachrechnung (siehe `GALAXY_DYNAMICS_ROADMAP.md`).

Antwort auf `prompts/Answers/nicht_stationäre_Treiber/SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md`
Abschnitt 5 ("G0 — Eingaben, Einheiten und falsifizierbare Fragen").

## Zweck

Jede in dieser Domäne verwendete physikalische Eingabe und jeder behauptete
Zielwert bekommt hier einen Status, bevor er in Code auftaucht. Ein Status
darf sich später nicht stillschweigend ändern (Plan §5.2). Vier Kategorien:

- **belegt** — direkt aus einer zitierten Publikation übernommen, keine
  eigene Anpassung.
- **modellabhängig** — folgt aus einer deklarierten Modellannahme (z. B.
  MOND-Interpolationsfunktion), ist keine unabhängige Messung.
- **gefittet / kalibriert** — wird in dieser Arbeit selbst aus Daten
  geschätzt (z. B. `rho0`, `r0` je SPARC-Galaxie).
- **blockiert** — für eine vollständige Verwendung fehlt noch eine Quelle
  oder Berechtigung (aktuell nur Yoon 2026, siehe unten).

## 1. Feste numerische Konventionen (Plan §5.3)

| Symbol | Wert | Einheit | Rolle |
|---|---:|---|---|
| `G_SI` | 6.67430e-11 | m³ kg⁻¹ s⁻² | Gravitationskonstante, Rechenkonvention |
| `PC_M` | 3.085677581491367e16 | m | 1 Parsec |
| `MSUN_KG` | 1.98847e30 | kg | 1 Sonnenmasse |
| `A0_SI` | 1.2e-10 | m s⁻² | externer MOND-Eingang, nicht selbst gefittet |
| `G_ASTRO` | 4.301047329314801e-6 | kpc (km/s)² M_sun⁻¹ | Gravitationskonstante in astronomischen Einheiten |

Status: **belegt als Rechenkonvention** — dies sind Standardwerte, keine
Behauptung unendlicher Präzision von Naturkonstanten. Umrechnungen:
`1 (km/s)²/kpc = 1e6/(1000·PC_M) m/s²`; `1 M_sun/pc³ = 1e9 M_sun/kpc³`.

## 2. Belegte empirische Aussagen

| Aussage | Wert | Status | Quelle |
|---|---:|---|---|
| Donato et al. (2009): Halo-Produkt | `log10(mu_h/[M_sun pc^-2]) = 2.15 ± 0.2` | belegt | [S1] |
| — numerisch transformiert | Zentralwert 141.25375446, Bereich 89.12509381–223.87211386 | eigene Transformation, **keine kalibrierte Konfidenzangabe** | eigene Rechnung, s. u. |
| MOND-Flächendichte `Sigma_M = a0/(2πG)` | 137.0180243872182 M_sun/pc² | modellabhängig (folgt aus `a0`, keine Messung eines Halos) | [S2] |
| Yoon (2026): analytische Näherung | `10^(2.24 ± 0.09) M_sun pc^-2` ≈ 173.78 | belegt als berichtetes Ergebnis, **Gleichungskette nicht geprüft** | [S4]–[S6], siehe `yoon_2026_source_audit.md` |
| FIRE-2 (Dalui/Desai): Halo-Flächendichte ~konstant für CDM und SIDM in Zwerggalaxien (~10^10 M_sun) | ohne Zahl übernommen als Warnung gegen Modell-Diskriminierung durch bloße Konstanz | belegt, begrenzter Massenbereich | [S7] |

**Wichtig (Plan §3.3):** Aus einer ähnlichen Flächendichte folgt weder die
Widerlegung dunkler Materie noch eine Bestätigung von SCF/UTAC/CREP/AFET.
Diese Domäne fügt keine neue Skala, keinen Kippprozess und keine
Gravitation-Information-Identität hinzu.

## 3. Modellabhängige/deklarierte Größen (für G3)

| Größe | Definition | Status | Hinweis |
|---|---|---|---|
| MOND-Interpolationsfunktion `mu_M(x) = x/sqrt(1+x^2)` | algebraisches Vergleichsmodell für Rotationskurven | modellabhängig, explizit deklariert | die alternative Funktion `x/(1+x)` ist NICHT austauschbar — deren zentrale Phantom-Säulendichte divergiert logarithmisch [S2] |
| `g/a0` bei `g_N = a0` | `1.272019649514069` | modellabhängig, exakte algebraische Konsequenz der gewählten Funktion | eigenständig nachgerechnet, s. u. |
| Burkert-, pseudoisothermes und NFW-Profil | drei alternative Halo-Formen | modellabhängig, dienen als Kontrollmodelle A/B (Plan §8.3) | keines ist "die Wahrheit", jedes ist eine deklarierte Baseline |
| `Upsilon_d = 0.5`, `Upsilon_b = 0.7` (M/L-Verhältnisse) | erste transparente SPARC-Baseline | modellabhängig, externe Annahme | Rolle als Modellannahme kennzeichnen, nicht als gemessene Konstante |

## 4. Gefittete Größen (entstehen erst in G5)

`rho0`, `r0` (bzw. `mu_h = rho0·r0`) je Galaxie im SPARC-Piloten — Status
wird erst nach dem Fit vergeben (deskriptiv, Modus A) bzw. nach
Testauswertung auf zurückgehaltenen äußeren Radien (Modus B, Plan §10.3).
Keine dieser Zahlen existiert vor G5.

## 5. Blockierte Quelle: Yoon (2026)

Siehe eigenes Dokument `docs/yoon_2026_source_audit.md`. Kurzfassung: Der
Volltext war bei Erstellung dieses Registers (2026-09-26) nicht
beschafft. G6 bleibt bis zur legalen Volltextbeschaffung blockiert; kein
Fake-Adapter, der einfach 170 (bzw. 173.78) zurückgibt.

## 6. Unabhängig nachgerechnete Kontrollwerte

Alle Werte unten wurden mit reinem Python (`math`-Standardbibliothek,
keine SCF-Produktionsformeln) neu berechnet, um die im Plan behaupteten
Zahlen vor jeder Implementierung zu bestätigen (Plan §12.2: "Vor
Implementierung relevante Herleitungen und Gegenfälle selbst
nachrechnen"). Volle Übereinstimmung, siehe `GALAXY_DYNAMICS_ROADMAP.md`
für die Ergebnistabelle.

```python
import math

def lognorm(mu, sigma):
    return 10**mu, 10**(mu - sigma), 10**(mu + sigma)

# Donato / Yoon log10-Transformationen (Plan Tabelle §3.1)
lognorm(2.15, 0.2)   # -> (141.2537544622754, 89.12509381337455, 223.872113856834)
lognorm(2.24, 0.09)  # -> (173.78008287493762, 141.25375446227554, 213.79620895022325)

# MOND-Flächendichte Sigma_M = a0/(2 pi G) (Plan §8.2)
G_SI = 6.67430e-11
A0_SI = 1.2e-10
PC_M = 3.085677581491367e16
MSUN_KG = 1.98847e30
Sigma_M = A0_SI / (2 * math.pi * G_SI) * PC_M**2 / MSUN_KG
# -> 137.01802438721816

# MOND g/a0 bei g_N = a0: g = sqrt((gN^2 + gN*sqrt(gN^2 + 4 a0^2)) / 2)
x = 1.0
g_over_a0 = math.sqrt((x**2 + x * math.sqrt(x**2 + 4)) / 2)
# -> 1.272019649514069

# Burkert-Referenzfall: rho0=0.05 Msun/pc^3, r0=3 kpc, ausgewertet bei r=r0
rho0, r0_pc = 0.05, 3000.0
mu_h = rho0 * r0_pc                       # -> 150.0
Sigma_col0 = (math.pi / 2) * mu_h         # -> 235.61944901923448
x = 1.0
bracket = math.log(1 + x) + 0.5 * math.log(1 + x**2) - math.atan(x)
M_over_rho_r3 = 2 * math.pi * bracket     # -> 1.5979560703661266
M_r0 = rho0 * r0_pc**3 * M_over_rho_r3    # -> 2157240694.994271 [M_sun]

G_ASTRO = 4.301047329314801e-6            # kpc (km/s)^2 Msun^-1
r0_kpc = 3.0
g_astro = G_ASTRO * M_r0 / r0_kpc**2      # (km/s)^2/kpc
g_si = g_astro * 1e6 / (1000 * PC_M)      # -> 3.3410253537355016e-11 [m/s^2]
v_c = math.sqrt(G_ASTRO * M_r0 / r0_kpc)  # -> 55.61293113984166 [km/s]
```

## 7. Vorab festgehaltene Fragen (Plan §5.1, unverändert übernommen)

1. Welche Flächendichtegröße wird jeweils verglichen: Profilparameterprodukt,
   tatsächliche Säulendichte, aperture-gemittelter Wert oder ein aus einem
   anderen Modell rückgerechneter Parameter?
2. Bewahrt eine explizite Homologie das Produkt und die zugehörige
   Beschleunigung? Welche Dynamik- und Zeitabbildung gehört dazu?
3. Kann dieselbe radiale Dynamik durch verschiedene effektive Dichten
   dargestellt werden, und welche zusätzlichen Messungen wären zur
   Unterscheidung nötig?
4. Ist ein aus Rotationskurven geschätztes `rho0*r0` identifizierbar, oder
   entsteht seine scheinbare Stabilität durch Parameterkovarianz,
   Profilwahl, Grenzen oder Stichprobenauswahl?
5. Wie unterscheiden sich fest deklarierte Vergleichsmodelle auf
   zurückgehaltenen äußeren Radien?
6. Falls Yoons vollständiges Modell verfügbar wird: Lässt sich der
   veröffentlichte Wert aus genau seinen Eingaben reproduzieren, und bleibt
   außerhalb des ursprünglichen Zielwertvergleichs eine neue überprüfbare
   Vorhersage übrig?

Diese Fragen werden in G1–G6 einzeln beantwortet, nicht hier vorweggenommen.

## Quellen

Siehe Plan Abschnitt 14 für vollständige Zitate. [S1] Donato et al. 2009,
arXiv:0904.4054. [S2] Milgrom 2009, arXiv:0909.5184. [S4]–[S6] Yoon 2026 /
Sejong-Pressemitteilung, siehe `yoon_2026_source_audit.md`. [S7] Dalui und
Desai, arXiv:2510.26545.
