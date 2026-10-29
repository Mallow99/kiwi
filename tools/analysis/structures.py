# Usage: structures.py <.reference/VER/jar/data/mineminenomi/structures> tools/analysis
import sys,glob,os,collections
sys.path.insert(0,sys.argv[2]); import nbt
root=sys.argv[1]
for p in sorted(glob.glob(root+'/**/*.nbt',recursive=True)):
    d=nbt.load(p); pal=d.get('palette') or (d.get('palettes') or [[]])[0]
    names=[b['Name'] for b in pal]
    blocks=[b for b in d['blocks'] if names[b['state']] not in ('minecraft:air','minecraft:structure_void')]
    special=collections.Counter(names[b['state']].split(':')[1] for b in d['blocks'] if any(k in names[b['state']] for k in ('chest','spawner','jigsaw','barrel')))
    print(f"{os.path.relpath(p,root):45s} {'x'.join(map(str,d['size'])):12s} blocks={len(blocks):6d} ents={len(d.get('entities',[])):3d} {dict(special)}")
