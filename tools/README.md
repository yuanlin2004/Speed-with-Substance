# Original-precision SSD reference

`reference.py` is a starting implementation using Transformers and Accelerate checkpoint dispatch. It stages model modules from SSD when the original BF16 checkpoint exceeds the declared resident-memory budgets. It never substitutes quantized weights. It is **not yet validated on the target Spark**; validate the architecture and offloaded-versus-resident outputs on a fitting model before using its artifacts as a trusted baseline.

Install compatible `torch`, `transformers`, `accelerate`, `safetensors`, and `numpy` in an isolated environment. Record exact package versions and checkpoint revision/hashes. The script supports architectures registered with `AutoModelForCausalLM` without remote code; other architectures need an explicitly reviewed adapter.

Input JSONL contains unique `id` and `prompt` fields. Prompts are already rendered final strings, including the frozen chat template; the utility does not apply one. Optional `text` supplies the teacher-forced sequence. Fix tokenization, masks, context windows, and document boundaries externally. Keep each input bounded: a full-vocabulary artifact for one long sequence can exhaust memory. Start with a short calibration probe.

```sh
python tools/reference.py --checkpoint /models/original-bf16 \
  --input frozen-prompts.jsonl --output reference-run-001 \
  --offload /ssd/reference-offload --cpu-memory 24GiB --gpu-memory 48GiB
```

Use `--save-logprobs` on a separate, short teacher-forced shard to save FP32 full-vocabulary log probabilities plus token IDs. Candidate evaluation must replay those IDs with the same masks. Without that flag only generated responses and token IDs are archived; no full-distribution KL claim is possible. Score generated responses with the pinned benchmark's official scorer.

The output directory must be new. Archive a checkpoint content hash inventory alongside `manifest.json`; a local path alone does not identify weights. The manifest records package versions, memory placement, settings, and input hash. Offload storage needs room for the dispatched weight representation in addition to the original checkpoint. Do not use the script's elapsed reference time as candidate tok/s or serving latency. Benchmark candidate goodput separately.

This is a reference-artifact utility, not a complete quantization benchmark runner. Sampling repeats, task scoring, paired confidence bounds, streaming candidate latency, and batch-load replay remain evaluation-harness responsibilities.
