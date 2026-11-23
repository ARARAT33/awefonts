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

Required: family, id, explicit licence, and at least one real local TTF/OTF/WOFF/WOFF2 file. The importer computes SHA-256 and byte size from the actual binary. Source paths must stay inside the family directory. Language tags are only imported when explicitly supplied by the upstream source or reviewed metadata.

## Run locally

```sh
node scripts/sync-global-font-corpus.mjs --fonts ./upstream-fonts --languages ./languoid.csv
node scripts/sync-global-font-corpus.mjs --fonts ./upstream-fonts --languages ./languoid.csv --write --out ./v1/imported
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
