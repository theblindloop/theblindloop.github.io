#!/usr/bin/env python3
"""Read original pixels for the method illustration; never execute research code."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def build(export):
 w=json.loads((ROOT/'data/worlds/profile-guitar-string-count.json').read_text())
 source=(export/w['programs']['generator']['sourcePath']).parent/'manifest.jsonl'
 rows={r['scene_id']:r for r in map(json.loads,source.read_text().splitlines())};items=[]
 for i,sample in enumerate(w['samples']):
  r=rows[f'scene_{i:04}'];scene=r['scene'];cx=256+scene['offset_x'];cy=round(249+scene['offset_y']+scene['body_height']*.73)
  assert r['answer']==sample['answer'] and r['question']==sample['question']
  img=Image.open(ROOT/sample['image']).convert('RGB');x0=cx-43
  pixels=[[list(img.getpixel((x,y))) for x in range(x0,x0+86)] for y in range(cy-1,cy+2)]
  counts=[]
  for row in pixels:
   dark=[sum(rgb)/3<105 for rgb in row];counts.append(sum(v and (j==0 or not dark[j-1]) for j,v in enumerate(dark)))
  assert counts==[int(sample['answer'])]*3
  items.append({'image':sample['image'],'sha256':sample['sha256'],'answer':sample['answer'],'scene':scene,'crop':[cx-61,cy-23,122,46],'rowOrigin':[x0,cy-1],'pixels':pixels,'rowCounts':counts})
 (ROOT/'data/method-pixels.json').write_text(json.dumps({'note':'Original image pixels at editorially selected bridge rows. Coordinates use recorded scene geometry for display only; the original inverse independently locates the bridge from pixels. No imported program was executed.','sourceManifest':str(source.relative_to(export)),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'instances':items},separators=(',',':'))+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--export',type=Path,required=True);build(p.parse_args().export)
