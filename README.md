# Speed with Substance

A research-backed article proposing a quality-first evaluation protocol for quantization and inference optimization on a **single 128 GB NVIDIA DGX Spark**.

**Read the article:** https://yuanlin2004.github.io/Speed-with-Substance/

The proposal combines numerical fidelity, paired task outcomes, context and serving correctness, and quality-qualified performance. It explains the established MLPerf precedent, the limits of perplexity and aggregate accuracy, statistical non-inferiority gates, and a practical single-machine runbook.

## Status

Methodology proposal, November 3, 2026. No hardware benchmark results are claimed. Suggested thresholds and budgets are explicitly illustrative. This repository contains the article, not an implemented evaluation harness.

## Edit and preview

The site is dependency-free static HTML and CSS:

- `docs/index.html`: article and primary-source references.
- `docs/assets/style.css`: responsive editorial design and print styles.
- `.github/workflows/pages.yml`: GitHub Pages deployment on changes to `main`.

Preview from the repository root:

```sh
python3 -m http.server 8000 --directory docs
```

Open http://localhost:8000. Google Fonts are optional; the page uses local system/serif fallbacks if unavailable. No analytics or client-side JavaScript is included.

## Publishing

Select **Settings → Pages → Source → GitHub Actions** once. Pushing article changes to `main` runs the publishing workflow. The deployed artifact contains only `docs/`.

## Research scope

Primary sources are linked next to the claims they support and listed at the end of the article. Repository policies and software documentation are living sources; actual benchmark runs must pin their revisions. The SWS protocol is a synthesis and proposal, not an MLPerf certification or an established industry standard.
