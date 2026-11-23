# Google Fonts language evidence

AWEFonts imports the public `googlefonts/lang` repository at an exact Git commit. The source contains one textproto per language/script profile, including fields such as ISO 639-3 language code, ISO 15924 script code, display name, autonym, population, regions, an explicit `historical` flag, language exemplar characters and sample text.

## Evidence rules

- The `historical` boolean is copied only when the source explicitly supplies it. Population 0, an ancient script or a missing speaker count is not independently treated as proof of extinction.
- `exemplarCharacters` is built from the source's base, index, numerals, punctuation and auxiliary exemplar fields. It is language-specific source data, not a script-wide guess.
- `sampleTextCharacters` is kept separately when a source profile has sample text but no formal exemplar set. A cmap match against it proves only that the particular sample can be represented, not full orthographic coverage.
- Script and population fields are linked to Glottolog records only through exact ISO 639-3 code matches. Unmatched Glottolog records remain unassigned.
- No font coverage is inferred from the presence of a language profile. Actual font coverage requires checksums and cmap inspection of downloaded font binaries.

The importer writes `v1/language-evidence.json`, enriches `v1/languages.json`, mirrors both under `api-site/v1/`, and updates source provenance and counts in health metadata. The automated workflow also links exact profile IDs, scripts, population and explicit historical flags into Glottolog's language-level registry.
