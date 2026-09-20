#!/usr/bin/env python3
"""Validate the shipped selection, local assets, and optionally source bindings."""
import argparse
import csv
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(export=None):
    data = json.loads((ROOT / 'data/questions.json').read_text())
    summaries = data['worlds']
    assert data['schemaVersion'] == 2
    worlds = []
    for summary in summaries:
        path = ROOT / summary['detail']
        assert sha(path) == summary['detailSha256']
        world = json.loads(path.read_text())
        for key in ['id', 'title', 'experiment', 'experimentLabel', 'profile', 'generator']:
            assert world[key] == summary[key]
        assert summary['question'] == world['samples'][0]['question']
        assert summary['image'] == world['samples'][0]['image']
        assert summary['sampleCount'] == len(world['samples'])
        worlds.append(world)
    assert data['worldCount'] == len(worlds)
    assert data['instanceCount'] == sum(len(w['samples']) for w in worlds)
    data['worlds'] = worlds
    selection = json.loads((ROOT / 'data/selection.json').read_text())['worlds']
    assert [w['id'] for w in data['worlds']] == [w['id'] for w in selection]
    assert len({w['id'] for w in data['worlds']}) == len(data['worlds'])
    assert len({w['recordId'] for w in data['worlds']}) == len(data['worlds'])
    expected_samples = {}
    for world in data['worlds']:
        assert world['replayStatus'] == 'verified'
        assert world['candidateId'] != 'state_switchyard_replay'
        assert len(world['samples']) == 3
        assert len({s['sha256'] for s in world['samples']}) == 3
        assert len({s['promptFamily'] for s in world['samples']}) == 1
        for sample in world['samples']:
            assert sample['question'] and sample['answer']
            if sample['options']:
                assert sample['answer'] in [str(x) for x in sample['options']], (world['id'], sample['answer'])
            image = ROOT / sample['image']
            assert image.resolve().is_relative_to(ROOT)
            assert sha(image) == sample['sha256']
            if export:
                assert sha(export / sample['sourceImage']) == sample['sha256']
            expected_samples[(world['recordId'], sample['id'])] = sample
        for program in world['programs'].values():
            assert sha(ROOT / program['path']) == program['sha256']
            if export:
                assert sha(export / program['sourcePath']) == program['sha256']
    if export:
        found = set()
        files = ['Section_1_Qeustions/sample_catalogue.csv', 'Section_2_Qeustions/sample_catalogue.csv', 'Section_3_consolidated/catalogues/samples.csv']
        for name in files:
            with (export / name).open(newline='') as f:
                for row in csv.DictReader(f):
                    key = (row['record_id'], row['example_id'])
                    if key not in expected_samples:
                        continue
                    sample = expected_samples[key]
                    assert row['question'] == sample['question']
                    assert row['answer'] == sample['answer']
                    assert row['quarantined'].lower() == 'false'
                    assert sample['sourceImage'].endswith('/' + row['image_path'])
                    assert row['prompt_family'] == sample['promptFamily']
                    found.add(key)
        assert found == set(expected_samples)
    assert len({w['experiment'] for w in data['worlds']}) == 3
    assert len({w['profile'] for w in data['worlds'] if w['profile']}) == 9
    assert len({w['generator'] for w in data['worlds']}) == 5

    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids = set()
            self.targets = []
            self.assets = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if 'id' in attrs:
                assert attrs['id'] not in self.ids, f'Duplicate DOM id: {attrs["id"]}'
                self.ids.add(attrs['id'])
            for attribute in ['href', 'src']:
                target = attrs.get(attribute)
                if not target:
                    continue
                if target.startswith('#'):
                    if len(target) > 1 and not target.startswith('#world='):
                        self.targets.append(target[1:])
                elif not urlsplit(target).scheme:
                    self.assets.append(unquote(urlsplit(target).path))

    for page in ['index.html', 'questions.html', 'steering.html']:
        links = Links()
        links.feed((ROOT / page).read_text())
        assert set(links.targets) <= links.ids
        for path in links.assets:
            assert (ROOT / path).is_file(), f'Missing local link: {path}'
    print(f'PASS: {len(data["worlds"])} worlds, {len(expected_samples)} exact question/answer/image records; {len(worlds) * 2} source files; all local HTML links.')
    if export:
        print('PASS: image and source hashes match the supplied export; question/answer pairs match source catalogue rows.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path)
    validate(parser.parse_args().export)
