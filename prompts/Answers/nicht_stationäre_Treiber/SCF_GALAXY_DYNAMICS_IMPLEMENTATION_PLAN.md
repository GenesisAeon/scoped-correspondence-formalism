# SCF: Galaxiendynamik, Flächendichten und prüfbare Strukturverwandtschaft

**Implementierungs- und Forschungsübergabe für Claude Code · 25. September 2026**

Repository: <https://github.com/GenesisAeon/scoped-correspondence-formalism>  
Ursprüngliche Architekturprüfung: `45f1ee30d006e2eae726ba6bd49db21d95e93821`.  
Aktualisierter Referenzstand einschließlich C0–C7: `4ed0cd98c52626d0e5932b15d22212ab27ad300b`.

## 1. Auftrag und wissenschaftliches Ziel

Erweitere SCF um eine klar abgegrenzte Galaxiendynamik-Domäne. Ausgangspunkt ist die Diskussion über eine annähernd charakteristische Halo-Flächendichte und Youngsub Yoons Arbeit zu Verlindes emergenter Gravitation. Die Erweiterung soll untersuchen, welche mathematischen Strukturen verschiedene Modelle teilen, welche Observablen dadurch erhalten bleiben und welche Daten ihre Unterschiede tatsächlich erkennen lassen.

Das sinnvolle Ziel ist ein **Prüfrahmen für Skalenbeziehungen, Modellabbildungen und Beobachtungsäquivalenz**. Eine neue Gravitationstheorie entsteht daraus nur, wenn zusätzlich eine eigenständige, geschlossene Dynamik mit nachvollziehbaren physikalischen Annahmen formuliert wird.

Die Arbeit hat drei Ebenen:

1. **Exakte Mathematik:** Profilkonventionen, Homologie, Zustands- und Zeitabbildung, erhaltene Observablen und explizite Gegenbeispiele.
2. **Kontrollierte Modellvergleiche:** Newtonsche Halo-Modelle und eine fest deklarierte MOND-Beziehung; Yoons konkrete Konstruktion erst nach Prüfung der vollständigen Originalquelle.
3. **Ein kleiner echter Datenpilot:** SPARC-Rotationskurven mit sauberer Komponentenrechnung, Identifizierbarkeitsprüfung und getrennten deskriptiven und prädiktiven Auswertungen.

Die Zielwerte ungefähr 138 beziehungsweise 170 Sonnenmassen pro Quadratparsec sind uns bereits bekannt. Eine nachträgliche Herleitung darf deshalb nicht als historisch blinde Vorhersage bezeichnet werden. Möglich bleiben eine überprüfbare Ableitung mit vollständig offengelegten Eingaben und vorab festgelegte Tests auf bislang in diesem Arbeitsablauf nicht ausgewerteten Daten.

**Konkreter Mehrwert für SCF:** Diese Domäne verbindet die bisherige Arbeit an Korrespondenzen und Identifizierbarkeit mit physikalischen Einheiten, geometrischen Beobachtungsoperatoren und strukturell verschiedenen Erklärungen derselben Messgröße. Es ist kein Kippmodell erforderlich. Die Galaxiendaten allein begründen insbesondere keine exponentielle Instabilität, keinen UTAC-Schwellenprozess und keine Identität zwischen Gravitation und Informationsgrößen.

## 2. Einordnung in den laufenden Repository-Stand

Die neue Serie heißt **G0–G7**. Sie ergänzt die bestehenden B- und C-Pakete. Der aktualisiert gelesene Stand von `INTEGRATED_EXTENSION_ROADMAP.md` meldet C0–C7 als erledigt; C1c, C4b, die Transportverzögerung zwischen C3/C5 und das vollständige C6-Panel bleiben ausdrücklich zurückgestellt. Ein gleichzeitig erstellter unabhängiger Review (`SCF_REVIEW_C0_C7_4ed0cd9.md`) enthält zusätzliche Korrekturen am abgeschlossenen Stand. Sicherheits- und Korrektheitsbefunde dieses Reviews vor weiterem Ausbau der betroffenen Kernmodule beheben. Die zwei ursprünglichen hydrologischen Zeitachsenfehler aus C0 sind keine erneut offenen Funde. Bestehende Arbeiten nicht überschreiben oder neu aufrollen.

Vor Beginn den tatsächlichen HEAD, die lokalen Änderungen und geltende Repository-Anweisungen lesen. Stimmen Pfade oder Schnittstellen inzwischen nicht mehr, den Plan an die vorgefundenen Strukturen anpassen und die Abweichung dokumentieren. Keine vorhandenen Änderungen verwerfen.

Anschlussstellen am gelesenen Stand:

| Vorhandener Baustein | Verwendung in der Erweiterung |
|---|---|
| `src/scoped_correspondence/correspondence/contract.py` | `ModelRef`, `StateMap`, `TimeMap`, `Scope`, `ErrorMetric`, `Correspondence`; Homologie als expliziter Vertrag |
| `src/scoped_correspondence/correspondence/approximation.py` | Endliche numerische Näherungschecks mit angegebenem Geltungsbereich |
| `src/scoped_correspondence/identifiability/profile_likelihood.py` | Geeignete vorhandene Profilwerkzeuge wiederverwenden; Parametrierung und Dimensionsgrenzen vorher prüfen |
| `scripts/run_verification_suite.py` | Neue `verify_*.py` ausdrücklich in `math` beziehungsweise `data` registrieren |
| `docs/real_data_provenance.md` und vorhandenes Manifest | Datenherkunft, Nutzungsbedingungen, Hashes und Transformationen anschließen |
| Bestehende Fähigkeitsübersicht | Exakte mathematische Fähigkeit von Pilotbefund und offener Forschung trennen |

Die bisherige Unterscheidung `flat_in_scanned_range` versus `established_unbounded` bleibt verbindlich: Ein endliches flaches Gitter beweist keine globale Unbeschränktheit. Ebenso wird aus Stichproben einer Korrespondenz kein globaler Satz. Vorhandene ungeprüfte astronomische Beispiele nicht zu empirischen Belegen dieser Erweiterung umdeklarieren.

## 3. Quellenstand und Korrektur der ursprünglichen Einordnung

### 3.1 Was belegt ist

| Aussage | Einordnung und Quelle |
|---|---|
| Donato et al. berichten einen engen Bereich für das Produkt zentraler Halo-Dichte und Kernradius | `log10(mu_h / [M_sun pc^-2]) = 2.15 ± 0.2`; die Größen entstehen durch Modellinterpretation von Beobachtungen. [S1] |
| MOND besitzt über seine Beschleunigungsskala eine charakteristische Flächendichte | `Sigma_M = a0/(2 pi G)`. Ob und wie ein vergleichbares Halo-Produkt nahe daran liegt, hängt von Interpolationsfunktion und physikalischem Regime ab. [S2] |
| Yoon berichtet eine analytische Näherung in der Größenordnung 170 | Öffentlich indexierter Abstract: `10^(2.24 ± 0.09) M_sun pc^-2`; Pressemitteilung der Sejong University bestätigt die Größenordnung. [S4–S6] |
| Eine ähnliche Regularität unterscheidet allein noch keine Dunkle-Materie- und Gravitationserklärung | Eine FIRE-2-Arbeit findet annähernd konstante Halo-Flächendichten für untersuchte Zwerggalaxien sowohl mit CDM als auch SIDM. Der dortige Massenbereich ist begrenzt, ungefähr `10^10 M_sun`. [S7] |

Numerische Umrechnung der publizierten logarithmischen Angaben:

| Angabe | Zentralwert | Untere und obere transformierte Grenze |
|---|---:|---:|
| `10^(2.15 ± 0.2)` | 141.25375446 | 89.12509381–223.87211386 |
| `10^(2.24 ± 0.09)` | 173.78008287 | 141.25375446–213.79620895 |

