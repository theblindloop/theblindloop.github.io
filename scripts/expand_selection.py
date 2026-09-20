#!/usr/bin/env python3
"""Index all replay-verified worlds, retaining the explicit website exclusions."""
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from import_questions import ROOT, SOURCES, rows


def expand(export):
    featured = json.loads((ROOT / 'data/featured.json').read_text())['worlds']
    overrides = {(w['experiment'], w['recordId']): w for w in featured}
    excluded_ids = json.loads((ROOT / 'data/exclusions.json').read_text())['candidateIds']
    buckets = defaultdict(list)
    included = {}
    exclusions = []
    for experiment, folder in SOURCES.items():
        catalogue = 'catalogues/tasks.csv' if experiment == 'model-feedback' else 'task_catalogue.csv'
        for task in rows(export / folder / catalogue):
            if task['replay_status'] != 'verified':
                continue
            if task['candidate_id'] in excluded_ids:
                exclusions.append({'experiment': experiment, 'recordId': task['record_id'], 'reason': excluded_ids[task['candidate_id']]})
                continue
            key = (experiment, task['record_id'])
            slug = re.sub(r'[^a-z0-9]+', '-', task['candidate_id'].lower()).strip('-')[:72]
            suffix = hashlib.sha256(task['record_id'].encode()).hexdigest()[:10]
            world = overrides.get(key) or {
                'id': f'{experiment}-{slug}-{suffix}',
                'experiment': experiment,
                'recordId': task['record_id'],
                'title': task['candidate_id'].replace('_', ' ').replace('-', ' ').capitalize(),
            }
            included[key] = world
            if key not in overrides:
                buckets[(experiment, task.get('profile', ''), task['model_key'])].append(world)
    selected = [included[(w['experiment'], w['recordId'])] for w in featured if (w['experiment'], w['recordId']) in included]
    # Interleave configurations/profiles/experiments, rather than sorting by one model.
    queues = [sorted(bucket, key=lambda w: hashlib.sha256(w['recordId'].encode()).hexdigest()) for _, bucket in sorted(buckets.items())]
    for index in range(max(map(len, queues), default=0)):
        selected.extend(queue[index] for queue in queues if index < len(queue))
    assert len(selected) == len(included)
    assert len({w['id'] for w in selected}) == len(selected)
    output = {
        'note': 'Replay-verified worlds from the three supplied discovery exports, subject to the explicit website exclusions. Featured worlds lead; remaining worlds are interleaved across experiments, profiles, and coding agents. Automated agreement does not establish human validity.',
        'exclusions': exclusions,
        'worlds': selected,
    }
    (ROOT / 'data/selection.json').write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n')
    print(f'Selected {len(selected)} worlds; {len(exclusions)} explicit website exclusions.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path, required=True)
    expand(parser.parse_args().export.resolve())
