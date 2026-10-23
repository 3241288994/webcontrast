"""Portable annotation-layer export and hash-checked local assembly helpers."""
import gzip
import hashlib
import json
from pathlib import Path

def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def read_rows(path):
    path = Path(path)
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as handle:
        return [json.loads(line) for line in handle if line.strip()]

def write_rows(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')

def annotation(page, index):
    src = page['source']
    ix = src.get('index', src)
    source = dict(dataset='Mind2Web', task_id=src['task_id'])
    for key in ('official_split', 'shard', 'task_index', 'step_index', 'action_uid', 'html_sha256'):
        if key not in ix:
            raise ValueError('Missing source field for ' + page['id'] + ': ' + key)
        source[key] = ix[key]
    result = dict(schema_version=1, id=page['id'], website=page['website'],
                  category=page.get('category', ''), stratum='core300' if index < 300 else 'hard200',
                  source=source, observation_sha256=sha(page['observation']),
                  goals=page['goals'], correct_action_indices=page['correct_action_indices'],
                  actions=[{key: action.get(key) for key in ('operation', 'target_bid', 'value')} for action in page['actions']],
                  notes=[dict(action_index=i, texts={key: note['texts'][key] for key in ('phrasing1', 'phrasing2')})
                         for i, note in enumerate(page['notes'])])
    if sorted(result['correct_action_indices']) != [0, 1]:
        raise ValueError('Goals must require opposite actions')
    return result

def assemble(annotations, observations):
    by_id = {}
    for row in observations:
        if row['id'] in by_id:
            raise ValueError('Duplicate observation ID: ' + row['id'])
        by_id[row['id']] = row['observation']
    output = []
    seen = set()
    for ann in annotations:
        if ann['id'] in seen:
            raise ValueError('Duplicate annotation ID: ' + ann['id'])
        seen.add(ann['id'])
        text = by_id.get(ann['id'])
        if text is None:
            raise ValueError('Missing observation: ' + ann['id'])
        if sha(text) != ann['observation_sha256']:
            raise ValueError('Observation hash mismatch: ' + ann['id'] + '. Do not substitute raw HTML for the frozen simplified observation.')
        output.append(dict(ann, observation=text))
    return output