Alle Tabellenwerte haben die Einheit `M_sun pc^-2`. Die Transformation macht die Intervalle nicht automatisch zu vergleichbaren Konfidenzintervallen. Insbesondere darf Yoons `±0.09` ohne Volltext nicht als unabhängig gemessene gaußsche Standardabweichung behandelt werden.

### 3.2 Was zur Yoon-Arbeit noch fehlt

Die vollständige Originalrechnung war bei Erstellung dieser Übergabe über die verfügbaren Zugänge nicht lesbar. Der öffentlich belegbare bibliografische Zusammenhang lautet:

- Veröffentlichter Titel laut Universitätsmitteilung: **A characteristic phantom-halo surface-density scale in Verlinde-inspired emergent gravity**; DOI `10.1016/j.dark.2026.102462`, PII `S2212686426002499`.
- Eine SSRN-Fassung wird als **Explanation of the constant central surface density of dark matter halos in galaxies by Verlinde’s emergent gravity** geführt, SSRN `7180683`. Titel- und Versionsunterschied ausdrücklich festhalten.
- Die Universitätsmitteilung vom 23. September nennt den 20. September 2026 als Veröffentlichungstag. Der Scinexx-Beitrag erschien am 24. September. Nachrichtendatum, Paperdatum und Preprintdatum nicht gleichsetzen.
- Die Mitteilung verweist auf einen Ansatz Yoons von 2024 zum Superpositionsproblem. Eine auffindbare mögliche Vorarbeit trägt den Titel **Testing Verlinde’s emergent gravity with the low acceleration gravitational anomaly observed in wide binary stars**, PII `S221268642400133X`. Ob dies genau die verwendete Vorarbeit ist, muss anhand des Literaturverzeichnisses der 2026-Arbeit bestätigt werden.

**Quellengrenze:** Pressemitteilung und Abstract reichen für die Aussage „dieses Ergebnis wird berichtet“. Sie reichen nicht, um die Gleichungen, Parameterfreiheit, Fehlerrechnung oder Gültigkeitsbedingungen zu rekonstruieren. Eine im Code selbst erfundene Formel darf nicht `yoon_2026` heißen. G6 bleibt bis zur Beschaffung einer autorisierten Volltextfassung ausdrücklich blockiert; G0–G5 und die ehrliche Dokumentation in G7 können unabhängig davon fertiggestellt werden.

### 3.3 Welche Schlussfolgerungen zu weit gingen

Aus einer ungefähr gleichen Flächendichte folgt weder die Nichtexistenz dunkler Materie noch eine Bestätigung von SCF, UTAC, CREP oder AFET. Auch eine Entropie- oder Informationsinterpretation ist damit nicht hergeleitet. Verlindes Ansatz enthält eigene physikalische Voraussetzungen und kosmologische Skalen; deren Übernahme wäre eine zusätzliche Modellannahme [S3].

Der fruchtbare Teil der ursprünglichen Idee bleibt bestehen: **Unterschiedliche Gegenstände können gemeinsame Transformations-, Operator- und Beobachtungsstrukturen besitzen.** Diese sollen wir ausdrücklich zulassen und präzise prüfen. Der geeignete Schluss ist dann beispielsweise „diese Observable bleibt unter dieser Abbildung erhalten“, nicht „diese Theorien sind physikalisch identisch“.

## 4. Paketübersicht und Reihenfolge

| Paket | Ergebnis | Abhängigkeit | Abschlusskriterium |
|---|---|---|---|
| G0 | Quellen-, Einheiten- und Hypothesenregister | keine | Jede physikalische Eingabe und jeder behauptete Zielwert hat einen Status |
| G1 | Sphärische Profile und getrennte Flächendichtebegriffe | G0 | Formeln, Grenzfälle und unabhängige Quadraturen stimmen überein |
| G2 | Exakter Homologievertrag mit Zeitabbildung | G1 | Herleitung, numerischer Vertrag und gezielte Verletzungen geprüft |
| G3 | Kontrollmodelle und Beobachtungsäquivalenz | G1–G2 | Deklarierte Gravitation/Geometrie, keine unzulässige Theoriegleichsetzung |
| G4 | Reproduzierbarer SPARC-Adapter | G0 | Offizielle Quellen, strikte Parser, Vorzeichen und Einheiten korrekt |
| G5 | Kleiner Datenpilot und Identifizierbarkeit | G3–G4 | Deskriptive und prädiktive Ergebnisse getrennt; Ausfälle vollständig berichtet |
| G6 | Quellengetreue Yoon-Reproduktion | vollständige Quelle plus G0–G3 | Reproduktion oder konkret dokumentierte Abweichung; sonst blockiert |
| G7 | Dokumentation und Fähigkeitsbilanz | fertige Teilpakete | Grenzen, offene Punkte und tatsächlich ausgeführte Prüfungen sichtbar |

Empfohlene Ausführung: G0 → G1 → G2 → G3 → G4 → G5 → G7. G6 nach Freigabe der Quellengrundlage einschieben und G7 aktualisieren. Einen noch blockierten G6 nicht durch einen grünen Status der übrigen Pakete als erledigt erscheinen lassen.

## 5. G0 — Eingaben, Einheiten und falsifizierbare Fragen

### 5.1 Vorab festzuhaltende Fragen

1. Welche Flächendichtegröße wird jeweils verglichen: Profilparameterprodukt, tatsächliche Säulendichte, aperture-gemittelter Wert oder ein aus einem anderen Modell rückgerechneter Parameter?
2. Bewahrt eine explizite Homologie das Produkt und die zugehörige Beschleunigung? Welche Dynamik- und Zeitabbildung gehört dazu?
3. Kann dieselbe radiale Dynamik durch verschiedene effektive Dichten dargestellt werden, und welche zusätzlichen Messungen wären zur Unterscheidung nötig?
4. Ist ein aus Rotationskurven geschätztes `rho0*r0` identifizierbar, oder entsteht seine scheinbare Stabilität durch Parameterkovarianz, Profilwahl, Grenzen oder Stichprobenauswahl?
5. Wie unterscheiden sich fest deklarierte Vergleichsmodelle auf zurückgehaltenen äußeren Radien?
6. Falls Yoons vollständiges Modell verfügbar wird: Lässt sich der veröffentlichte Wert aus genau seinen Eingaben reproduzieren, und bleibt außerhalb des ursprünglichen Zielwertvergleichs eine neue überprüfbare Vorhersage übrig?

### 5.2 Dimensionsanalyse als verbindliche Kontrolle

Für eine Flächendichte gilt `[Sigma] = M L^-2`, für `G` gilt `[G] = L^3 M^-1 T^-2`. Aus `G` und dimensionslosen SCF-Kennzahlen allein lässt sich keine Flächendichte konstruieren. Dafür muss eine zusätzliche dimensionsbehaftete Skala vorliegen, etwa eine Beschleunigung `a_*`:

\[
\Sigma_* = C\,\frac{a_*}{G}.
\]

Diese Form ist zunächst eine Dimensionsaussage. Sie bestimmt weder `a_*` noch den dimensionslosen Faktor `C`. Ebenso erzeugt die zulässige Kombination `c H0` aus Lichtgeschwindigkeit und Hubble-Parameter nicht automatisch eine begründete dynamische Gleichung oder einen bestimmten Vorfaktor.

Für jede neue Skala protokollieren: Definition, Einheit, Quelle, extern festgelegt oder gefittet, verwendete Daten, Zeitpunkt ihrer Festlegung und Änderungshistorie. Ein über das bekannte Ziel 170 gewähltes `C` ist eine Kalibrierung. Eine aus unabhängig begründeten Gleichungen folgende Zahl ist eine bedingte Vorhersage dieses Modells. Diese Kategorien dürfen sich später nicht stillschweigend ändern.

### 5.3 Feste numerische Konventionen

Für die untenstehenden Regressionswerte wurden verwendet:

```text
G_SI   = 6.67430e-11                 # m^3 kg^-1 s^-2
PC_M   = 3.085677581491367e16        # m
MSUN_KG = 1.98847e30                # kg
A0_SI  = 1.2e-10                   # m s^-2; externer MOND-Eingang
G_ASTRO = 4.301047329314801e-6      # kpc (km/s)^2 M_sun^-1
```

