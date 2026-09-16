# Anwendungsprüfung: neural-avalanche-utac

Revision 2, 16. September 2026. Grundlage: bereitgestelltes Beispiel mit Nachtrag und am 15. September geprüfter [Quellstand](https://github.com/GenesisAeon/neural-avalanche-utac/tree/2e06f35d7e3c084921b07babf330e36695e8dd6b).

## Modellkern und vorhandene Diagnostik

`HomeostaticPlasticity.update()` setzt eine diskrete Relaxation mit anschließendem Clipping um:

\[
\sigma_{n+1}=\sigma_n+r(\sigma_*-\sigma_n)\Delta t.
\]

Die zugehörige kontinuierliche ODE hat bei r>0 die lokale Rate `S_rec=r`. Im unbeschnittenen diskreten Modell ist dagegen der Störungsfaktor `m=1-r*Delta_t`, Stabilität erfordert `|m|<1`, und die Rate pro Zeit ist `-log|m|/Delta_t`. Für r=0,15/h und Δt=1 h ergibt das ungefähr 0,162519/h. Bei m=0 ist die lineare Abweichung nach einem Schritt null; die logarithmische Rate ist kein endlicher Wert. Clipping und andere Rückführungen benötigen eigene Analyse.

Die Literaturzuschreibung des Parameters ist im Code vorhanden. Diese Revision hat weder Originalmessdaten rekonstruiert noch r neu empirisch geschätzt. Der modellinterne Eigenwert wird daher nicht als neue Messung ausgegeben.

## Bereits korrigierte Aussagen

Der Γ-Rundtrip über atanh und tanh reproduziert den Ausgangswert im zulässigen Bereich. Die tatsächliche Rückkehr entsteht im separaten Relaxationsschritt. Gemeinsame η=0,5 und σ=2,2 erzeugen die gleiche Γ-Zahl in AMOC und diesem Paket durch Konstruktion.

Die überzogene Universalitätsaussage wurde bereits zurückgenommen; Rundtrip und ungenutzter E/I-Monitor sind dokumentiert, Changelog 1.0.1. Die bestehende C/R/E/P-Bridge ist keine bereits vollzogene Übersetzung nach S/K/R/V. Eine solche Übersetzung braucht echte Messdefinitionen.

## Konkreter offener Codepunkt

`effective_r()` hat im geprüften Stand keinen Zeitparameter. Sein Quotient `sum(error*delta)/sum(error^2)` schätzt bei konstantem Δt den Wert `r*Delta_t` pro Schritt. Bei anderen Abständen als einer Stunde darf er nicht unverändert als Rate pro Stunde ausgegeben werden.

Ein möglicher Korrekturweg verwendet bekannte `dt_i` und den Regressor `error_i*dt_i`:

\[
\hat r=\frac{\sum_i(error_i\Delta t_i)\,\Delta\sigma_i}{\sum_i(error_i\Delta t_i)^2}.
\]

Das ist eine modellbedingte Least-Squares-Schätzung, bei geeignetem Rauschmodell; Clipping, Messfehler im Regressor und andere Dynamik können sie verzerren. Bei Nenner null ist r aus diesen Daten nicht identifizierbar. Der vorhandene Fallback auf den Default ist dann keine empirische Schätzung. Die vorgeschlagene Δt-Korrektur wird im Verifikationsbeispiel geprüft, aber nicht als bereits ausgeführter Paketpatch behauptet.

## Selbstähnlichkeit

Eine lineare Relaxation lässt sich nach Skalierung der Zeit mit anderen linearen Relaxationsmodellen vergleichen. Das ist eine konkrete mathematische Strukturbeziehung. Eine darüber hinausgehende gemeinsame biologische/ozeanische Dynamik folgt daraus nicht; dafür wären unabhängige Messungen und unterscheidbare Vorhersagen erforderlich.

Historische Analyse: [Archiv](archive/2026-09-15/worked_example_neural_avalanche_utac.md).
