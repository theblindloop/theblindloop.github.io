#!/usr/bin/env python3
"""Build a static, clickable header mosaic from the unchanged question images."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    worlds = json.loads((ROOT / 'data/questions.json').read_text())['worlds']
    tiles = []
    # A bounded header: one instance from each of 72 different worlds.
    for world in worlds[:72]:
        label = html.escape(f'{world["title"]}, instance 1', quote=True)
        path = html.escape(world['image'], quote=True)
        link = html.escape(f'#world={world["id"]}&sample=1', quote=True)
        tiles.append(f'<a class="mosaic-tile" href="{link}" aria-label="Try {label}"><img src="{path}" alt="" decoding="async"><span>{html.escape(world["title"])}</span></a>')
    markup = '<div class="question-mosaic" aria-label="Recorded question images">\n' + '\n'.join(tiles) + '\n</div>'
    path = ROOT / 'index.html'
    text = path.read_text()
    start = text.index('<!-- MOSAIC:START -->') + len('<!-- MOSAIC:START -->')
    end = text.index('<!-- MOSAIC:END -->')
    path.write_text(text[:start] + '\n' + markup + '\n        ' + text[end:])
    print(f'Built a {len(tiles)}-image clickable mosaic.')


if __name__ == '__main__':
    build()