Das sind explizite Rechenkonventionen, keine Behauptung unendlich genauer Naturkonstanten. `1 (km/s)^2/kpc = 1e6/(1000*PC_M) m/s^2`; `1 M_sun/pc^3 = 1e9 M_sun/kpc^3`. Im numerischen Kern eine Einheitenbasis wählen; an Ein- und Ausgabegrenzen konvertieren. Unbeschriftete Zahlenfelder wie `density` oder `radius` durch eindeutige Einheitenkonventionen absichern.

## 6. G1 — Profile und wirklich vergleichbare Observablen

### 6.1 Drei verschiedene Größen

Für ein sphärisches Profil mit endlicher Zentraldichte:

\[
\rho(r)=\rho_0 f(r/r_0),\qquad f(0)=1,
\]

definieren wir das **Profilparameterprodukt**

\[
\mu_h=\rho_0 r_0.
\]

Die tatsächliche zentrale Säulendichte des untrunkierten Profils ist dagegen

\[
\Sigma_{\rm col}(0)=2\int_0^\infty\rho(r)\,dr
=2\mu_h\int_0^\infty f(x)\,dx.
\]

Eine mittlere projizierte Dichte innerhalb einer endlichen Apertur ist nochmals eine andere Größe. Entsprechende Funktionen und Ergebnisspalten verschieden benennen. Keine generische `surface_density`, die abhängig vom Modell etwas anderes zurückgibt.

| Profil | Form `f(x)` | Zentrale Säulendichte | Wichtige Grenze |
|---|---|---|---|
| Burkert | `1/[(1+x)(1+x^2)]` | `(pi/2) rho0*r0` | Gesamtmasse wächst untrunkiert logarithmisch |
| Pseudoisothermisch | `1/(1+x^2)` | `pi rho0*r0` | Gesamtmasse wächst untrunkiert linear |
| NFW | `1/[x(1+x)^2]` mit Skalenwert `rho_s` | zentral divergent | `rho_s*r_s` ist ein endliches Skalenprodukt, keine endliche zentrale Dichte mal Kernradius |

Bei endlicher äußerer Trunkierung ändern sich die Säulendichtefaktoren. Die API muss dann den Trunkierungsradius mitführen. Einen NFW-Cusp nicht durch Umbenennen von `rho_s` in `rho0` in einen Kern verwandeln.

### 6.2 Exakter Burkert-Kontrollfall

Mit `x=r/r0` folgt durch direkte Integration:

\[
M(<r)=2\pi\rho_0r_0^3\left[\ln(1+x)+\frac12\ln(1+x^2)-\arctan x\right],
\]

\[
g(r)=\frac{G M(<r)}{r^2},\qquad v_c(r)=\sqrt{\frac{G M(<r)}r}.
\]

Die geschlossene Massenformel leidet bei kleinem `x` an Auslöschung. Eine konsistent geprüfte Reihenentwicklung oder andere stabile Auswertung verwenden. Der Anfang der Reihe lautet:

\[
M(<r)=4\pi\rho_0r_0^3
\left(\frac{x^3}{3}-\frac{x^4}{4}+\frac{x^7}{7}-\frac{x^8}{8}+\cdots\right).
\]

Der Umschaltpunkt ist eine numerische Entscheidung; ihn über Fehler gegen unabhängige Quadratur und Kontinuität prüfen. Für `r=0` bei endlicher Zentraldichte gelten `M=0`, `g=0`, `v_c=0`; kein ungeprüftes `0/0`. Negative Radien und nichtpositive Skalenparameter zurückweisen.

**Unabhängig nachgerechneter Referenzfall:** `rho0=0.05 M_sun/pc^3`, `r0=3 kpc`, Auswertung bei `r=r0`.

| Größe | Referenzwert |
|---|---:|
| `mu_h` | `150 M_sun/pc^2` |
| `Sigma_col(0)` | `235.6194490192345 M_sun/pc^2` |
| `M(<r0)/(rho0*r0^3)` | `1.597956070366127` |
| `M(<r0)` | `2.157240694994272e9 M_sun` |
| `g(r0)` | `3.341025353735504e-11 m/s^2` |
| `v_c(r0)` | `55.61293113984169 km/s` |

Für diese Übergabe wurden die Massen- und Säulenintegrale unabhängig numerisch integriert. Die Zahlen sind Regressionsanker, kein gemessener Galaxienbefund. Im Test eine andere Rechenroute als im Produktionscode benutzen.

### 6.3 Mindestprüfungen

- Geschlossene Masse gegen Dichtequadratur über kleine, mittlere und große dimensionslose Radien.
- Säulendichtefaktoren gegen unabhängige Quadratur.
- Positivität, Monotonie der eingeschlossenen Masse, korrekter Zentralgrenzwert.
- Konsistenz zwischen SI und astronomischen Einheiten.
- NFW-Zentraldivergenz als explizit nicht unterstützte endliche Observable; keine künstliche Zahl durch willkürliche kleine Integrationsuntergrenze.
- Trunkierte und untrunkierte Aussagen nicht vermischen.

## 7. G2 — Exakte Homologie als SCF-Korrespondenz

### 7.1 Herleitung und Geltungsbereich

Für `lambda > 0` definieren wir eine Familie verschiedener sphärischer Dichtefelder:

\[
\rho_\lambda(r)=\lambda^{-1}\rho(r/\lambda),\quad
\rho_{0,\lambda}=\rho_0/\lambda,\quad r_{0,\lambda}=\lambda r_0.
\]

Die Profilform bleibt fest. Substitution in das Massenintegral liefert:

\[
M_\lambda(<\lambda r)=\lambda^2 M(<r),\qquad
g_\lambda(\lambda r)=g(r),\qquad
v_{c,\lambda}(\lambda r)=\sqrt\lambda\,v_c(r).
\]

Damit ist `mu_h` innerhalb dieser Familie invariant. Die Aussage gilt an **korrespondierenden Radien** `r` und `lambda*r`, nicht am selben physikalischen Radius. Es handelt sich um eine Abbildung zwischen unterschiedlich skalierten Modellen; ihre Massen sind unterschiedlich. Eine Änderung der Einheit von kpc zu pc ist davon zu unterscheiden.

Für Newtonsche Testteilchen in den entsprechend skalierten statischen Potentialen setzen wir

\[
T_\lambda(\mathbf r,\mathbf v)
=(\lambda\mathbf r,\sqrt\lambda\,\mathbf v).
\]

Mit dem Phasenraum-Vektorfeld `F=(v,a)` folgt

\[
D T_\lambda\,F(z)=\sqrt\lambda\,F_\lambda(T_\lambda z),
\qquad
T_\lambda\Phi^t(z)=\Phi_\lambda^{\sqrt\lambda t}(T_\lambda z).
\]

Äquivalent: `r_lambda(t)=lambda*r(t/sqrt(lambda))`. Umlaufzeiten wachsen um `sqrt(lambda)`; Kreisfrequenzen fallen um denselben Faktor.

**API-Konvention beachten:** Im gelesenen SCF-Vertrag wird `T(source.flow(state,t))` mit `target.flow(T(state),c*t)` verglichen. Daher ist `TimeMap.constant_scale = sqrt(lambda)`. Der Kehrwert wäre in dieser Schnittstelle falsch.

Der Satz beschreibt Testteilchendynamik in vorgegebenen Feldern. Eine selbstkonsistente Entwicklung ganzer Sternverteilungen, Kollisionen, kosmologische Expansion oder eine relativistische Metrik sind damit nicht nachgewiesen. Nicht mitskalierte Baryonen, feste äußere Radien und zusätzliche physikalische Skalen können die Korrespondenz brechen.

### 7.2 Positive Kontrolle und gezielte Verletzungen

Für den Burkert-Referenzfall mit `lambda=4`:

