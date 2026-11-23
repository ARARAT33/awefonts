# Verified language-to-font glyph coverage

AWEFonts checks the actual Google Fonts TTF binaries against the exact character data from the pinned Google Fonts language dataset.

## Evidence types

- **Language exemplar:** every required letter/mark/number codepoint in the sourced language exemplar is present in the font's cmap.
- **Sample text only:** every required codepoint in a cited sample passage is present. This proves that passage can be represented, not that the font covers the full language orthography.
- **No complete cmap match:** at least one sourced character set was checked, but no family contained every required codepoint.
- **Unverified:** no usable character evidence exists for that language-script profile.

The workflow downloads the checksummed GitHub Release corpus, re-runs the binary importer and SHA-256 checks, inspects font cmap tables with FontTools, and links exact Google Fonts provider IDs to canonical AWEFonts family IDs. It stores profile-level evidence at `/v1/language-cmap-coverage.json` and adds matching family IDs to Glottolog language records.

## Important limitations

Cmap checks prove codepoint presence only. They do not validate shaping, OpenType substitutions, mark positioning, ligatures, script direction, line breaking, language orthography or rendering quality. A multi-script language record keeps separate results per script profile; the union of those results is not a claim that one font supports every script. Historical flags are source flags, not independent proof that a language is extinct. Population value 0 is treated as unreported in the UI.
