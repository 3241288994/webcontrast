#!/usr/bin/env python3
"""Export whitelisted result fields from the audited CSVs. No inference."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

EXTERNAL = [
    ('wa3_base', 'Qwen2.5-3B-Instruct', 'Base', 'wa'),
    ('wa3_released', 'WebArbiter-3B', 'Released', 'wa'),
    ('wa4_base', 'Qwen3-4B', 'Base', 'wa'),
    ('wa4_released', 'WebArbiter-4B-Qwen3', 'Released', 'wa'),
    ('wa7_base', 'Qwen2.5-7B-Instruct', 'Base', 'wa'),
    ('wa7_released', 'WebArbiter-7B', 'Released', 'wa'),
    ('wa8_base', 'Qwen3-8B', 'Base', 'wa'),
    ('wa8_released', 'WebArbiter-8B-Qwen3', 'Released', 'wa'),
    ('ws3_base', 'Qwen2.5-3B-Instruct', 'Base', 'ws'),
    ('ws3_released', 'Web-Shepherd-3B', 'Released', 'ws'),
    ('ws8_base', 'Qwen3-8B', 'Base', 'ws'),
    ('ws8_released', 'Web-Shepherd-8B', 'Released', 'ws'),
    ('llama_initial', 'Llama-3.1-8B-Instruct', 'Reference', 'reference'),
    ('agentrm_released', 'AgentRM', 'Released', 'reference'),
]
METRICS = {'without', 'with', 'effect', 'flip_conditional', 'flip_coverage', 'help', 'harm'}

def load(path):
    with path.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))

def measurements(rows):
    output = {}
    for row in rows:
        if row['metric'] not in METRICS:
            continue
        key = row['metric']
        if key in output:
            raise ValueError('Duplicate metric: ' + key)
        output[key] = {k: float(row[k]) for k in ('mean', 'lower95', 'upper95')}
    for key in ('without', 'with', 'effect', 'flip_conditional', 'flip_coverage'):
        if key not in output:
            raise ValueError('Missing metric: ' + key)
    if abs(output['with']['mean'] - output['without']['mean'] - output['effect']['mean']) > 1e-8:
        raise ValueError('Effect does not equal with minus without')
    return output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--external', type=Path, required=True)
    parser.add_argument('--repair', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    external = [r for r in load(args.external) if r['cohort'] == 'all500' and r['cluster'] == 'page']
    repair = [r for r in load(args.repair) if r['cohort'] == 'all500' and r['cluster'] == 'page' and r['readout'] == 'margin']
    data = dict(schema_version=1, pages=500, websites=130, dataset_freeze='2026-10-20',
                data_sha256='8b88ce9c1bf5cecfae68b77a96773f1e3efa3e7b847f1c3647ad112d6eb01d08',
                result_export='2026-10-22', external=[], repair=[],
                sources={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (args.external, args.repair)},
                notes=['All means use the fixed 500-page set.',
                       'External rows have family-specific interfaces, not a unified leaderboard.',
                       'Repair rows average two training seeds; intervals cluster pages, not a seed population.',
                       'These are offline action judgments, not browser task success rates.'])
    for key, label, role, group in EXTERNAL:
        data['external'].append(dict(id=key, label=label, role=role, group=group,
                                     metrics=measurements([r for r in external if r['model'] == key])))
    for family, label in [('qwen', 'Qwen3-8B'), ('llama', 'Llama-3.1-8B-Instruct')]:
        for arm in ('native', 'preact_calibrated'):
            key = 'repair/' + family + '/' + arm
            data['repair'].append(dict(id=key, label=label, backbone=family,
                                       arm='Native' if arm == 'native' else 'PreAct',
                                       metrics=measurements([r for r in repair if r['configuration'] == key])))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps(dict(status='ok', external_rows=len(data['external']), repair_rows=len(data['repair']))))

if __name__ == '__main__':
    main()
