#!/usr/bin/env python3
"""Copy traceable website instances from immutable paper exports.

No research code is executed. No inference or scoring is performed.
"""
import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'profile-conditioned': 'Section_1_Qeustions',
    'image-support-steered': 'Section_2_Qeustions',
    'model-feedback': 'Section_3_consolidated',
}
EXPERIMENTS = {
    'profile-conditioned': 'Profile-conditioned discovery',
    'image-support-steered': 'Image-support-steered discovery',
    'model-feedback': 'Model-feedback discovery',
}
PROFILES = {
    'tracing': 'Tracing', 'topology': 'Topology',
    'correspondence': 'Correspondence', 'search': 'Search',
    'state_tracking': 'State tracking', 'measurement': 'Measurement',
    'prior_conflict': 'Prior conflict',
    'reveal_global_structure': 'Global structure',
    'reveal_declared_transform': 'Declared transform',
}
MODELS = {
    'sol-high': 'Sol (high)', 'sol-max': 'Sol (max)',
    'luna-max': 'Luna', 'opus5': 'Opus 5',
    'deepseek-v4-flash-0731': 'DS-V4-Flash',
}


def rows(path):
    with path.open(newline='', encoding='utf-8') as handle:
        yield from csv.DictReader(handle)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_path(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file():
        raise ValueError(f'Invalid source path: {relative}')
    return path


def run(export):
    selection = json.loads((ROOT / 'data/selection.json').read_text())
    worlds = []
    for experiment, folder in SOURCES.items():
        base = export / folder
        third = experiment == 'model-feedback'
        task_file = 'catalogues/tasks.csv' if third else 'task_catalogue.csv'
        sample_file = 'catalogues/samples.csv' if third else 'sample_catalogue.csv'
        code_file = 'catalogues/source_code.csv' if third else 'source_code_catalogue.csv'
        tasks = {r['record_id']: r for r in rows(base / task_file)}
        codes = {r['record_id']: r for r in rows(base / code_file)}
        wanted = [s for s in selection['worlds'] if s['experiment'] == experiment]
        picked = {s['recordId']: [] for s in wanted}
        families = {}
        for sample in rows(base / sample_file):
            record = sample['record_id']
            if record not in picked or len(picked[record]) >= 3:
                continue
            if sample.get('quarantined', '').lower() not in ('false', '0', ''):
                continue
            if third and sample['replay_status'] != 'verified':
                continue
            family = families.setdefault(record, sample['prompt_family'])
            if sample['prompt_family'] != family:
                continue
            image = source_path(base, sample['image_path'])
            sha = digest(image)
            if any(s[2] == sha for s in picked[record]):
                continue
            picked[record].append((sample, image, sha))
        for selected in wanted:
            record = selected['recordId']
            task = tasks[record]
            if task['replay_status'] != 'verified':
                raise ValueError(f'World is not replay-verified: {record}')
            if len(picked[record]) != 3:
                raise ValueError(f'Need 3 distinct images: {record}')
            slug = selected['id']
            if any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in slug):
                raise ValueError(f'Unsafe slug: {slug}')
            dest = ROOT / 'static/questions' / slug
            dest.mkdir(parents=True, exist_ok=True)
            samples = []
            for i, (sample, image, sha) in enumerate(picked[record], 1):
                filename = f'sample-{i}{image.suffix.lower()}'
                target = dest / filename
                shutil.copyfile(image, target)
                assert digest(target) == sha
                samples.append({
                    'id': sample['example_id'],
                    'image': target.relative_to(ROOT).as_posix(),
                    'question': sample['question'], 'answer': sample['answer'],
                    'options': json.loads(sample.get('answer_options_json') or sample.get('answer_options') or '[]'),
                    'sha256': sha,
                    'sourceImage': f'{folder}/{sample["image_path"]}',
                    'promptFamily': sample['prompt_family'],
                })
            code = codes[record]
            program_files = {}
            for name, field, hash_field in [
                ('generator', 'forward_renderer_path' if third else 'forward_path', 'forward_renderer_sha256' if third else 'forward_sha256'),
                ('inverse', 'inverse_oracle_path' if third else 'inverse_path', 'inverse_oracle_sha256' if third else 'inverse_sha256'),
            ]:
                original = source_path(base, code[field])
                sha = digest(original)
                if sha != code[hash_field]:
                    raise ValueError(f'Source hash mismatch: {record} {name}')
                target = dest / f'{name}.py.txt'
                shutil.copyfile(original, target)
                program_files[name] = {
                    'path': target.relative_to(ROOT).as_posix(),
                    'sha256': sha, 'sourcePath': f'{folder}/{code[field]}',
                }
            worlds.append({
                'id': slug, 'title': selected['title'],
                'experiment': experiment, 'experimentLabel': EXPERIMENTS[experiment],
                'profile': PROFILES.get(task.get('profile')),
                'generator': MODELS[task['model_key']],
                'recordId': record, 'candidateId': task['candidate_id'],
                'replayStatus': 'verified', 'humanAdmission': task['human_admission'],
                'sourceCatalogue': f'{folder}/{task_file}',
                'samples': samples, 'programs': program_files,
            })
    order = {s['id']: i for i, s in enumerate(selection['worlds'])}
    worlds.sort(key=lambda w: order[w['id']])
    detail_root = ROOT / 'data/worlds'
    detail_root.mkdir(exist_ok=True)
    catalogue = []
    for world in worlds:
        detail_path = detail_root / f'{world["id"]}.json'
        detail_path.write_text(json.dumps(world, ensure_ascii=False, separators=(',', ':')) + '\n')
        summary = {key: world[key] for key in ['id', 'title', 'experiment', 'experimentLabel', 'profile', 'generator']}
        summary.update({
            'question': world['samples'][0]['question'],
            'image': world['samples'][0]['image'],
            'sampleCount': len(world['samples']),
            'detail': detail_path.relative_to(ROOT).as_posix(),
            'detailSha256': digest(detail_path),
        })
        other_questions = list(dict.fromkeys(s['question'] for s in world['samples'][1:] if s['question'] != summary['question']))
        if other_questions:
            summary['additionalQuestions'] = other_questions
        catalogue.append(summary)
    output = {
        'schemaVersion': 2,
        'worldCount': len(worlds),
        'instanceCount': sum(len(w['samples']) for w in worlds),
        'selectionNote': selection['note'],
        'samplePolicy': 'First three file-distinct, nonexcluded replay images in the first eligible prompt family; no model inference is performed.',
        'worlds': catalogue,
    }
    (ROOT / 'data/questions.json').write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')) + '\n')
    from build_mosaic import build
    build()
    print(f'Imported {len(worlds)} worlds and {sum(len(w["samples"]) for w in worlds)} images.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path, required=True)
    run(parser.parse_args().export.resolve())
