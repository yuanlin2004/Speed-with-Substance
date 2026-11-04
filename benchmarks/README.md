# Versioned benchmark packages

No measured runs or benchmark packages have been published yet. Experiments remain on hold.

Every published result must link to a package at an immutable commit or release. The package must include:

- Reference, recipe, environment, and benchmark IDs, each with an immutable version.
- A setup document with driver version, hardware/OS, pinned runtime/container dependencies, and commands to start the supplied recipe.
- Exact benchmark data, or pinned acquisition/generation instructions when redistribution is not permitted, including dataset revision, split, item IDs, checksums, generation seeds, and request order.
- Prompt templates, context/output limits, decoding policy, workload arrival/load settings, official scorer revision and configuration, confidence method, quality gates, latency limits, and error accounting.
- Commands/scripts to run both reference and candidate (or retrieve hashed frozen reference artifacts), score the outputs, and reproduce the paired decision and performance summary.
- Raw per-item outputs/scores and timing records from the published run. The scripts must produce machine-readable outputs, not just a chart. State tolerances and compare reproduced decisions and performance with uncertainty; a rerun need not produce bitwise-identical generations.

The benchmark version identifies the **entire test contract**, not just the dataset. Changing a prompt, sample subset, scorer, decoding budget, load schedule, or decision rule requires a new version. Preserve old versions so old results can be checked. Do not compare ranks across incompatible benchmark versions.

## Speed suite

The same versioned benchmark package must include a dedicated speed suite alongside quality evaluation:

- Controlled input/output-length tests, representative prompt replay, and scored quality-under-load runs, labeled separately.
- Short-interaction, generation-heavy, long-context, and mixed profiles, with exact lengths/distributions, IDs, budgets, counts, seeds, and cache state.
- Concurrency sweeps through 1/2/4/8/16/32 where feasible, and a separately labeled fixed-arrival-schedule replay. Preregister stop conditions and retain failed operating points.
- A pinned load generator with timing boundaries, token-versus-chunk timing semantics, warm-up exclusions, request timeouts, and workload drain policy.
- Per-request TTFT, decode ms/token, end-to-end latency, counts and stop reasons; aggregate output tok/s and completions/s over declared wall time; resource/startup costs and independent-run variation.
- Actual scored responses and SLO decisions to recompute goodput. Never estimate it by multiplying throughput by accuracy from another run. Publish SLO-compliant throughput when correctness is ungraded.
- Scripts and commands to reproduce all tables, confidence summaries, and quality decisions. Preserve the raw traces and error records. Pair aggregate tok/s with per-stream ms/token; their values are not reciprocals.

The SSD reference is a quality baseline, not a serving-speed baseline. Rank only matching workloads and latency limits. The current wrapper launches external benchmark commands; a streaming load generator and metric implementation must accompany each measured result. No speed experiments have been performed.

## Execution wrapper

`tools/run_benchmark.py` runs the package's pinned commands sequentially, checks specified input hashes, and archives the manifest, command logs, actual driver query, runner hash, and step exit codes. It does not implement benchmark scoring or convert successful command execution into a quality pass. Official benchmark harnesses and their output adapters must be provided/pinned by each package.

The JSON manifest requires `reference_id`, `recipe_id`, `environment_id`, and a `benchmark` object with nonempty `id`, `version`, `dataset_revision`, and `scorer_revision`. `files` maps package-relative input/config/scorer paths to SHA256 digests. `commands` is a nonempty list of argument arrays, executed without a shell from the manifest directory. Each command must honor the package's output-path contract; `SWS_OUTPUT_DIR` points to a new results directory. Pin the execution wrapper commit as well.

After installing the package's pinned dependencies and starting its prescribed endpoint, run:

```sh
python tools/run_benchmark.py --manifest /path/to/package/run.json --output /path/to/new-results
```

Publish the exact command and manifest with the result. Keep credentials in environment variables, not command arguments, manifests, or public logs. Inspect artifacts for secrets before publishing. The wrapper records driver information on the host where it runs; if the endpoint runs on a separate Spark, the package must collect that Spark's environment separately. Its wall time includes command and scorer overhead and is **not** a serving latency or goodput measurement.

The wrapper has not been validated against a Spark benchmark run. No example result or synthetic leaderboard entry is included.

## Failed and inconclusive evaluations

Publish verified failed and inconclusive evaluations on the unranked board, with the same four versioned identities and reproducibility requirements as passing results. Include the decision rule, affected task/load slice, observed gate results, paired counts and confidence bounds where available, error logs, completed test coverage, and wall-clock cost. Explain missing evidence and what would resolve an inconclusive result.

Record execution status separately from quality status. An incomplete run or resource error does not establish a quality regression unless it violates a declared critical gate. Preserve valid partial measurements and label unavailable fields explicitly; do not invent zero values or infer goodput. Any measured speed is diagnostic and does not confer ranking eligibility. Link retests to earlier immutable records and document corrections rather than silently replacing unfavorable results.
