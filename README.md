# AWEFonts

A static-first global font library and local Font Studio.

## Verified inventory (2026-11-23)

| Unit | Count |
|---|---:|
| Distinct font families | 2,235 |
| Provider face/subset records | 99,159 |
| Binary font files | 3,914 |
| Total resource records | 103,073 |
| Language codes | 1,404 |
| Language-script profiles | 1,695 |
| Script identifiers | 172 |
| Committed API CSS presets | 67 |

103,073 resource records are **not** 103,073 unique families. The language index comes from Google Fonts language metadata, Unicode CLDR and Unicode script data; it is not a complete registry of all 7,000+ living languages.

## Language coverage targets (not claims)
- Rare/endangered/very-low-resource: 10 distinct families.
- Low distribution: 1,000.
- Medium distribution: 10,000.
- Wide distribution: 100,000.

Only source-verified families count. Script support alone is not language support. Do not pad with duplicates, weights, subsets, mirrors or placeholders. See [coverage policy](docs/world-language-coverage.md). Run `node scripts/audit-world-library.mjs` for a read-only integrity audit.

## Pages
Home, Fonts, Specimen, Compare, Packs, Font Studio, Assets, Languages, Sources and Developers.

## Static API
Origin: `https://fonts.api.aweconnect.dpdns.org`

- `/v1/catalog.json`
- `/v1/languages.json`
- `/v1/assets-index.json` and `/v1/assets/*.json`
- `/v1/sources.json`
- `/v1/health.json`
- `/v1/css-index.json`
- `/v1/embed.v6.js`

Example:
```html
<script src="https://fonts.api.aweconnect.dpdns.org/v1/embed.v6.js"
 data-font="roboto,noto-sans-armenian" data-apply="true"
 data-selector=".article" data-size="18px" data-line-height="1.6"></script>
```

The embed loader uses AWEFonts API-origin CSS preset URLs. The preset list is a curated subset; unsupported catalog families are explicitly reported, not silently loaded from another provider. AWEFonts-hosted CSS may still reference an upstream CDN; that is not a locally mirrored binary. See [static API contract](docs/static-api-and-embed.md).

## Deployment safety
Static assets only; root directory `/`; build command empty; no Workers or Functions. Do not trigger Cloudflare builds/deployments. Keep work on `feat/awefonts-world-library-2026`; do not merge to `main` without explicit approval.


## Full-corpus import pipeline

Use `scripts/sync-global-font-corpus.mjs` to import local upstream snapshots after downloading them. It verifies that each record has a family ID, source URL, explicit licence, and real local font binaries; computes SHA-256 hashes; records exact language tags; and reports identical binaries and rejected metadata. It does not invent or infer language coverage. See [font corpus import contract](docs/font-corpus-import.md). This is an ingestion tool, not evidence that all upstream repositories have already been downloaded.

### Source snapshot workflow

For an actual Google Fonts binary snapshot, run the sparse downloader locally (Git required):

```sh
node scripts/fetch-google-fonts.mjs --out ./upstream-fonts/google-fonts --limit 100
node scripts/sync-global-font-corpus.mjs --fonts ./upstream-fonts/google-fonts
```

Use `--families "Noto Sans,Roboto"` for exact families or `--all` for the full upstream collection (large download). The downloader pins and records the upstream Git commit, preserves per-family licence metadata, and does not infer language support from subset names. Importing and committing the resulting binaries is a separate, size- and licence-reviewed step; this branch does not yet contain a bulk mirror of the Google Fonts binaries.

### Global language evidence pipeline

```sh
# Fetch the latest official Glottolog languoid registry + provenance hashes
python scripts/fetch-glottolog.py --out-dir ./upstream/glottolog

# Extract sourced modern-language exemplar characters from Unicode CLDR
# (CLDR is not a full 7,000+ language census)
git clone --depth 1 https://github.com/unicode-org/cldr.git ./upstream/cldr
python scripts/import-cldr-exemplars.py --cldr-root ./upstream/cldr --include-auxiliary --out ./language-exemplars/cldr.json
python scripts/import-cldr-exemplars.py --self-test

# Validate actual downloaded font binaries against sourced exemplars
python -m pip install fonttools brotli
python scripts/validate-language-cmap.py --fonts-root ./upstream-fonts/google-fonts --corpus ./v1/imported/verified-fonts.json --exemplars ./language-exemplars/cldr.json --out ./v1/imported/cldr-cmap-coverage.json
```

The Glottolog importer counts language-level rows separately from dialects and families. Every source snapshot records immutable provenance. Character-map matches are only codepoint evidence; shaping and full language usability need additional validation.
