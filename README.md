# Speed with Substance

A research-backed article proposing a quality-first evaluation protocol for quantization and inference optimization on a **single 128 GB NVIDIA DGX Spark**.

**Read the article:** https://yuanlin2004.github.io/Speed-with-Substance/

The proposal combines numerical fidelity, paired task outcomes, context and serving correctness, and quality-qualified performance. It explains the established MLPerf precedent, the limits of perplexity and aggregate accuracy, statistical non-inferiority gates, and a practical single-machine runbook.

**Results board:** https://yuanlin2004.github.io/Speed-with-Substance/results.html

The board is intentionally empty. It will contain only recipes we test and verify ourselves; experiments remain on hold. There is no submission flow.

## Status

**Funding:** We are preparing GitHub Sponsors support for benchmark maintenance and independent testing. Sponsorship is not yet live. See [the funding plan and independence policy](SPONSORSHIP.md).

Methodology proposal v1.12, November 3, 2026. No hardware benchmark results are claimed. Suggested thresholds and budgets are explicitly illustrative. This repository contains the article, a reference utility, and a benchmark-command wrapper. Actual benchmark packages will accompany future measured results.

## Edit and preview

The site is dependency-free static HTML and CSS:

- `docs/index.html`: article and primary-source references.
- `docs/results.html`: empty curated results board and publication policy.
- `docs/assets/style.css`: responsive editorial design and print styles.
- `.github/workflows/pages.yml`: GitHub Pages deployment on changes to `main`.

Preview from the repository root:

```sh
python3 -m http.server 8000 --directory docs
```

Open http://localhost:8000. Google Fonts are optional; the page uses local system/serif fallbacks if unavailable. No analytics or client-side JavaScript is included.

## Publishing

Select **Settings → Pages → Source → GitHub Actions** once. Pushing article changes to `main` runs the publishing workflow. The deployed artifact contains only `docs/`.

## Revision 1.12

Numbers all four figures and gives speed testing its own Section 5, with updated section numbering and navigation. The speed suite includes controlled tests, representative replay, and scored quality under load. Defines timing metrics, workload/load profiles, and speed reproduction requirements. Retains the four versioned records required for each result: reference, supplied recipe, environment (including driver version), and benchmark. Each future result must publish a runnable benchmark package and evidence so others can verify it. Experiments and worked examples remain deferred.

See `benchmarks/README.md` for the package contract, `tools/run_benchmark.py` for command execution and recording, and `tools/reference.py` for reference generation. The wrapper does not implement scoring or provide a benchmark dataset.

## Research scope

Primary sources are linked next to the claims they support and listed at the end of the article. Repository policies and software documentation are living sources; actual benchmark runs must pin their revisions. The SWS protocol is a synthesis and proposal, not an MLPerf certification or an established industry standard.
