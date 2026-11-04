#!/usr/bin/env python3
"""Run a versioned benchmark command list and archive the execution record."""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', required=True, help='New directory for records and harness outputs')
    args = parser.parse_args()
    source = Path(args.manifest).resolve()
    raw = source.read_bytes()
    manifest = json.loads(raw)
    for field in ('reference_id', 'recipe_id', 'environment_id'):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            parser.error(f'Missing {field}')
    benchmark = manifest.get('benchmark', {})
    for field in ('id', 'version', 'dataset_revision', 'scorer_revision'):
        if not isinstance(benchmark.get(field), str) or not benchmark[field].strip():
            parser.error(f'Missing benchmark.{field}')
    commands = manifest.get('commands')
    if not isinstance(commands, list) or not commands:
        parser.error('commands must contain the pinned benchmark/scoring command arrays')
    for command in commands:
        if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
            parser.error('Each command must be a nonempty array of argument strings; shell strings are not accepted')
    files = manifest.get('files')
    if not isinstance(files, dict) or not files:
        parser.error('files must map benchmark/config/scorer paths to SHA256 hashes')
    for relative, expected in files.items():
        artifact = source.parent / relative
        actual = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if actual != expected:
            parser.error(f'Artifact hash mismatch: {relative}')
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output/'manifest.json').write_bytes(raw)
    driver = subprocess.run(['nvidia-smi', '--query-gpu=name,driver_version', '--format=csv,noheader'],
        capture_output=True, text=True) if __import__('shutil').which('nvidia-smi') else None
    record = {
        'manifest_sha256': hashlib.sha256(raw).hexdigest(),
        'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'platform': platform.platform(), 'python': platform.python_version(),
        'driver_query': None if driver is None else {'returncode': driver.returncode,
            'stdout': driver.stdout, 'stderr': driver.stderr},
        'steps': [], 'status': 'running',
    }
    def save():
        (output/'execution.json').write_text(json.dumps(record, indent=2)+'\n')
    save()
    environment = {**os.environ, 'SWS_OUTPUT_DIR': str(output)}
    status = 0
    try:
        for index, command in enumerate(commands):
            start = time.monotonic()
            with (output/f'step-{index:02d}.log').open('wb') as log:
                result = subprocess.run(command, cwd=source.parent, env=environment,
                    stdout=log, stderr=subprocess.STDOUT, check=False)
            record['steps'].append({'command':command, 'returncode':result.returncode,
                'elapsed_seconds':time.monotonic()-start})
            save()
            if result.returncode:
                status = result.returncode
                break
        record['status'] = 'completed' if status == 0 else 'failed'
    except BaseException:
        record['status'] = 'interrupted_or_failed'
        raise
    finally:
        record['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    raise SystemExit(status)


if __name__ == '__main__':
    main()