```text
rho0_target = 0.0125 M_sun/pc^3
r0_target  = 12 kpc
mu_h_target = 150 M_sun/pc^2
M_target(<12 kpc) / M_source(<3 kpc) = 16
g_target(12 kpc) / g_source(3 kpc) = 1
v_target(12 kpc) / v_source(3 kpc) = 2
orbital_period_target / orbital_period_source = 2
```

Der Flow-Test kann zuerst mit analytischen Kreisbahnen innerhalb des dafür eingeschränkten `Scope` erfolgen. Für allgemeine Anfangszustände entweder den Vektorfeldsatz direkt prüfen oder numerische Flows mit dokumentierter Integrationsgenauigkeit verwenden. Einen Kreisbahn-Ausdruck nicht als allgemeinen Burkert-Flow anbieten. Stichproben bestätigen die Implementierung; die allgemeine Aussage kommt aus der Herleitung.

Ein einfacher Gegenfall zeigt, warum Baryonen zum Vertrag gehören: In normierten Einheiten `G=1` habe das Ausgangsmodell bei `r=1` Halo-Masse 1 und eine zentrale Punktmasse 1. Dann ist `g=2`. Unter `lambda=2` hat der skalierte Halo bei `r=2` Masse 4. Bleibt die Punktmasse 1, ist dort `g=5/4`, also nicht 2. Erst bei mittransformierter Punktmasse 4 wird `g=2` wiederhergestellt. Die Rechnung erfolgt bei positivem Radius, nicht an der Punktmassensingularität.

Weitere negative Kontrollen: falscher Zeitfaktor; Vergleich bei festem statt korrespondierendem Radius; geänderte Profilform; fester statt mitskalierter Trunkierungsradius. Verwendete Gegenbeispiele müssen eine messbare Verletzung erzeugen, nicht lediglich eine andere Benennung.

### 7.3 Numerische Sorgfalt

Position und Geschwindigkeit haben verschiedene Einheiten. Ein gemeinsamer unnormalisierter Maximalfehler über SI-Positionen und Geschwindigkeiten ist kein sinnvoller Korrespondenzmaßstab. Zustände dimensionslos normieren oder Residuen nach Koordinatenblöcken getrennt beurteilen. Toleranzen an konditionierte Größen und Solverfehler binden.

**Interpretation:** Dieser Vertrag zeigt exakt, wie ein Flächendichteprodukt und Beschleunigungen erhalten bleiben können. Er wählt keine bestimmte Flächendichte aus. Beliebige zulässige Ausgangswerte von `rho0*r0` erzeugen ihre eigene invariante Familie.

## 8. G3 — Kontrollmodelle und Beobachtungsäquivalenz

### 8.1 Effektive Dichte als expliziter Beobachtungsoperator

Für ein glattes, sphärisches, nach innen gerichtetes Beschleunigungsprofil `g(r)` gilt bei `r>0`:

\[
\rho_{\rm eff}(r)=\frac{1}{4\pi G r^2}\frac{d}{dr}\big[r^2g(r)\big].
\]

Bei festgelegter baryonischer Dichte kann man `rho_phantom = rho_eff - rho_baryon` definieren. Das ist eine Newtonsche effektive Darstellung der radialen Dynamik. Sie entscheidet nicht, ob dort Teilchenmasse liegt. Zentral vorhandene Punktmassen brauchen zusätzlich einen distributionellen Beitrag; die Ableitungsformel für `r>0` allein erfasst ihn nicht.

Daraus ergeben sich saubere Prüfungen: Ein analytisch erzeugtes Kugelprofil durch den Operator zurückgewinnen; identische `g(r)` müssen identische lokale Kreisgeschwindigkeiten ergeben; verschiedene Parametrisierungen können dieselbe Observable erzeugen. Negative effektive Restdichten nicht stillschweigend auf null setzen.

Rotationskurven in einer Scheibenebene bestimmen keine eindeutige dreidimensionale Dichte. Daher keine verrauschte SPARC-Kurve direkt differenzieren und das Ergebnis als gemessene Halo-Dichte ausgeben. Beobachtungsäquivalenz für diese Kurven bedeutet auch keine Äquivalenz für Gravitationslinsen, relativistische Potentiale oder kosmologische Strukturentwicklung.

### 8.2 Fest deklarierter MOND-Kontrollfall

Als mathematisch übersichtlichen Vergleich verwenden wir die Interpolationsfunktion

\[
\mu_{\rm M}(x)=\frac{x}{\sqrt{1+x^2}},\qquad
\mu_{\rm M}(g/a_0)g=g_N.
\]

In Kugelsymmetrie folgt für `g_N>=0`:

\[
g=\sqrt{\frac{g_N^2+g_N\sqrt{g_N^2+4a_0^2}}{2}}.
\]

Die Auswertung dimensionslos und über große Dynamikbereiche stabil implementieren. Bei `g_N=a0` ist `g/a0=1.272019649514069`; für große Beschleunigungen gilt `g/g_N -> 1`, für kleine `g/sqrt(a0*g_N) -> 1`. Der Grenzfall `g_N=0` ergibt 0; negative Eingaben sind in diesem skalaren Modell außerhalb des Geltungsbereichs.

Mit unseren Konstanten ist `Sigma_M=137.0180243872182 M_sun/pc^2`. Milgroms historische Rundung lautet 138. Seine vergleichbare Halo-Skala enthält einen Faktor abhängig von der Interpolation und gilt nicht universell für Systeme im tiefen Niedrigbeschleunigungsregime. Für die hier gewählte Funktion ergibt sein Punktmassen-Kontrollfall den Faktor 1. Die andere, oft „simple“ genannte Funktion `x/(1+x)` ist nicht austauschbar: Das zugehörige Integral für die untrunkierte zentrale Phantom-Säulendichte divergiert logarithmisch [S2]. Diese Unterscheidung soll vor falschen Kombinationen bekannter Formeln schützen.

Für Scheibengalaxien ist diese algebraische Relation im Rahmen einer modifizierten Poisson-Gravitation im Allgemeinen kein vollständiger Feldsolver. Ihr Einsatz in G5 trägt daher den Namen **algebraisches MOND-Vergleichsmodell für Rotationskurven**. Ein sphärischer Exaktheitsnachweis darf nicht auf diese Anwendung übertragen werden. Ein echter Scheiben-Feldsolver ist eine spätere, eigenständige Erweiterung mit weiteren Randbedingungen.

### 8.3 Fairer Vergleichsumfang

Baseline A: baryonische Komponenten plus sphärischer Burkert-Halo. Baseline B: dieselben baryonischen Komponenten plus sphärischer NFW-Halo als Kontrolle der Profilabhängigkeit. Baseline C: obige algebraische MOND-Beziehung mit extern festem `a0`. Baryonische Annahmen und Datenaufbereitung bleiben im jeweiligen Vergleich gleich.

Ein frei gefitteter Burkert- oder NFW-Halo ist nicht bereits eine populationsbasierte Vorhersage des gesamten ΛCDM-Modells. Ein besserer Fit beweist ebenso wenig eine bestimmte Ontologie. Im ersten Pilot geht es um bedingte Vorhersagegüte, Parameterinformation und die Wirkung unterschiedlicher Modellvoraussetzungen.

## 9. G4 — SPARC-Datenadapter und Provenienz

### 9.1 Offizielle Daten und Rechteprüfung

Primärquelle ist das astronomische SPARC-Projekt mit 175 Galaxien [S8]. Die offizielle Seite bietet direkt abrufbare Tabellen; ein ZIP-Download ist für diesen Pilot nicht erforderlich:

- Metadaten: <https://astroweb.case.edu/SPARC/SPARC_Lelli2016c.mrt>
- Komponenten und Rotationskurven: <https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt>

