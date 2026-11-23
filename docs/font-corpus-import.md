# Font corpus import contract

AWEFonts imports real font files from local upstream snapshots. It does not invent metadata or claim that a font supports a language because the two share a Unicode script.

## Normalized family metadata

Each upstream family directory must contain `family.json` or `metadata.json`:

```json
{
  "id": "example-font",
  "canonicalId": "example-font-foundry",
  "family": "Example Font",
  "designer": "Foundry or designer",
  "provider": "SIL",
  "sourceUrl": "https://upstream.example/font",
  "license": { "id": "OFL-1.1", "url": "https://openfontlicense.org/open-font-license-official-text/" },
  "languages": ["hy"],
  "sourceFiles": [
    { "path": "files/Example-Regular.ttf", "variant": { "weight": 400, "style": "normal" } }
  ]
}
```

Required: family, id, explicit licence, and at least one real local TTF/OTF/WOFF/WOFF2 file. The importer computes SHA-256 and byte size from the actual binary. Source paths must stay inside the family directory. Language tags are only imported when explicitly supplied by the upstream source or reviewed metadata. The CSV adapter imports Glottolog rows with level `language` by default (not dialect/family records); use `--include-dialects` only when those are intentionally wanted. Exact font links are made only by Glottolog ID or ISO 639-3 tag. No script-based fallback is used.

## Download a Google Fonts snapshot

The repository includes a sparse downloader. It clones Google Fonts with Git partial-clone support, reads family metadata first, and checks out binaries only for selected families.

```sh
# First 100 families
node scripts/fetch-google-fonts.mjs --out ./upstream-fonts/google-fonts --limit 100

# Exact family selection
node scripts/fetch-google-fonts.mjs --out ./upstream-fonts/google-fonts --families "Noto Sans,Roboto"

# Full source tree; may require substantial disk space
node scripts/fetch-google-fonts.mjs --out ./upstream-fonts/google-fonts --all

# Validate local binaries and produce manifests
node scripts/sync-global-font-corpus.mjs --fonts ./upstream-fonts/google-fonts
```

The downloader records the immutable Google Fonts commit SHA and reports unrecognized licences. It does not convert subset labels into language claims: subsets are not proof that a particular language is supported. Language links require explicit language metadata or later cmap/exemplar validation. The importer accepts Glottolog `level=language` rows by default; `--include-dialects` additionally admits dialect rows, never family rows.

## Glyph-level language evidence

After importing binaries, use the optional cmap validator to compare each family’s actual Unicode character map with a sourced language exemplar set. Install its local dependency first:

```sh
python -m pip install fonttools brotli
python scripts/validate-language-cmap.py \\
  --fonts-root ./upstream-fonts/google-fonts \\
  --corpus ./v1/imported/verified-fonts.json \\
  --exemplars ./language-exemplars.json \\
  --out ./v1/imported/cmap-coverage.json
```

The exemplar input is JSON shaped like this (the exemplar text and source must come from a language-data source, not be guessed):

```json
{
  "languages": [
    {
      "id": "hy",
      "name": "Armenian",
      "sourceUrl": "https://example.org/source-record",
      "exemplarCharacters": "ԱԲԳԴԵԶԷԸԹԺԻԼԽԾԿՀՁՂՃՄՅՆՇՈՉՊՋՌՍՎՏՐՑՒՓՔՕՖաբգդեզըթժիլխծկհձղճմյնշոչպջռսվտրցւփքօֆ"
    }
  ]
}
```

By default a family qualifies only when every required exemplar letter/mark/number is present in the union of its font files’ cmap tables. The report also includes partial matches and missing codepoints. This is character-presence evidence only: it does not prove shaping, mark positioning, ligatures, orthographic correctness, or rendering quality. A language exemplar is only as complete as its cited source, and specialist review remains necessary.

## Import Unicode CLDR language exemplars

The CLDR extractor imports main exemplar characters (and optionally auxiliary characters) from a pinned Unicode CLDR checkout. It preserves the source revision, locale code, script/territory hints, and multi-character exemplar strings separately.

```sh
git clone --depth 1 https://github.com/unicode-org/cldr.git ./upstream/cldr
python scripts/import-cldr-exemplars.py \\\
  --cldr-root ./upstream/cldr \\\
  --include-auxiliary \\\
  --out ./language-exemplars/cldr.json

# Test the UnicodeSet range/escape parser without downloading CLDR
python scripts/import-cldr-exemplars.py --self-test
```

Feed that JSON directly to `validate-language-cmap.py`. CLDR covers modern locales, not all world languages; it is not a replacement for Glottolog's language-level registry. Locale IDs are not automatically treated as Glottolog or ISO 639-3 IDs. Multi-character exemplar strings are retained, but the current cmap validator checks only individual codepoint presence and cannot verify shaping.

## Run locally

```sh
node scripts/sync-global-font-corpus.mjs --fonts ./upstream-fonts --languages ./languoid.csv
node scripts/sync-global-font-corpus.mjs --fonts ./upstream-fonts --languages ./languoid.csv --write --out ./v1/imported
# Optional: include dialect-level Glottolog records too
node scripts/sync-global-font-corpus.mjs --fonts ./upstream-fonts --languages ./languoid.csv --include-dialects --write --out ./v1/imported
```

The script performs no network calls and no deployment. It creates:
- `verified-fonts.json`: unique normalized family records, binary paths, sizes and hashes.
- `world-languages.json`: language registry records; Glottolog vitality is left unknown unless a separate source field is present.
- `import-report.json`: import counts and rejected metadata files.

## Coverage policy

- One family is one family. Weights, styles, variable instances, subsets, mirrors and formats are not additional families.
- The canonical identity is a reviewed `canonicalId`, or normalized family plus designer/foundry. Name collisions are retained as possible distinct families when foundries differ.
- Each family has per-file SHA-256 hashes and an explicit licence. Redistribution is allowed only when the family licence permits it.
- Explicit language tags and reviewed character coverage are accepted evidence. Script membership alone is not.
- Historical/extinct status must be supported by a cited language-data source. Unknown remains unknown.
- Language targets (10 / 1,000 / 10,000 / 100,000) are goals, never padded inventory claims. A shortfall is displayed as a gap.

## Source repositories

- Google Fonts binaries and metadata: https://github.com/google/fonts
- Google Fonts language exemplars: https://github.com/googlefonts/lang
- Fontsource source packages: https://github.com/fontsource/fontsource
- SIL specialist fonts: https://software.sil.org/fonts/
- Noto family repositories: https://github.com/notofonts
- Open Font Library: https://fontlibrary.org
- Glottolog language registry: https://glottolog.org/meta/downloads
- Unicode CLDR: https://github.com/unicode-org/cldr

These are different source classes. Language registries and Unicode data are not font repositories. Each downloaded family must be checked independently for binary integrity, licence, source provenance and language evidence.
