# World-language coverage policy

## Counting rules
- Count a normalized font family once. Weights, styles, variable axes, subsets, formats, mirrors and provider copies are resources—not new families.
- A script match alone does not prove support for every language written in that script. Coverage needs an upstream language tag or documented glyph/character-set evidence.
- Preserve source family IDs, URLs, retrieval date, licence and redistribution permissions.
- Missing fonts remain gaps. Never add placeholders, duplicate names, relabel Latin fonts, or copy one family across languages to satisfy a target.

## Targets (not current inventory claims)

| Distribution tier | Desired distinct families per language/script profile |
|---|---:|
| Rare, endangered or extremely low-resource | 10 |
| Low distribution | 1,000 |
| Medium distribution | 10,000 |
| Wide distribution | 100,000 |

A profile must have an explicit evidence-backed `coverageTier` before its target is audited. Unclassified profiles are not silently assigned a tier.

## Current evidence boundary
The repository currently indexes 1,404 language codes, 1,695 language-script profiles and 172 script identifiers from Google Fonts language metadata, Unicode CLDR and Unicode script data. This is not a complete registry of all 7,000+ living languages. Unicode script presence does not prove that a living language has a published font.

The family catalog (2,235) and resource index (103,073) are different units. Resource records include provider face/subset records and binary files. A target of 100,000 distinct families for a widely distributed language is aspirational; if published/licensed fonts do not exist in that quantity, publish the verified count and gap.

Run `node scripts/audit-world-library.mjs` for a read-only audit. It does not scrape, modify files, build or deploy.