Die Dateien waren bei Erstellung dieser Übergabe lesbar. Es wurde keine eindeutige allgemeine Weiterverbreitungslizenz der Rohdateien verifiziert. Das ist ein offener Nutzungsbedingungen-Status, keine Behauptung eines Verbots. Das bekannte Repo-Protokoll anwenden: zunächst lokaler Download mit Herkunft und Hash, synthetische CI-Fixtures, Rohdaten erst bei dokumentierter Berechtigung einchecken. Nicht mit dem gleichnamigen biomedizinischen SPARC-Projekt oder einer fremden Zenodo-Spiegelung verwechseln.

Manifest mindestens: Original-URL, Abrufzeit UTC, Paper, Dateiversion beziehungsweise Header, SHA-256 der unveränderten Originalbytes, Lizenz-/Nutzungsstatus, Parserversion, Zeilenzahl, Auswahlkonfiguration und Hash der Ausgabedaten. Falls Text normalisiert wird, Original- und normalisierten Hash getrennt führen. Den bereits aufgetretenen CRLF/LF-Fehler nicht wiederholen; erzeugte Textartefakte mit expliziten Zeilenenden schreiben und gegebenenfalls `.gitattributes` ergänzen.

### 9.2 Schema und Validierung

Die Header definieren feste Bytebereiche. Diese auswerten oder mit explizit geprüftem festen Schema parsen; nicht auf zufällige Whitespace-Zerlegung vertrauen.

Wichtige Spalten der Komponententabelle, 1-basiert inklusive Endposition:

| Bytes | Feld | Einheit |
|---|---|---|
| 1–11 | Galaxienkennung | Text |
| 13–18 | Referenzentfernung | Mpc |
| 20–25 | Radius | kpc |
| 27–32 | beobachtete Rotationsgeschwindigkeit | km/s |
| 34–38 | angegebener Geschwindigkeitsfehler | km/s |
| 40–45 | Gasbeitrag | km/s, mit Vorzeichenkonvention |
| 47–52 | Scheibenbeitrag bei Referenz-M/L | km/s, mit Vorzeichenkonvention |
| 54–59 | Bulgebeitrag bei Referenz-M/L | km/s, mit Vorzeichenkonvention |
| 61–67 und 69–76 | Scheiben-/Bulgeflächenhelligkeit | `L_sun pc^-2` |

Zusätzlich aus der Metadatentabelle lesen: Entfernung und Fehler, Inklination und Fehler, effektive Flächenhelligkeit, Qualitätsflag und verfügbare Strukturgrößen. Die dortige Bytebeschreibung ist maßgeblich. Prüfen: eindeutige IDs, übereinstimmende Referenzentfernungen, sortierbare positive Radien, doppelte Radien, endliche Werte und positive Beobachtungsfehler. Fehlende Werte, unbekannte Flags und Inkonsistenzen erzeugen nachvollziehbare Statusmeldungen. Keine stillen Nullwerte und keine gemittelten Duplikate ohne definierte fachliche Regel.

### 9.3 Vorzeichen und baryonischer Beitrag

SPARC kodiert nach außen gerichtete Komponentenbeschleunigung durch negative Komponentenwerte. Deshalb lautet die Kombination:

\[
v_{\rm bar}^2=|v_{\rm gas}|v_{\rm gas}
+\Upsilon_d|v_d|v_d+\Upsilon_b|v_b|v_b.
\]

Die Komponenten einfach alle zu quadrieren wäre falsch. Beispiel: `v_gas=-10`, `v_disk=40`, `v_bulge=0`, `Upsilon_d=0.5` ergibt **700**, nicht 900, in `(km/s)^2`.

Der Heliumfaktor 1.33 ist im Gasbeitrag bereits berücksichtigt; nicht erneut anwenden. Die Sternkomponenten sind für M/L gleich 1 normiert. Für die erste transparente Baseline `Upsilon_d=0.5`, `Upsilon_b=0.7` vorab festlegen und ihre Rolle als externe Modellannahmen kennzeichnen. Die tabellierten `v_obs` sind bereits für die Referenzinklination korrigiert. [S8–S10]

Ist der gesamte `v_bar^2` negativ, kann das skalare MOND-Modell nicht durch Absolutwertbildung gerettet werden. Den Punkt als außerhalb dieses Vergleichsmodells markieren, Häufigkeit und Auswirkung berichten und die gemeinsame Auswertungsmenge nach einer vorher festgelegten Regel bestimmen. Ein Halo-Modell kann trotz negativem baryonischem Einzelbeitrag eine positive Gesamtbeschleunigung besitzen.

### 9.4 Entfernung und Inklination sind gemeinsame Störparameter

Bei einer Entfernungsänderung `alpha_D=D/D_ref` skalieren für festes Winkelprofil:

\[
r=\alpha_D r_{\rm ref},\qquad
v_{\rm component}^2=\alpha_D v_{\rm component,ref}^2.
\]

Für eine geänderte Inklination:

\[
v_{\rm obs}(i)=v_{\rm obs,ref}\frac{\sin i_{\rm ref}}{\sin i},
\]

mit entsprechend skaliertem tabelliertem Geschwindigkeitsfehler. Winkel intern eindeutig in Radiant umrechnen. Nicht zweimal deprojizieren.

Am gleichen Winkelort hebt sich die Entfernung in `g_bar=v_bar^2/r` auf; `g_obs=v_obs^2/r` bleibt entfernungsabhängig. Das ist eine nützliche dimensionsanalytische Kontrolle, kein Beweis einer universellen Galaxienhomologie. Entfernung und Inklination beeinflussen viele Punkte gemeinsam; sie sind keine unabhängigen Fehler pro Radius. Die angegebenen Geschwindigkeitsfehler enthalten nicht automatisch diese gesamte Unsicherheit.

Zunächst Referenzwerte fixieren. Danach dieselben vorab definierten `±1 sigma`-Sensitivitäten in allen Modellen auswerten, gegebenenfalls mit fachlich zulässigen Grenzen. Solche Sensitivitätskurven nicht als kalibrierte Konfidenzbänder ausgeben. Gemeinsame Parameterprofilierung ist ein nachfolgender Ausbau, wenn die Baseline korrekt läuft.

## 10. G5 — Kleiner Pilot mit echter Trennung von Beschreibung und Vorhersage

### 10.1 Vorab eingefrorene Stichprobe

Der Pilot soll zunächst zwölf Galaxien umfassen. Die Zahl ist eine Arbeitsbegrenzung, keine statistisch ausreichende Stichprobe für universelle Kosmologieaussagen.

Vorgeschlagene deterministische Auswahl, **vor Sichtung von Fits und Residuen festschreiben**:

1. Qualitätsflag 1 oder 2, positive Entfernung und effektive Flächenhelligkeit, Inklination 30–80 Grad, mindestens zehn gültige Radialpunkte. Die obere Inklinationsgrenze ist eine eigene Pilotentscheidung.
2. Eligible Galaxien nach `log10(SBeff)`, bei Gleichheit nach ID sortieren und möglichst gleich große untere, mittlere und obere Drittel bilden.
3. Innerhalb jedes Drittels nach SHA-256 des UTF-8-Texts `SCF-GALAXY-v1|<ID>` sortieren, bei Hashgleichheit nach ID. Die ersten vier wählen.
4. Je Drittel die ersten zwei als Entwicklung und die folgenden zwei als Evaluation kennzeichnen. Das ergibt sechs plus sechs Galaxien.

Falls ein Drittel nicht vier geeignete Objekte enthält oder die Datenstruktur anders ist, die Protokolländerung vor Modellresultaten dokumentieren. Nach einem schlechten Fit keine Ersatzgalaxie suchen. Auswahl, Ausschlüsse und Gründe vollständig als maschinenlesbare Tabelle speichern. Metadaten und Anzahl gültiger Zeilen dürfen zur Planung gelesen werden; die äußeren Testgeschwindigkeiten gehören nicht zur Modellentscheidung.

Die Daten sind öffentlich und historisch bekannt. „Zurückgehalten“ bedeutet hier: in diesem Arbeitsablauf nicht zur Auswahl von Modellen, Toleranzen oder Hyperparametern verwendet.

### 10.2 Modus A: deskriptive Parameteranalyse

