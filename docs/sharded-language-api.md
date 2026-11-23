# Sharded static language coverage API

The language registry and glyph-coverage results are published as small static JSON indexes plus deterministic detail shards. This avoids a single oversized Pages asset and lets clients fetch only the language/script records they need.

- `/v1/language-registry.json` contains the searchable Glottolog summary index.
- `/v1/language-registry/shards/registry-NNN.json` contains full language records, including all matching family IDs and per-script evidence.
- `/v1/language-cmap-coverage.json` contains the searchable language-script coverage summary.
- `/v1/language-cmap-coverage/shards/cmap-NNN.json` contains full matching and partial family lists for each profile.

Each summary record has a `detailsShard` path. Shard sizes and counts are included in the indexes and health endpoint. The sharding script is deterministic and can be rerun after refreshed source data.
