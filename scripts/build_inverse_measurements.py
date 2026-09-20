"""Explicit display measurements of original pixels; never import candidate programs.
These source-informed operations illustrate the inverse computations. They are
not another held-out verification run. All outputs are checked against saved answers.
"""
from collections import deque
import hashlib,html,json,math
import numpy as np
from PIL import Image

def runs(values):
    result=[];start=None
    for i,v in enumerate(list(values)+[False]):
        if v and start is None:start=i
        elif not v and start is not None:result.append((start,i));start=None
    return result

def components(mask):
    seen=np.zeros_like(mask);sizes=[];height,width=mask.shape
    for y,x in np.argwhere(mask):
        if seen[y,x]:continue
        seen[y,x]=True;q=deque([(int(y),int(x))]);size=0
        while q:
            cy,cx=q.popleft();size+=1
            for ny,nx in [(cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)]:
                if 0<=ny<height and 0<=nx<width and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;q.append((ny,nx))
        sizes.append(size)
    return sizes

def mask_svg(mask,color):
    h,w=mask.shape
    path=' '.join(f'M{a} {y}h{b-a}v1h{a-b}z' for y,row in enumerate(mask) for a,b in runs(row))
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Pixels belonging to color RGB {color}"><path d="{path}" fill="rgb{tuple(color)}"/></svg>'

def ring_measure(arr):
    hi=arr.max(2).astype(int);lo=arr.min(2).astype(int);spread=hi-lo;mean=arr.mean(2)
    grey=(spread<=14)&(mean>=90)&(mean<=190);ink=~grey&~((spread<=14)&(mean>235))
    cols=runs(grey.sum(0)>20);rows=runs(grey.sum(1)>20);assert len(cols)==10 and len(rows)==2
    top,bottom=rows[0][1],rows[1][0];panels=[];masks=[]
    for i in range(5):
        left,right=cols[2*i][1],cols[2*i+1][0];sub=arr[top:bottom,left:right];sel=ink[top:bottom,left:right]
        colors=np.unique(sub[sel].reshape(-1,3),axis=0);assert len(colors)==2
        ms=[sel&np.all(sub==color,axis=2) for color in colors];counts=[sum(n>=10 for n in components(m)) for m in ms]
        a,b=ms;near=np.zeros_like(b);near[1:]|=b[:-1];near[:-1]|=b[1:];near[:,1:]|=b[:,:-1];near[:,:-1]|=b[:,1:];touch=bool((a&near).any())
        panels.append({'panel':i+1,'box':[left,top,right-left,bottom-top],'colors':colors.tolist(),'counts':counts,'touching':touch});masks.append(ms)
    winners=[i for i,p in enumerate(panels) if p['counts']==[1,1] and p['touching']];assert len(winners)==1
    winner=winners[0];p=panels[winner]
    visuals=''.join(f'<figure>{mask_svg(mask,color)}<figcaption>Color {i+1}: <strong>1 piece</strong></figcaption></figure>' for i,(mask,color) in enumerate(zip(masks[winner],p['colors'])))
    table=''.join(f'<tr class="{"measurement-winner" if i==winner else ""}"><th scope="row">Panel {i+1}</th><td>'+ ' + '.join(f'<span class="color-count"><i style="background:rgb{tuple(c)}"></i>{n}</span>' for c,n in zip(p['colors'],p['counts']))+f'</td><td>{"Interlocked" if i==winner else "Stacked"}</td></tr>' for i,p in enumerate(panels))
    markup=f'<p class="measurement-step"><b>1</b> Separate the ring colors</p><div class="ring-mask-pair">{visuals}</div><p class="measurement-caption">Isolated pixels from panel {winner+1}, selected by the display measurement.</p><p class="measurement-step"><b>2</b> Count connected pieces</p><table class="measurement-table"><caption>Four-connected components per color</caption><thead><tr><th>Panel</th><th>Pieces</th><th>Decision</th></tr></thead><tbody>{table}</tbody></table><p class="measurement-caption">One piece of each color, plus touching masks, identifies the interlocked pair. A stacked pair leaves two pieces of the rear ring.</p>'
    return {'panels':panels,'answer':f'panel-{winner+1}'},markup