Auf jeder vollständigen Kurve die deklarierte Halo-Baseline fitten und für Burkert `rho0`, `r0`, `mu_h`, Optimierungsstatus und Parametergrenzen berichten. Das ist eine Beschreibung derselben Daten, auf denen geschätzt wurde. Sie darf nicht als externe Vorhersageleistung ausgewiesen werden.

Für das Produkt direkt in den Koordinaten

\[
\psi=\log_{10}\!\left(\frac{\rho_0}{M_\odot\,pc^{-3}}\right)
+\log_{10}\!\left(\frac{r_0}{pc}\right),\qquad
\eta=\log_{10}\!\left(\frac{r_0}{pc}\right)
\]

profilieren. Dann ist `psi=log10(mu_h/[M_sun pc^-2])`. Ein vergessener Faktor 1000 zwischen kpc und pc würde das Ergebnis um drei Zehnerpotenzen verschieben. Die Kovarianz von Dichte und Radius darf nicht durch unabhängige Fehlerfortpflanzung verloren gehen.

Gegenkontrolle: Im inneren Kern gilt näherungsweise `v_c^2 ≈ (4 pi G rho0/3) r^2`. Der führende Term enthält `r0` nicht. Eine reine Innenkurve kann daher den Kernradius und damit das Produkt schwach bestimmen. Auf synthetischen Daten zeigen, wie breite Radiusabdeckung die Information verändert. Keine automatische Behauptung, dass das Produkt immer besser identifizierbar sei als seine Faktoren.

Fit in logarithmisch positiven Parametern, mit mehreren deterministischen Startwerten und protokolliertem Status. Für den ersten Durchlauf sind beispielsweise `log10(rho/[M_sun pc^-3])` von −4 bis 1 und `log10(r_scale/kpc)` von −2 bis 2.5 deklarierte Rechengrenzen. Sie sind keine astronomischen Populationsprioren. Vorab festlegen: bei Randtreffer genau eine Erweiterung um eine Dekade je betroffener Seite und erneut rechnen; bleibt der Rand aktiv, Ergebnis als grenzabhängig berichten. Ein endlicher Scan oder ein begrenzter Optimierer beweist keine globale Identifizierbarkeit.

NFW nur mit seinen eigenen Skalenparametern und passenden Observablen vergleichen. Seine Skalenproduktverteilung darf nicht in dieselbe Spalte wie ein Burkert-Zentralkernprodukt eingehen. Eine enge Verteilung auf zwölf ausgewählten Objekten ist noch keine universelle Konstante.

### 10.3 Modus B: zurückgehaltene äußere Radien

Vor jeder vollständigen deskriptiven Auswertung der sechs Evaluationsgalaxien ihre Testdaten logisch abtrennen. Modellwahl, Toleranzen, Startwertschema, Rechengrenzen und sämtliche Hyperparameter allein mit synthetischen Daten und den sechs Entwicklungsgalaxien festlegen.

Für eine Evaluationsgalaxie mit `n` geeigneten Radien nach aufsteigendem Radius:

```text
n_train = floor(0.70 * n)
training = erste n_train Radien
test = verbleibende äußere Radien
```

Mindestens sieben Trainingspunkte und drei Testpunkte verlangen. Lokale Halo-Parameter ausschließlich auf den inneren Punkten schätzen. Die äußeren Geschwindigkeiten werden einmalig zur Auswertung geöffnet. Baryonische Komponenten am Testradius dürfen als bekannte Kovariaten verwendet werden; dies ist eine **bedingte radiale Extrapolation**, keine Vorhersage aus überhaupt unbeobachteter Materieverteilung.

Anschließend kann Modus A auf den vollständigen Kurven ergänzt werden, mit eindeutig anderer Ergebnisdatei. Die zuerst berechneten Testresultate bleiben unverändert; spätere Verbesserungen erhalten einen neuen explorativen Status.

### 10.4 Ziele, Scores und Unsicherheiten

Lokale Anpassung zunächst über `chi2=sum(((v_obs-v_pred)/sigma_v)^2)` unter der ausdrücklich bedingten Annahme diagonaler Messfehler. Ungültige Gesamtgeschwindigkeiten erzeugen einen Modellfehlerstatus, keine stillen Nan-Auslassungen.

Primäre Testmetriken: MAE und RMSE in km/s je Galaxie; danach gleiches Gewicht je Galaxie. Zusätzlich Anzahl der Punkte, fehlgeschlagene Fits, Randtreffer und normierte Residuen berichten. Eine Galaxie mit vielen Radien soll die Gesamtzusammenfassung nicht unbemerkt dominieren.

Ein gaußscher Log-Score ist nur mit vollständig angegebener prädiktiver Varianz sinnvoll. Verwendet die Rechnung allein `sigma_v`, muss sie als bedingter Messfehler-Score bezeichnet werden; Parameterunsicherheit und gemeinsame Systematiken sind dann nicht abgedeckt. Kein automatisch kalibriertes 80- oder 95-Prozent-Band aus einer lokalen Hesse-Matrix behaupten. Profil-Likelihood-Schwellen ebenfalls mit ihren Voraussetzungen kennzeichnen.

Modellvergleiche je Galaxie paaren. Falls Unsicherheit der mittleren Differenz untersucht wird, ganze Galaxien resamplen, keine Radialpunkte als unabhängige neue Galaxien behandeln. Sechs Evaluationsgalaxien erlauben höchstens eine vorsichtige Pilotbeschreibung; ein schmales Bootstrapintervall ersetzt keine repräsentative Stichprobe. Eine universelle Siegerbehauptung oder starke Signifikanzsprache ist nicht das Abnahmekriterium.

### 10.5 Zwingende synthetische Kontrollen

- Burkert-generierte, ausreichend weit reichende Kurven: exakte rauschfreie Rückgewinnung innerhalb numerischer Toleranz.
- Auf innere Radien beschränkte Kurven: Verlust der Radiusinformation sichtbar machen.
- Ein Fall mit negativem Gasbeitrag; 700-gegen-900-Regression.
- Reine Einheitenänderung: identische physikalische Vorhersage und identisches dimensionsloses Ergebnis.
- Entfernungsskala und Inklinationsänderung: gemeinsame Transformation aller betroffenen Größen prüfen.
- Lecktest: Änderungen an zurückgehaltenen `v_obs` dürfen Training, Parameter und Auswahl nicht ändern, nur Testscores.
- Beobachtungsäquivalenz: zwei deklarierte Darstellungen desselben `g(r)` erzeugen dieselbe Kreisgeschwindigkeit.
- Randtreffer, fehlende Fehlerwerte und außerhalb des Modellgeltungsbereichs liegende Punkte werden sichtbar berichtet.

### 10.6 Ergebnisdateien und Abnahme

Benötigt werden: eingefrorene Auswahlkonfiguration; Provenienz; je Galaxie Modellstatus und Parameter; getrennte deskriptive und prädiktive Scoretabellen; Residuen- und Profilgrafiken; eine knappe Interpretation inklusive neutraler oder negativer Befunde. Bilder deterministisch aus Ergebnisdateien erzeugen. Ein Datenpilot ohne Ergebnisbericht ist nicht abgeschlossen; ein blockierter Datenzugang darf nicht durch synthetische Zahlen als „SPARC-Ergebnis“ ersetzt werden.

## 11. G6 — Yoon-Reproduktion mit eigenem Quellen-Gate

Nach legaler Beschaffung einer vollständigen Autor-, Preprint- oder Verlagsfassung zuerst ein Quellenmemo anlegen. Erforderlich sind:

1. Exakte Version, Titel, Datum, DOI/Preprintkennung und Gleichungsnummern.
2. Definition der vorhergesagten Observable: tatsächliche Säulendichte, Burkert-äquivalentes Produkt oder anderer Kennwert.
3. Vollständige Gleichungskette bis zum Zahlenwert; jeder angenäherte Schritt und sein Regime.
4. Alle Eingaben mit Dimensionen und Herkunft, etwa kosmologische Skalen, Profilformen oder vorher kalibrierte Beziehungen.
5. Bedeutung und Herleitung von `±0.09`; Parameterstreuung, Näherungsfehler und Messfehler getrennt.
6. Vergleichsdaten und ihre Unabhängigkeit von den zur Konstruktion verwendeten Daten.
7. Rolle der 2024-Vorarbeit und tatsächlich verwendete Superpositionsregel.

