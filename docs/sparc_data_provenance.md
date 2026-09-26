# SPARC Data Provenance (G4, added 2026-09-26)

**Status:** license status UNRESOLVED (see below) — unlike every dataset
in [docs/real_data_provenance.md](real_data_provenance.md), the raw
SPARC files are **deliberately NOT checked into this git repository**.
Only the parser code, this documentation, and self-generated synthetic
test fixtures are committed (Johann's explicit decision, 2026-09-26).

## Why this is separate from `docs/real_data_provenance.md`

That file's own "ground rules" require a clear, confirmed license for
anything listed there. SPARC's redistribution rights were not resolved
at the time of `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` (§9.1: "Es
wurde keine eindeutige allgemeine Weiterverbreitungslizenz der
Rohdateien verifiziert. Das ist ein offener Nutzungsbedingungen-Status,
keine Behauptung eines Verbots."). This file exists so that provenance
is still fully recorded (source, retrieval time, exact bytes via
SHA-256) even though the files themselves stay outside the repo.

## The two official tables

- **Metadata table**: `SPARC_Lelli2016c.mrt`
  <https://astroweb.case.edu/SPARC/SPARC_Lelli2016c.mrt>
- **Mass-models / component table**: `MassModels_Lelli2016c.mrt`
  <https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt>
- **Paper**: Lelli, McGaugh & Schombert (2016), *SPARC: Mass Models for
  175 Disk Galaxies with Spitzer Photometry and Accurate Rotation
  Curves*, arXiv:1606.09251, DOI:10.3847/0004-6256/152/6/157.

## Retrieval record (2026-09-26)

| File | Retrieved (UTC) | Size (bytes) | SHA-256 (original bytes) | Line endings |
|---|---|---:|---|---|
| `SPARC_Lelli2016c.mrt` | 2026-09-26T11:55:23Z | 28259 | `5aa0501f6b0d881fa579030e315e7b5b6ef561a5bd3a07472f9929c7e5728243` | LF |
| `MassModels_Lelli2016c.mrt` | 2026-09-26T11:55:23Z | 269518 | `9108994b12cc401b94a1768beca61c53ec354779385c9c9cc571049f3043244c` | **CRLF** (confirmed via `od -c`) |

The CRLF terminator on the component table is exactly the failure mode
the plan warns about (§9.1: "Den bereits aufgetretenen CRLF/LF-Fehler
nicht wiederholen") — `sparc_data.py` splits lines with `str.splitlines()`
(handles both `\n` and `\r\n` correctly), never a naive `.split("\n")`.

**License status: UNRESOLVED.** The site is a public university research
page with no visible redistribution terms checked at retrieval time.
Treat any local copy as "for local verification/analysis use", not as
something to redistribute, republish, or check into a public repository,
until this is explicitly clarified (e.g. by checking the paper's data
policy or contacting the SPARC maintainers).

## Local storage (outside the repo)

Raw files are kept at `D:\mandala\scf_external_data\sparc\` on this
machine — a sibling directory of the repo, not inside it, and not
git-tracked. To reproduce locally:

```bash
mkdir -p /d/mandala/scf_external_data/sparc
curl -sSL -o /d/mandala/scf_external_data/sparc/SPARC_Lelli2016c.mrt \
  https://astroweb.case.edu/SPARC/SPARC_Lelli2016c.mrt
curl -sSL -o /d/mandala/scf_external_data/sparc/MassModels_Lelli2016c.mrt \
  https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt
sha256sum /d/mandala/scf_external_data/sparc/*.mrt  # compare against the table above
```

`verification/verify_sparc_real_local.py` looks for this exact path (or
the directory named by the `SCF_SPARC_RAW_DIR` environment variable) and
**skips cleanly (exit 0, each check explicitly marked `"skipped":
true`)** when the files aren't present — Standard-CI never needs this
download (Plan §12.1: "Standard-CI darf keine externen Downloads
voraussetzen"). A skipped run is recorded as skipped, never reported as
a passed data check (Plan §12.1's own distinction) — this file, and only
a run where the checks actually executed against the real files, is the
authoritative record that they were genuinely verified.

## Real-file byte-schema verification (2026-09-26)

Both tables' real headers were fetched and read directly (not assumed
from the plan text) before writing the parser:

- **Component table** (`MassModels_Lelli2016c.mrt`): its own
  byte-by-byte header matches `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md`
  §9.2's table **exactly**, byte range for byte range (1-11 ID, 13-18 D,
  20-25 R, 27-32 Vobs, 34-38 e_Vobs, 40-45 Vgas, 47-52 Vdisk, 54-59 Vbul,
  61-67 SBdisk, 69-76 SBbul).
- **Metadata table** (`SPARC_Lelli2016c.mrt`): the plan defers to "die
  dortige Bytebeschreibung" (§9.2) rather than giving its own byte table;
  the real header gives 1-11 Galaxy, 12-13 T, 14-19 D, 20-24 e_D, 25-26
  f_D, 27-30 Inc, 31-34 e_Inc, 35-41 L[3.6], 42-48 e_L[3.6], 49-53 Reff,
  54-61 SBeff, 62-66 Rdisk, 67-74 SBdisk, 75-81 MHI, 82-86 RHI, 87-91
  Vflat, 92-96 e_Vflat, 97-99 Q, 100-113 Ref. -- note this table has NO
  1-byte gaps between fields (fully packed), unlike the component table's
  small gaps; `sparc_data.py` encodes each table's byte ranges
  separately and explicitly rather than assuming a shared convention.
