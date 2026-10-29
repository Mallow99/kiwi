# Usage: boxes.py <.reference/VER/jar/data/mineminenomi>
import json,glob,os,sys
root=sys.argv[1]
def chance(pool):
    c=1.0
    for cond in pool.get('conditions',[]):
        if cond.get('condition')=='minecraft:random_chance': c*=cond['chance']
        elif 'chance' in cond: c*=cond['chance']
    return c
print('== Chest box odds (per chest)')
for f in sorted(glob.glob(root+'/loot_tables/**/*.json',recursive=True)):
    if '/dfboxes/' in f: continue
    d=json.load(open(f))
    for p in d.get('pools',[]):
        ents=p.get('entries',[])
        boxes=[e for e in ents if 'box' in e.get('name','')]
        if not boxes: continue
        tot=sum(e.get('weight',1) for e in ents)
        r=p.get('rolls',1); c=chance(p)
        conds=[x.get('condition') for x in p.get('conditions',[])]
        s=', '.join(f"{e['name'].split(':')[1].replace('_box','')} {100*c*e.get('weight',1)/tot:.1f}%" for e in boxes)
        print(f" {os.path.relpath(f,root+'/loot_tables'):48s} rolls={r} {s}  conds={conds}")
print('\n== Box contents')
for f in sorted(glob.glob(root+'/loot_tables/dfboxes/*.json')):
    d=json.load(open(f))
    for p in d['pools']:
        ents=p['entries']; tot=sum(e.get('weight',1) for e in ents)
        print(os.path.basename(f),'rolls',p.get('rolls'),'entries',len(ents))
        for e in sorted(ents,key=lambda e:-e.get('weight',1)):
            print(f"   {e.get('name',e.get('type')).split(':')[-1]:40s} {100*e.get('weight',1)/tot:5.1f}%")