Erst danach Formeln implementieren und dimensionslos gegen Handrechnung prüfen. Falls nur eine skalare Flächendichteformel hergeleitet wird, daraus keinen vollständigen Rotationskurven-Generator erfinden. Zusätzliche Modellannahmen brauchen eigene Namen und Gültigkeitsangaben.

Zwei Ergebnisse getrennt führen: **Reproduktion des publizierten Ergebnisses** und **zusätzlicher SCF-Test**. Eine gelungene Reproduktion ist wertvoll, aber noch keine neue Bestätigung durch unabhängige Daten. Ein passender zusätzlicher Test könnte eine vorab festgelegte Abhängigkeit von baryonischer Flächenhelligkeit oder eine Kurvenform sein, sofern die Originaltheorie sie tatsächlich liefert. Keine solche Vorhersage vor der Quellenprüfung voraussetzen.

Bleibt die Quelle unzugänglich, ein offenes Issue mit konkretem fehlendem Material dokumentieren; kein Fake-Adapter, der einfach 170 zurückgibt. Bei vollständiger Quelle, aber nicht reproduzierbarem Zahlenwert, die Abweichung samt Einheiten und Eingaben berichten. Nachträgliches Nachstellen des Vorfaktors ist keine bestandene Reproduktion.

## 12. Implementierungsstruktur und Verifikation

### 12.1 Vorgeschlagene additive Struktur

Die folgenden Pfade sind Vorschläge für neu anzulegende Dateien, keine Behauptung, dass sie bereits existieren:

```text
GALAXY_DYNAMICS_ROADMAP.md
docs/galaxy_dynamics_scope.md
docs/galaxy_homology.md
docs/galaxy_pilot.md
docs/yoon_2026_source_audit.md
src/scoped_correspondence/astrophysics/units.py
src/scoped_correspondence/astrophysics/spherical_profiles.py
src/scoped_correspondence/astrophysics/galaxy_homology.py
src/scoped_correspondence/astrophysics/acceleration_relations.py
src/scoped_correspondence/validation/sparc_data.py
src/scoped_correspondence/validation/galaxy_pilot.py
verification/verify_galaxy_profiles.py
verification/verify_galaxy_homology.py
verification/verify_galaxy_observation_maps.py
verification/verify_sparc_adapter.py
verification/verify_galaxy_pilot.py
```

Nach Inspektion die bestehenden Repo-Konventionen bevorzugen. Keine zweite allgemeine Optimierungs-, Einheiten- oder Datenmanifestbibliothek bauen. Vorhandene NumPy-/SciPy-Abhängigkeiten genügen voraussichtlich für den Einstieg. Eine neue große Astronomieabhängigkeit oder ein PDE-Solver ist kein Bestandteil des Minimalpakets.

`verify_sparc_adapter.py` und ein synthetischer `verify_galaxy_pilot.py` gehören bei rein synthetischen Fixtures zu `math`, unabhängig vom Dateinamen. Ein ausdrücklich echter, lokal verfügbarer Datencheck gehört zu `data`. Neue Skripte in `_EXPLICIT_CATEGORY` registrieren. Standard-CI darf keine externen Downloads voraussetzen. Lokale echte Pilotläufe getrennt benennen; ein übersprungener Lauf ist kein bestandener Datencheck.

### 12.2 Verifikationsmatrix

| Prüfung | Unabhängige Referenz | Erwartetes Ergebnis |
|---|---|---|
| Burkert-Masse | Integration von `4*pi*r^2*rho(r)` | Übereinstimmung inklusive kleinem Radius |
| Profilprodukt/Säulendichte | Eigenständige Linienintegration | Faktoren `pi/2` beziehungsweise `pi`, nicht Gleichheit |
| Homologie | Symbolische Skalierung und analytische Kreisbahn | korrekte Massen-, Geschwindigkeits- und Zeitfaktoren |
| Homologieverletzung | nicht mitskalierte Punktmasse | Gegenbeispiel `2` versus `1.25` |
| MOND-Kontrollfall | Lösung der algebraischen Gleichung | `1.272019649514069` bei `g_N=a0` |
| SPARC-Vorzeichen | direkte Beschleunigungssumme | 700 statt 900 |
| Einheiten | unabhängige SI-Auswertung | unveränderte physikalische Aussage |
| Datenaufteilung | gezielte Änderung ausschließlich der Testzielwerte | Training und Parameter unverändert |
| Identifizierbarkeit | synthetische Innen-/Vollkurven | begrenzte Information sichtbar, kein falscher globaler Beweis |
| Quellen-Gate | fehlende Volltextgrundlage | G6 bleibt sichtbar blockiert |

Für gut konditionierte geschlossene Kontrollfälle ist beispielsweise `rtol=1e-10` plausibel; nahe null mit expliziter dimensionsloser absoluter Toleranz prüfen. Diese Zahl nicht blind auf ODE-Flows oder Parameteroptimierung übertragen. Dort unabhängige Fehlerschätzung und konditionsgerechte Toleranz verwenden. Kein Test darf denselben Hilfsalgorithmus zweimal aufrufen und das als unabhängige Bestätigung verkaufen.

Vor Implementierung relevante Herleitungen und Gegenfälle selbst nachrechnen. Nach jedem fachlichen Paket dessen Prüfungen und die vorhandene Regression ausführen. Der gelesene Runner unterstützt:

```bash
python scripts/run_verification_suite.py --category math
python scripts/run_verification_suite.py --category data
python scripts/run_verification_suite.py --category links
```

`all` umfasst am Referenzstand mathematische und Datenprüfungen, aber keine Linkprüfung. Der eingecheckte Linkprüfer prüft relative Links; externe URLs werden nur gezählt, nicht auf Erreichbarkeit getestet. Bei inzwischen geänderter CI deren tatsächliche Befehle übernehmen. Bereits grüne CI ist kein Nachweis für die neuen mathematischen oder physikalischen Aussagen.

## 13. G7 — Ergebnisformulierung und mögliche Anschlussforschung

### 13.1 Welche Aussagen nach erfolgreicher Arbeit erlaubt sind

| Befund | Angemessene Aussage | Darüber hinaus nicht belegt |
|---|---|---|
| Homologie analytisch und numerisch bestätigt | SCF beschreibt eine exakte strukturtreue Abbildung dieser Modelle | Natur muss genau diese Familie oder den Wert 170 wählen |
| Gemeinsame Kreisgeschwindigkeit bei verschiedener Darstellung | Beobachtungsäquivalenz für diese Observable und diesen Bereich | vollständige physikalische oder relativistische Identität |
| Enges geschätztes Halo-Produkt im Pilot | bedingter Befund unter Profil-, Auswahl- und Fehlerannahmen | universelle Naturkonstante |
| Ein Modell extrapoliert im Pilot besser | bessere bedingte Testleistung auf dieser Stichprobe | endgültige Entscheidung über Dunkle Materie |
| Yoons Zahl reproduziert | Originalrechnung mit dokumentierten Eingaben reproduziert | SCF habe den Wert selbst vorhergesagt |
| Keine zusätzliche Skala aus SCF ableitbar | aktueller Formalismus bestimmt keine neue gravitative Skala | strukturelle Korrespondenzen seien wertlos |

Die Abschlussübersicht muss getrennt nennen: implementiert; mathematisch begründet; synthetisch geprüft; mit echten Daten ausgeführt; explorativ; blockiert. Alle Ergebnisse auf den tatsächlichen Commit und die eingefrorene Datenkonfiguration beziehen.

### 13.2 Sinnvolle nächste Ausbauten nach diesem Einstieg

