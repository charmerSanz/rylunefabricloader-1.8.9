#!/usr/bin/env python3
"""Local Rylune mod scanner and isolated instance setup. Does not execute JARs."""
import argparse, json, re, shutil, struct, zipfile
from pathlib import Path
from datetime import datetime

TARGET=(1,8,9)

def version(s):
    if not re.fullmatch(r'\d+(?:\.\d+){0,2}',s): return None
    a=tuple(map(int,s.split('.'))); return a+(0,)*(3-len(a))

def match_one(s,target=TARGET):
    s=s.strip()
    if s=='*': return True
    if re.fullmatch(r'\d+(?:\.\d+)?\.[xX*]',s) or re.fullmatch(r'\d+\.[xX*]',s):
        a=tuple(map(int,s.split('.')[:-1])); return target[:len(a)]==a
    results=[]
    for token in s.split():
        m=re.fullmatch(r'(>=|<=|>|<|=|~|\^)?(\d+(?:\.\d+){0,2})',token)
        if not m: return None
        op=m[1] or '='; v=version(m[2]); n=len(m[2].split('.'))
        if op=='~': upper=(v[0]+1,0,0) if n==1 else (v[0],v[1]+1,0); result=v<=target<upper
        elif op=='^': upper=(v[0]+1,0,0) if v[0] else (0,v[1]+1,0) if v[1] else (0,0,v[2]+1); result=v<=target<upper
        else: result={'=':target==v,'>':target>v,'<':target<v,'>=':target>=v,'<=':target<=v}[op]
        results.append(result)
    return all(results) if results else None

def matches(value,target=TARGET):
    if isinstance(value,str): return match_one(value,target)
    if isinstance(value,list):
        a=[match_one(x,target) if isinstance(x,str) else None for x in value]
        return True if True in a else None if None in a or not a else False
    return None

def scan(path, java=8):
    out={'file':path.name,'status':'REVIEW','notes':[]}
    try:
        with zipfile.ZipFile(path) as z:
            names=z.namelist()
            if 'fabric.mod.json' not in names:
                out['status']='NOT_FABRIC'; out['notes'].append('No top-level fabric.mod.json; do not install as a Fabric mod.'); return out
            info=z.getinfo('fabric.mod.json')
            if info.file_size>1_000_000: raise ValueError('Oversized metadata')
            data=json.loads(z.read(info)); dep=data.get('depends',{})
            if not isinstance(dep,dict): raise ValueError('Invalid dependency metadata')
            out.update(id=data.get('id'),version=data.get('version'),dependencies=dep)
            compat=matches(dep.get('minecraft')); java_compat=matches(dep.get('java'),(java,0,0))
            max_major=0
            for entry in z.infolist():
                if entry.filename.endswith('.class') and not entry.filename.startswith('META-INF/versions/'):
                    with z.open(entry) as f: head=f.read(8)
                    if len(head)==8 and head[:4]==b'\xca\xfe\xba\xbe': max_major=max(max_major,struct.unpack('>H',head[6:8])[0])
            out['max_class_major']=max_major
            if compat is False or java_compat is False or max_major>44+java or data.get('environment')=='server':
                out['status']='UNSUPPORTED'
                if compat is False: out['notes'].append('Minecraft version declaration excludes 1.8.9.')
                if java_compat is False: out['notes'].append('Declared Java constraint excludes selected runtime.')
                if max_major>44+java: out['notes'].append('Top-level bytecode requires Java newer than selected runtime '+str(java)+'.')
                if data.get('environment')=='server': out['notes'].append('Server-only mod.')
            elif compat is True:
                out['status']='CANDIDATE'; out['notes'].append('Metadata allows 1.8.9; runtime compatibility is not established.')
            else: out['notes'].append('Missing or unrecognized Minecraft constraint; manual review required.')
            if data.get('jars'): out['notes'].append('Nested JARs not scanned; Fabric Loader performs dependency checks.')
            if data.get('mixins'): out['notes'].append('Mixin targets not validated by this scanner.')
            if dep.get('java'): out['notes'].append('Check declared Java requirement against Java '+str(java)+': '+str(dep['java']))
    except (OSError,ValueError,KeyError,TypeError,AttributeError,RuntimeError,zipfile.BadZipFile) as e:
        out['status']='INVALID'; out['notes'].append(str(e))
    return out

