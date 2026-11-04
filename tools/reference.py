#!/usr/bin/env python3
"""Generate frozen reference artifacts with bounded CPU/GPU and SSD offload."""
import argparse
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint', required=True, help='Local original-precision HF checkpoint directory')
    p.add_argument('--input', required=True, help='JSONL: id, prompt, optional text for teacher forcing')
    p.add_argument('--output', required=True)
    p.add_argument('--offload', required=True, help='Dedicated SSD directory with ample free space')
    p.add_argument('--cpu-memory', default='24GiB')
    p.add_argument('--gpu-memory', default='48GiB')
    p.add_argument('--max-new-tokens', type=int, default=256)
    p.add_argument('--save-logprobs', action='store_true', help='Save full-vocabulary FP32 teacher-forced logprobs per item')
    args = p.parse_args()
    import hashlib
    import time
    import numpy as np
    import torch
    import transformers
    import accelerate
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
    from accelerate import init_empty_weights, infer_auto_device_map, load_checkpoint_and_dispatch

    checkpoint = Path(args.checkpoint).resolve()
    if not checkpoint.is_dir():
        p.error('Download and pin a local checkpoint first.')
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)  # Never silently overwrite an existing baseline.
    tokenizer = AutoTokenizer.from_pretrained(checkpoint, local_files_only=True)
    config = AutoConfig.from_pretrained(checkpoint, local_files_only=True)
    with init_empty_weights():
        model = AutoModelForCausalLM.from_config(config, torch_dtype=torch.bfloat16)
    model.tie_weights()
    budgets = {'cpu': args.cpu_memory}
    if torch.cuda.is_available():
        budgets[0] = args.gpu_memory
    no_split = model._no_split_modules or []
    placement = infer_auto_device_map(model, max_memory=budgets, no_split_module_classes=no_split, dtype=torch.bfloat16)
    if all(v == 'disk' for v in placement.values()):
        raise RuntimeError('At least one module must fit in CPU/GPU execution memory; raise the budget.')
    model = load_checkpoint_and_dispatch(model, checkpoint=str(checkpoint), device_map=placement,
        offload_folder=args.offload, offload_state_dict=True, dtype=torch.bfloat16,
        no_split_module_classes=no_split)
    model.eval()
    device = next((v for v in placement.values() if v not in ('cpu', 'disk')), 'cpu')
    device = torch.device(f'cuda:{device}' if isinstance(device, int) else device)
    source = Path(args.input).read_bytes()
    manifest = {**vars(args), 'input_sha256': hashlib.sha256(source).hexdigest(),
        'torch': torch.__version__, 'transformers': transformers.__version__,
        'accelerate': accelerate.__version__, 'device_map': {k:str(v) for k,v in placement.items()},
        'precision': 'BF16 weights; FP32 log-softmax', 'timing_scope': 'quality reference, not serving performance'}
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2))
    seen = set()
    with (out/'responses.jsonl').open('w') as results, torch.inference_mode():
        for index, line in enumerate(source.decode().splitlines()):
            row = json.loads(line)
            if row['id'] in seen:
                raise ValueError('Duplicate input ID')
            seen.add(row['id'])
            tokens = tokenizer(row['prompt'], return_tensors='pt').to(device)
            start = time.monotonic()
            generated = model.generate(**tokens, do_sample=False, max_new_tokens=args.max_new_tokens,
                pad_token_id=tokenizer.eos_token_id)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            output = generated[0, tokens.input_ids.shape[1]:].cpu().tolist()
            record = {'id':row['id'], 'prompt':row['prompt'], 'prompt_ids':tokens.input_ids[0].cpu().tolist(),
                'output_ids':output, 'response':tokenizer.decode(output, skip_special_tokens=True),
                'reference_seconds':time.monotonic()-start}
            if args.save_logprobs:
                # Identical concatenated token IDs must be replayed in the candidate.
                text = row.get('text', row['prompt'])
                fixed = tokenizer(text, return_tensors='pt').to(device)
                logits = model(**fixed, use_cache=False).logits[0, :-1]
                logp = torch.log_softmax(logits.float(), dim=-1)
                ids = fixed.input_ids[0].cpu().numpy()
                filename = f'logprobs-{index:06d}.npz'
                np.savez(out/filename, token_ids=ids, logprobs=logp.cpu().numpy())
                record['teacher_forced_artifact'] = filename
            results.write(json.dumps(record)+'\n')
            results.flush()


if __name__ == '__main__':
    main()
