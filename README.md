AWEFonts static multi-page worldwide typography library and local font studio.

Pages: home, fonts.html, font.html?id=family-id, packs.html, studio.html, sources.html, developers.html.

Catalog: 2168 indexed families including 1960 Google Fonts, 145 Fontsource and 63 current distributable SIL Fonts families. SIL entries include OFL/license metadata and direct font file references.

Language packs fetch provider stylesheets and font binaries in the browser and create ZIP files locally. SIL packs include TTF/WOFF2 files where available. No Workers, Functions, backend, database, login or API keys. The studio imports images and exports TTF locally. Check original licenses before commercial use. Android does not universally install fonts system-wide from ZIP files.

Deploy on Cloudflare Pages with no build command and output directory /.


## Separate API hostname
Deploy `api-site/` as a second Cloudflare Pages project (root directory `api-site`, no build command, output directory `.`) and attach `fonts.api.aweconnect.dpdns.org`. Keep the main UI Pages project rooted at repository root for `fonts.aweconnect.dpdns.org`. API documentation and embed example are in `api-site/README.md`.

Production UI Pages project now serves this feature branch on `fonts.aweconnect.dpdns.org`; API-only Pages project serves `api-site/` on `fonts.api.aweconnect.dpdns.org`.


## Global source directory and multilingual studio
The source directory indexes every platform supplied in the project brief. Only fonts with redistribution rights are mirrored in the downloadable catalogue; commercial and mixed archives remain linked and are not scraped or republished without permission. The library preview uses script-specific specimen strings and explicit font loading. The local studio offers glyph grids for 30+ writing systems and generates self-contained CSS `@font-face` embeds using a data URL from a locally exported TTF. Complex-script shaping (ligatures, contextual forms and mark positioning) requires a full OpenType shaping editor; this pixel-grid tool is a local glyph prototyping studio.

API v4 options: `data-font`, `data-weights`, `data-selector`, `data-apply`, `data-size`, `data-line-height`, `data-letter-spacing`.