def band_measure(arr):
    a=arr.astype(int);red,green,blue=a[:,:,0],a[:,:,1],a[:,:,2]
    bm=(blue-red>70)&(green-red>28)&(blue>135);dark=arr.max(2)<95;points=[]
    for i,f in enumerate([.12,.272,.424,.576,.728,.88]):
        x=round(110+f*880);ys=np.nonzero(bm[117:513,max(122,x-7):min(978,x+8)])[0]+117
        ys=np.unique(ys);groups=np.split(ys,np.flatnonzero(np.diff(ys)>8)+1);groups=[g for g in groups if len(g)>=2];assert len(groups)>=2
        upper,lower=float(np.mean(groups[0])),float(np.mean(groups[-1]));traceys=np.nonzero(dark[123:507,max(128,x-13):min(972,x+14)])[0]+123;assert len(traceys)>=20
        marker=float(np.median(traceys));inside=upper+4<marker<lower-4
        points.append({'checkpoint':i+1,'x':x,'upperY':upper,'markerY':marker,'lowerY':lower,'inside':inside})
    low=min(min(p['upperY'],p['markerY']) for p in points)-15;high=max(max(p['lowerY'],p['markerY']) for p in points)+15
    fy=lambda y:30+(y-low)/(high-low)*130
    marks=[]
    for i,p in enumerate(points):
        x=43+i*48;u,t,l=map(fy,[p['upperY'],p['markerY'],p['lowerY']]);color='#85d5ba' if p['inside'] else '#ffc087'
        marks.append(f'<path d="M{x} {u:.2f}V{l:.2f}" stroke="#91bfff" stroke-width="12" opacity=".45"/><path d="M{x-9} {u:.2f}h18M{x-9} {l:.2f}h18" stroke="#b5d5ff"/><circle cx="{x}" cy="{t:.2f}" r="5" fill="{color}" stroke="#122237" stroke-width="1.5"/><text x="{x}" y="183" text-anchor="middle">T{i+1}</text><text x="{x}" y="202" text-anchor="middle" fill="{color}">{"in" if p["inside"] else "out"}</text>')
    plot='<svg class="band-measure-plot" viewBox="0 0 326 211" role="img" aria-label="Blue intervals show measured band boundaries; dots show marker heights at six checkpoints"><text x="8" y="14">Image row ↓</text>'+''.join(marks)+'</svg>'
    table=''.join(f'<tr><th>T{p["checkpoint"]}</th><td>{p["upperY"]:.1f}</td><td>{p["markerY"]:.1f}</td><td>{p["lowerY"]:.1f}</td></tr>' for p in points)
    answer=str(sum(p['inside'] for p in points))
    markup=f'<p class="measurement-step"><b>1</b> Measure band edges and marker centers</p>{plot}<p class="measurement-caption">Blue interval: band boundaries. Dot: black marker center. Green means inside; orange means outside. Image-row coordinates increase downward.</p><p class="measurement-step"><b>2</b> Count markers strictly inside</p><code class="measurement-rule">upper + 4 &lt; marker &lt; lower − 4</code><p class="measurement-caption">The source uses a four-pixel interior margin. <strong>{answer} of 6</strong> markers satisfy the test.</p><details class="measurement-details"><summary>Measured pixel coordinates</summary><table class="measurement-table"><thead><tr><th></th><th>Upper</th><th>Marker</th><th>Lower</th></tr></thead><tbody>{table}</tbody></table></details>'
    return {'checkpoints':points,'answer':answer},markup

def circle_measure(arr,image):
    a=arr.astype(float);ys,xs=np.nonzero(np.linalg.norm(a-np.array([40.,48.,58.]),axis=2)<48);x=xs+.5;y=ys+.5
    coeff,_,rank,_=np.linalg.lstsq(np.column_stack([2*x,2*y,np.ones_like(x)]),x*x+y*y,rcond=None);assert rank==3
    cx,cy,c=map(float,coeff);radius=math.sqrt(c+cx*cx+cy*cy);rms=float(np.sqrt(np.mean((np.hypot(x-cx,y-cy)-radius)**2)))
    palette={'red':[205,67,85],'blue':[45,103,210],'green':[38,151,105],'orange':[232,132,39]};names=list(palette);dist=np.linalg.norm(a[:,:,None,:]-np.array(list(palette.values()))[None,None,:,:],axis=3);nearest=dist.argmin(2);minimum=dist.min(2);markers=[]
    for i,name in enumerate(names):
        my,mx=np.nonzero((nearest==i)&(minimum<58));assert len(mx)>0;px=float(mx.mean()+.5);py=float(my.mean()+.5);markers.append({'name':name,'x':px,'y':py,'distance':math.hypot(px-cx,py-cy),'color':palette[name]})
    ranked=sorted(markers,key=lambda m:m['distance']);answer=ranked[0]['name']
    lines=''.join(f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{m["x"]:.2f}" y2="{m["y"]:.2f}" stroke="rgb{tuple(m["color"])}" stroke-width="2" stroke-dasharray="5 4"/>' for m in markers)
    svg=f'<svg class="circle-measure-plot" viewBox="{cx-radius-25:.2f} {cy-radius-25:.2f} {2*radius+50:.2f} {2*radius+50:.2f}" role="img" aria-label="Original pixels with a fitted circle, center cross, and marker distances"><image href="{image}" width="{arr.shape[1]}" height="{arr.shape[0]}"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.2f}" fill="none" stroke="#227d91" stroke-width="2.5" stroke-dasharray="6 5"/>{lines}<path d="M{cx-8:.2f} {cy:.2f}h16M{cx:.2f} {cy-8:.2f}v16" stroke="#122237" stroke-width="3"/></svg>'
    rows=''.join(f'<tr class="{"measurement-winner" if m["name"]==answer else ""}"><th><span class="color-count"><i style="background:rgb{tuple(m["color"])}"></i>{m["name"].title()}</span></th><td>{m["distance"]:.1f} px</td></tr>' for m in ranked)
    markup=f'<p class="measurement-step"><b>1</b> Fit a circle to dark arc pixels</p>{svg}<p class="measurement-caption">Dashed outline: fitted circle. Cross: estimated center. Overlay on original pixels; fit RMS error {rms:.2f} px.</p><p class="measurement-step"><b>2</b> Select the nearest colored dot</p><table class="measurement-table"><caption>Dot-center distance to fitted center</caption><tbody>{rows}</tbody></table>'
    return {'center':[cx,cy],'radius':radius,'rms':rms,'markers':markers,'answer':answer},markup

def build_measurements(root,world):
    displays=[];records=[]
    for i,s in enumerate(world['samples']):
        arr=np.asarray(Image.open(root/s['image']).convert('RGB'))
        if world['id']=='profile-linked-ring-panel':data,markup=ring_measure(arr)
        elif world['id']=='profile-band-checkpoint-count':data,markup=band_measure(arr)
        else:data,markup=circle_measure(arr,s['image'])
        assert data['answer']==s['answer'],(world['id'],i,data['answer'],s['answer'])
        records.append({'image':s['image'],'imageSha256':hashlib.sha256((root/s['image']).read_bytes()).hexdigest(),**data})
        displays.append(f'<div class="inverse-measurement" data-inverse-measurement="{i}" {"hidden" if i else ""}>{markup}</div>')
    return ''.join(displays),records
