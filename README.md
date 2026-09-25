# Movie & Series Title Typo Sources

A tracked index of every public dataset useful for building a **misspelled / alternate movie and series title** database: title AKA dumps, Wikipedia misspelling redirects, Wikidata aliases, and general misspelling corpora.

A GitHub Action runs **every day at 09:00 UTC**, checks each upstream download URL for a new version, and commits the result back to this repository:

- `manifest.json` — current version fingerprint of every source (ETag, Last-Modified, size, or SHA-256)
- `CHANGELOG.md` — dated log of every upstream change detected
- `data/` — mirrored copies of the small, redistributable corpora
- the `mirror-latest` release — mirrored copies of the large files
- the status table below

## Current status

<!-- STATUS:START -->
| Source | Category | Size | Upstream last modified | Last change detected | Mirrored | Download |
|---|---|---|---|---|---|---|
| [IMDb alternate titles (AKAs)](https://developer.imdb.com/non-commercial-datasets) | titles | 491.3 MB | Thu, 24 Sep 2026 12:42:54 GMT | 2026-09-25 | no | [link](https://datasets.imdbws.com/title.akas.tsv.gz) |
| [IMDb base titles](https://developer.imdb.com/non-commercial-datasets) | titles | 217.0 MB | Thu, 24 Sep 2026 12:42:02 GMT | 2026-09-25 | no | [link](https://datasets.imdbws.com/title.basics.tsv.gz) |
| [TMDB daily movie ID export](https://developer.themoviedb.org/docs/daily-id-exports) | titles | 26.8 MB | Fri, 25 Sep 2026 07:18:32 GMT | 2026-09-25 | [release asset](../../releases/tag/mirror-latest) | [link](https://files.tmdb.org/p/exports/movie_ids_09_25_2026.json.gz) |
| [TMDB daily TV series ID export](https://developer.themoviedb.org/docs/daily-id-exports) | titles | 4.8 MB | Fri, 25 Sep 2026 07:10:29 GMT | 2026-09-25 | [release asset](../../releases/tag/mirror-latest) | [link](https://files.tmdb.org/p/exports/tv_series_ids_09_25_2026.json.gz) |
| [English Wikipedia redirect table (includes R from misspelling)](https://en.wikipedia.org/wiki/Category:Redirects_from_misspellings) | titles | 178.3 MB | Thu, 03 Sep 2026 17:59:27 GMT | 2026-09-17 | [release asset](../../releases/tag/mirror-latest) | [link](https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-redirect.sql.gz) |
| [English Wikipedia page table](https://dumps.wikimedia.org/enwiki/latest/) | titles | 2.2 GB | Thu, 03 Sep 2026 17:57:41 GMT | 2026-09-17 | [release asset](../../releases/tag/mirror-latest) | [link](https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz) |
| [English Wikipedia categorylinks table](https://dumps.wikimedia.org/enwiki/latest/) | titles | 2.4 GB | Thu, 03 Sep 2026 17:20:42 GMT | 2026-09-17 | [release asset](../../releases/tag/mirror-latest) | [link](https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz) |
| [Wikidata full entity dump (aliases / also known as)](https://www.wikidata.org/wiki/Wikidata:Database_download) | titles | 96.1 GB | Thu, 24 Sep 2026 05:20:25 GMT | 2026-09-24 | no | [link](https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2) |
| [Birkbeck misspellings (Roger Mitton)](https://www.dcs.bbk.ac.uk/~roger/corpora.html) | misspellings | 360.3 KB | Thu, 19 Apr 2007 22:50:28 GMT | 2026-09-17 | [data/birkbeck-missp.dat](data/birkbeck-missp.dat) | [link](https://titan.dcs.bbk.ac.uk/~roger/missp.dat) |
| [Holbrook misspellings (Roger Mitton)](https://www.dcs.bbk.ac.uk/~roger/corpora.html) | misspellings | 24.0 KB | Mon, 21 May 2007 20:47:23 GMT | 2026-09-17 | [data/holbrook-missp.dat](data/holbrook-missp.dat) | [link](https://titan.dcs.bbk.ac.uk/~roger/holbrook-missp.dat) |
| [Aspell test misspellings (Roger Mitton)](https://www.dcs.bbk.ac.uk/~roger/corpora.html) | misspellings | 9.1 KB | Mon, 02 Apr 2007 15:43:10 GMT | 2026-09-17 | [data/aspell.dat](data/aspell.dat) | [link](https://titan.dcs.bbk.ac.uk/~roger/aspell.dat) |
| [Wikipedia misspellings (Roger Mitton)](https://www.dcs.bbk.ac.uk/~roger/corpora.html) | misspellings | 42.8 KB | Mon, 23 Apr 2007 21:58:41 GMT | 2026-09-17 | [data/wikipedia.dat](data/wikipedia.dat) | [link](https://titan.dcs.bbk.ac.uk/~roger/wikipedia.dat) |
| [Peter Norvig spell-errors.txt](https://norvig.com/ngrams/) | misspellings | 440.9 KB | Mon, 22 Apr 2019 19:47:37 GMT | 2026-09-18 | [data/norvig-spell-errors.txt](data/norvig-spell-errors.txt) | [link](https://norvig.com/ngrams/spell-errors.txt) |
| [Wikipedia lists of common misspellings (machine-readable)](https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines) | misspellings | 96.8 KB | Sat, 27 Jan 2024 15:31:36 GMT | 2026-09-17 | [data/wikipedia-common-misspellings.txt](data/wikipedia-common-misspellings.txt) | [link](https://en.wikipedia.org/w/index.php?title=Wikipedia:Lists_of_common_misspellings/For_machines&action=raw) |
<!-- STATUS:END -->

## What is mirrored and what is only tracked

| Kind | Sources | Why |
|---|---|---|
| **Mirrored in git** (`data/`) | Mitton corpora, Norvig `spell-errors.txt`, Wikipedia common misspellings | Small and freely redistributable |
| **Mirrored as release assets** ([`mirror-latest`](../../releases/tag/mirror-latest)) | TMDB daily ID exports, English Wikipedia `redirect` / `page` / `categorylinks` tables | Too large for git (GitHub blocks files over 100 MB). Files above 1.9 GB are split: rejoin with `cat NAME.part* > NAME` |
| **Tracked only** (URL + version) | IMDb datasets | IMDb's licence forbids republishing the data |
| **Tracked only** (URL + version) | Wikidata full entity dump | 96 GB, refreshed weekly: not something GitHub hosting is meant for. Use SPARQL for film and TV aliases instead |

TMDB data is mirrored unmodified with attribution: this product uses TMDB data but is not endorsed or certified by TMDB.

For tracked-only sources, download from the link in the status table. `manifest.json` tells you whether your local copy is stale.

## Usage

```bash
python3 scripts/check_updates.py
```

No dependencies beyond Python 3.9+. Add a source by appending an entry to `sources.json`:

```json
{
  "id": "unique-id",
  "name": "Human name",
  "category": "titles | misspellings",
  "url": "https://... ({MM} {DD} {YYYY} placeholders allowed for dated files)",
  "homepage": "https://...",
  "license": "...",
  "mirror": false
}
```

Set `"mirror": true` plus a `"filename"` only for small files whose licence allows redistribution.

## Sources that cannot be tracked here

These have no bulk download; they need your own account or API key:

- Google Search Console and Bing Webmaster Tools query exports (real user typos for your own site)
- TMDB `/movie/{id}/alternative_titles` and `/tv/{id}/alternative_titles` (API key)
- Wikidata SPARQL at https://query.wikidata.org/ (more practical than the 100 GB dump)

## Dead upstreams

- **GitHub Typo Corpus v1.0.0** — the official S3 bucket (`github-typo-corpus.s3.amazonaws.com`) no longer exists as of 2026-09-17. The [repository](https://github.com/mhagiwara/github-typo-corpus) still holds the code to rebuild it. Not tracked, because a deleted bucket name can be re-registered by anyone.

## Licence

Code in this repository: MIT. Each dataset stays under its own upstream licence, listed in `sources.json`. IMDb data is for personal and non-commercial use only.
