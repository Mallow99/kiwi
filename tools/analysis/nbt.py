# Minimal NBT reader (gzip or raw) for structure templates.
import gzip,struct,io
def _r(f,t):
    if t==1: return struct.unpack('>b',f.read(1))[0]
    if t==2: return struct.unpack('>h',f.read(2))[0]
    if t==3: return struct.unpack('>i',f.read(4))[0]
    if t==4: return struct.unpack('>q',f.read(8))[0]
    if t==5: return struct.unpack('>f',f.read(4))[0]
    if t==6: return struct.unpack('>d',f.read(8))[0]
    if t==7: n=_r(f,3); return f.read(n)
    if t==8: n=struct.unpack('>H',f.read(2))[0]; return f.read(n).decode('utf-8','replace')
    if t==9:
        et=_r(f,1); n=_r(f,3); return [_r(f,et) for _ in range(n)]
    if t==10:
        d={}
        while True:
            tt=_r(f,1)
            if tt==0: return d
            k=_r(f,8); d[k]=_r(f,tt)
    if t==11: n=_r(f,3); return list(struct.unpack('>%di'%n,f.read(4*n)))
    if t==12: n=_r(f,3); return list(struct.unpack('>%dq'%n,f.read(8*n)))
    raise ValueError(t)
def load(path):
    data=open(path,'rb').read()
    if data[:2]==b'\x1f\x8b': data=gzip.decompress(data)
    f=io.BytesIO(data); t=_r(f,1); _r(f,8); return _r(f,t)
