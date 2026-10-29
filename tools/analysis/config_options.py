# Usage: config_options.py <.reference/VER/src/xyz/pixelatedw/mineminenomi/config>
import re,sys,glob,os
for f in sorted(glob.glob(sys.argv[1]+'/*.java')):
    s=open(f).read()
    items=re.findall(r'(\w+Option(?:<[^>]*>)?) (\w+) = new \w+Option(?:<>)?\((.*?)\);\n',s,re.S)
    if not items: continue
    print('==',os.path.basename(f),len(items))
    for t,n,a in items:
        a=' '.join(a.split())
        m=re.search(r'"([^"]+)",\s*"([^"]*)"',a)
        if m: print(' -',m.group(1),'|',a.split(',')[0][:30],'|',m.group(2).split('\\n')[0][:110])
        else: print(' -',n,a[:120])
