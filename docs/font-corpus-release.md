# Google Fonts binary corpus release

AWEFonts stores the large verified binary snapshot as GitHub Release assets, not as thousands of historical Git blobs. This keeps the website repository small while the actual redistributable font files remain hosted by GitHub.

## Automated pipeline

The workflow `.github/workflows/google-font-corpus.yml`:
1. Fetches the current Google Fonts repository revision with sparse Git checkout.
2. Reads each family's upstream `METADATA.pb` and admits only explicit OFL-1.1, Apache-2.0 or Ubuntu-Font-1.0 records.
3. Copies real TTF files and their family licence text.
4. Requires source metadata, a canonical family identity and bundled licence text.
5. Computes SHA-256 and byte size for every binary; removes exact duplicate binaries and duplicate family identities.
6. Runs the independent local-corpus importer.
7. Creates archive parts no larger than 1,500 MiB and uploads them to the GitHub Release `font-corpus-google-2026-11`.
8. Publishes a static manifest at `/v1/corpora/google-fonts.json` with release links, checksums, source revision and exact counts.

No Workers, Functions, backend, database or Cloudflare build/deployment is used by this pipeline.

## Download and restore

The release manifest lists each archive part, size and SHA-256. Download every part into the same directory and verify them against the checksums.

Linux/macOS:

```sh
cat google-fonts.tar.gz.part-* | tar -xz
```

Windows PowerShell:

```powershell
Get-Content .\google-fonts.tar.gz.part-* -AsByteStream | Set-Content google-fonts.tar.gz
tar -xzf google-fonts.tar.gz
```

The archive contains one directory per accepted family, the original font binaries, a family metadata file, the upstream licence text, and a corpus manifest. It excludes the temporary upstream Git checkout.

## Published snapshot (2026-11-23)

The first full Google Fonts import is published at [GitHub Release](https://github.com/ARARAT33/awefonts/releases/tag/font-corpus-google-2026-11): **1,992 verified families, 3,719 unique binary files, 2,356,676,768 uncompressed bytes**. The source is pinned to `06bfe0d62a98375cb09c942fa18e68bd32cff057`. The accepted licence summary is 1,989 OFL-1.1 families and 3 Ubuntu-Font-1.0 families. Two duplicate records were removed and seven families were rejected by the strict metadata/licence/binary checks. See `/v1/corpora/google-fonts.json` for the exact archive-part SHA-256 and manifest links.

## What this does not claim

- Google Fonts is one major open-font source, not every font ever created.
- A family being in the corpus does not prove support for every language using the same script.
- A Google Fonts subset label is not language-level evidence.
- This source does not provide 100,000 distinct typefaces for every widely spoken language. If the world's actual supply is below a target, the gap must remain visible.
- Commercially licensed fonts are not redistributed. Only the explicit upstream licences admitted by the workflow are included.