PRESETS={
 'low':{'renderDistance':'6','fancyGraphics':'false','ao':'0','clouds':'false','particles':'1','mipmapLevels':'0','useVbo':'true','enableVsync':'false','maxFps':'120'},
 'balanced':{'renderDistance':'8','fancyGraphics':'false','ao':'1','clouds':'false','particles':'1','mipmapLevels':'2','useVbo':'true','enableVsync':'false','maxFps':'120'},
}

def setup(instance,jar,preset):
    if not jar.is_file(): raise ValueError('Missing mod JAR')
    result=scan(jar)
    if result.get('id')!='rylunefabric' or result['status']!='CANDIDATE': raise ValueError('Expected Rylune Fabric 1.8.9 JAR')
    instance.mkdir(parents=True,exist_ok=True); mods=instance/'mods'; mods.mkdir(exist_ok=True)
    dest=mods/jar.name
    if dest.exists(): raise ValueError('Destination JAR already exists; remove old version manually.')
    if any(scan(p).get('id')=='rylunefabric' for p in mods.glob('*.jar')): raise ValueError('Another Rylune JAR already installed.')
    shutil.copy2(jar,dest)
    if preset: apply_preset(instance,preset)
    print(f'Installed mod in {mods}. Set this as the game directory of a Ornithe Gen 2 1.8.9 launcher profile.')

def apply_preset(instance,preset):
    instance.mkdir(parents=True,exist_ok=True); p=instance/'options.txt'; values=PRESETS[preset].copy()
    lines=p.read_text(encoding='utf-8').splitlines() if p.exists() else []
    if p.exists(): shutil.copy2(p,p.with_name('options.txt.rylune-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.bak'))
    result=[]
    for line in lines:
        key=line.partition(':')[0]
        if key in values: result.append(key+':'+values.pop(key))
        elif key not in PRESETS[preset]: result.append(line)
    result.extend(k+':'+v for k,v in values.items())
    tmp=p.with_suffix('.rylune.tmp'); tmp.write_text('\n'.join(result)+'\n',encoding='utf-8'); tmp.replace(p)
    print('Applied graphics preset; existing options backed up if present. Close Minecraft before changing settings.')

def main():
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('scan'); p.add_argument('path',type=Path); p.add_argument('--json',action='store_true'); p.add_argument('--java',type=int,default=8,choices=range(8,26))
    p=sub.add_parser('setup'); p.add_argument('instance',type=Path); p.add_argument('jar',type=Path); p.add_argument('--preset',choices=PRESETS)
    p=sub.add_parser('preset'); p.add_argument('instance',type=Path); p.add_argument('name',choices=PRESETS)
    args=parser.parse_args()
    if args.cmd=='scan':
        if not args.path.exists(): parser.error('Path not found')
        files=sorted(args.path.glob('*.jar')) if args.path.is_dir() else [args.path]
        data=[scan(p,java=args.java) for p in files]; ids={x.get('id') for x in data}; builtins={'minecraft','java','fabricloader'}
        for x in data:
            missing=set(x.get('dependencies',{}))-ids-builtins
            if missing: x['notes'].append('Dependency IDs not present at top level (may be nested/provided): '+', '.join(sorted(missing)))
        if args.json: print(json.dumps(data,indent=2))
        else:
            for x in data:
                print(f"{x['status']:12} {x['file']}")
                for n in x['notes']: print('   '+n)
    elif args.cmd=='setup': setup(args.instance,args.jar,args.preset)
    else: apply_preset(args.instance,args.name)
if __name__=='__main__': main()
