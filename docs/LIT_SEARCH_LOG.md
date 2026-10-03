# Literature search and verification log

Date: 3 October 2026. Status: bibliographic verification completed for 56 DOI
records; closest-ten full-text review and novelty/patent review remain pending.

The uploaded reference list was treated as leads. `analysis/reference_search.py`
queried Crossref for 46 titles, followed by six broad and five targeted recent
queries covering loop scheduling, stealing, simulation, small clusters, and
constrained topologies. Crossref's observed public limit is one request per
second and one concurrent request; failed requests were recorded and retried
serially after that diagnosis. Canonical DOI queries corrected misleading matches.

`analysis/curate_references.py` selects reviewed author/title/year records,
deduplicates DOI and exports bibliographic facts without abstracts or publisher
text. See `reference_records.json`, `LITERATURE_MATRIX.md`, and `../refs.bib`.
**26 of 56** records date from 2019 onward. Software/methodology references and
papers about heterogeneous, dependent, or shared-memory work are labeled as
background with explicit boundaries, not direct competitors. Existence checks
are not presented as completed full-paper reading.

Rejected examples include Spectral Graph Theory matching a different chapter,
Regular Polytopes matching Johnson, Ray matching an unrelated article, Borg
Next Generation matching a poem, MapReduce matching different authors, Holm
matching Shaffer, and UTS lacking a deposited publication year. Blumofe/Leiserson
uses canonical JACM 1999 DOI rather than its conference version. The official
JMLR Demsar record was retrieved but is not used to inflate the DOI-only count.
Holm's original record and Coxeter's publisher record remain unverified in this
session; the legacy geometry reference is explicitly flagged.

The provisional closest ten are marked in the matrix. Semantic Scholar supplied
author-copy leads for Cybenko, Loh and Gast et al.; others were closed, empty, or
not found. `reading_access.json` records attempts to follow the ten canonical
DOIs: most returned proxy or publisher 403, and IEEE returned HTTP 202 without
usable paper text. No access challenge or paywall was bypassed. Additions for
observed publisher/author-copy domains are saved for environment review.
Direct author-copy retrievals were also attempted and returned tunnel 403;
`author_copy_access.json` records those outcomes.

Full text, methods, information assumptions, actual algorithms and attributed
claims must be read and recorded before closing the literature gate. The ten
closest reviews, remaining journal rules, patent search, and novelty assessment
are incomplete. Abstracts and metadata cannot close those items.
