# Usage: fruits.py <.reference/VER/src/xyz/pixelatedw/mineminenomi/init/ModFruits.java> <out.json>
import re,sys,json,collections
src=open(sys.argv[1]).read()
out=[]
for m in re.finditer(r'(\w+)\s*=\s*(?:ModRegistry\.registerFruitItem|registerMochi)\(\s*"([^"]+)",\s*\(\)\s*->\s*new AkumaNoMiItem\((.*?)\)\s*\);',src,re.S):
    args=[a.strip() for a in m.group(3).replace('\n',' ').split(',')]
    abil=[a.replace('.INSTANCE','') for a in args[2:] if a]
    out.append(dict(id=m.group(1),name=m.group(2),tier=int(args[0]),type=args[1].replace('FruitType.',''),abilities=abil))
json.dump(out,open(sys.argv[2],'w'),indent=1)
print(len(out))
c=collections.Counter((f['type'],f['tier']) for f in out)
for k,v in sorted(c.items()): print(k,v)
for f in sorted(out,key=lambda f:(f['tier'],f['type'])): print(f['tier'],f['type'],f['name'],len(f['abilities']))
