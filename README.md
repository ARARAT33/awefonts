AWEFonts static multi-page worldwide typography library and local font studio.

Pages: home, fonts.html, font.html?id=family-id, packs.html, studio.html, sources.html, developers.html.

Catalog: 2168 indexed families including 1960 Google Fonts, 145 Fontsource and 63 current distributable SIL Fonts families. SIL entries include OFL/license metadata and direct font file references.

Language packs fetch provider stylesheets and font binaries in the browser and create ZIP files locally. SIL packs include TTF/WOFF2 files where available. No Workers, Functions, backend, database, login or API keys. The studio imports images and exports TTF locally. Check original licenses before commercial use. Android does not universally install fonts system-wide from ZIP files.

Deploy on Cloudflare Pages with no build command and output directory /.


## Separate API hostname
Deploy `api-site/` as a second Cloudflare Pages project (root directory `api-site`, no build command, output directory `.`) and attach `fonts.api.aweconnect.dpdns.org`. Keep the main UI Pages project rooted at repository root for `fonts.aweconnect.dpdns.org`. API documentation and embed example are in `api-site/README.md`.