1. **Hierarchische Populationsmodelle:** Intrinsische Streuung von `mu_h` unter Messfehlern, Auswahl und Profilunsicherheit untersuchen. Erst nach belastbarer Einzelgalaxien-Identifizierbarkeit; keine konstante Populationsprior verwenden und deren Ergebnis als entdeckte Konstanz verkaufen.
2. **Geometrisch angemessene Feldmodelle:** Achsensymmetrische Potentiale beziehungsweise ein klar spezifizierter modifizierter Poisson-Solver mit Randbedingungen. Damit wird die Scheiben-Näherung aus G3 selbst prüfbar.
3. **Zusätzliche Observablen:** Linsenwirkung oder vertikale Dynamik können unterschiedliche Modellrepräsentationen auseinanderhalten. Dafür braucht jedes Modell eigene Vorhersagen und ein neues Beobachtungsmodell; Rotationskurven allein liefern diese nicht.
4. **Identifizierbarkeit als Experimentaldesign:** Welche Radien, Entfernungsinformationen oder Zusatzdaten unterscheiden die Modelle am stärksten? Dies passt zum SCF-Thema Informationswert, ohne Gravitation mit Information gleichzusetzen.
5. **Gebrochene Homologie und Approximation:** Quantifizieren, wie nicht mitskalierte Baryonen, Trunkierung oder Profilformänderungen Korrespondenzresiduen erzeugen. Im ersten Schritt direkte Fehlerfunktionen; spätere gleichmäßige Schranken nur mit vollständigen Annahmen.

Diese Punkte sind Anschlussforschung, keine stillen zusätzlichen Pflichten innerhalb des ersten Piloten. Der Kern ist bereits sinnvoll, wenn die gemeinsame Struktur exakt nachgewiesen wird und die realen Daten mehrere Erklärungen offenlassen.

## 14. Quellenverzeichnis und Zugangshinweise

Die Links sind Ausgangspunkte, keine Zusicherung dauerhaft freier Volltexte. Zugriff und Versionsstand bei der Implementierung erneut protokollieren. Nachrichten dienen dem Anlass, Gleichungen und Datenschemata den Primärquellen.

- **[S1] Donato et al. (2009):** *A constant dark matter halo surface density in galaxies.* [arXiv:0904.4054](https://arxiv.org/abs/0904.4054), [DOI:10.1111/j.1365-2966.2009.15004.x](https://doi.org/10.1111/j.1365-2966.2009.15004.x). Grundlage der zitierten empirischen Produktregularität.
- **[S2] Milgrom (2009):** *The central surface density of “dark halos” predicted by MOND.* [arXiv:0909.5184](https://arxiv.org/abs/0909.5184), [lesbare Fassung](https://arxiv.org/html/0909.5184v1), [DOI:10.1111/j.1365-2966.2009.15255.x](https://doi.org/10.1111/j.1365-2966.2009.15255.x). Interpolation und Geltungsbereich entscheidend; tatsächliche Säulendichte und vergleichbarer Halo-Parameter getrennt lesen.
- **[S3] Verlinde (2016/2017):** *Emergent Gravity and the Dark Universe.* [arXiv:1611.02269](https://arxiv.org/abs/1611.02269), [DOI:10.21468/SciPostPhys.2.3.016](https://doi.org/10.21468/SciPostPhys.2.3.016). Eigene Theorieannahmen; kein SCF-Axiom.
- **[S4] Yoon (2026), veröffentlichte Arbeit:** [DOI:10.1016/j.dark.2026.102462](https://doi.org/10.1016/j.dark.2026.102462), [Verlagskennung S2212686426002499](https://www.sciencedirect.com/science/article/pii/S2212686426002499). Volltext bei Erstellung nicht geprüft; Titelzuordnung über [S6].
- **[S5] Yoon, SSRN-Fassung:** [SSRN:7180683](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7180683). Öffentlich indexierter Abstract mit logarithmischer Ergebnisangabe; vollständige Fassung und Gleichheit mit [S4] noch prüfen.
- **[S6] Sejong University, Pressemitteilung vom 23.09.2026:** [Phys.org-Veröffentlichung](https://phys.org/news/2026-09-central-surface-density-dark-theory.html). Belegt die öffentliche Darstellung von Yoons Ergebnis, keine unabhängige Validierung. Anlassartikel: [Scinexx, 24.09.2026](https://www.scinexx.de/news/physik/neue-gravitationstheorie-passt-zu-zentraler-oberflaechendichte-von-dunkler-materie/).
- **[S7] Dalui und Desai, FIRE-2-Analyse (2025/2026):** [arXiv:2510.26545](https://arxiv.org/abs/2510.26545), [DOI:10.1016/j.dark.2026.102265](https://doi.org/10.1016/j.dark.2026.102265). Vergleich von CDM und SIDM in untersuchten Zwerggalaxien.
- **[S8] Lelli, McGaugh und Schombert (2016):** *SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves.* [arXiv:1606.09251](https://arxiv.org/abs/1606.09251), [DOI:10.3847/0004-6256/152/6/157](https://doi.org/10.3847/0004-6256/152/6/157), [offizielle Projektseite](https://astroweb.case.edu/SPARC/).
- **[S9] SPARC-Metadatentabelle:** [SPARC_Lelli2016c.mrt](https://astroweb.case.edu/SPARC/SPARC_Lelli2016c.mrt). Header mit Einheiten, Bytebereichen und Qualitätskennungen.
- **[S10] SPARC-Komponententabelle:** [MassModels_Lelli2016c.mrt](https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt). Referenzentfernung, Radien, Geschwindigkeiten, Komponenten und Flächenhelligkeiten.
- **[S11] Li et al. (2020):** *A Comprehensive Catalog of Dark Matter Halo Models for SPARC Galaxies.* [arXiv:2001.10538](https://arxiv.org/abs/2001.10538), [DOI:10.3847/1538-4365/ab700e](https://doi.org/10.3847/1538-4365/ab700e). Weiterführender Vergleichspunkt für Halo-Parametrisierung; nicht ungeprüft als Datenunabhängigkeit oder Wahrheit übernehmen.
- **[S12] Mögliche Yoon-Vorarbeit (2024):** [Verlagskennung S221268642400133X](https://www.sciencedirect.com/science/article/pii/S221268642400133X), [SSRN:4781209](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4781209). Zusammenhang und Version erst anhand der vollständigen 2026-Arbeit bestätigen.

## 15. Direkter Arbeitsauftrag an Claude Code

Übernimm diese Übergabe als additive Roadmap G0–G7. Beginne mit dem aktuellen Repository-Stand und lege den Quellen- und Annahmenstatus fest. Rechne die angegebenen Kontrollfälle unabhängig nach. Implementiere danach den mathematischen Kern, den Homologievertrag und den streng abgegrenzten SPARC-Piloten in kleinen fachlich geschlossenen Schritten. Nutze vorhandene SCF-Verträge und Verifikationskonventionen.

G6 benötigt den vollständigen Originaltext. Ist er weiterhin nicht verfügbar, dokumentiere genau diesen Blocker und schließe die unabhängig möglichen Pakete ab. Keine Formel erfinden, keine 170 in eine vermeintliche Ableitung hineinfitten und keine Modellgleichheit aus einem gemeinsamen Zahlenwert ableiten.

Der Abschlussbericht soll erklären, welche neue Fähigkeit tatsächlich entstanden ist, welche Befunde echte Daten liefern und welche Fragen offenbleiben. Er soll die ausgeführten Prüfungen, Datenversion, Commit und offenen Grenzen nennen. Keine Repository-Änderung, kein Commit oder Push wird durch dieses Dokument allein als bereits ausgeführt behauptet; veröffentliche Änderungen nur im Rahmen des für deine Sitzung erteilten Auftrags.

**Erfolg ist eine nachvollziehbare, prüfbare Verbindung von Mathematik und Beobachtung — auch wenn sie am Ende mehrere physikalische Erklärungen offenlässt.**
