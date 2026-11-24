#!/usr/bin/env python3
"""Explicit feature adapters and optional upstream Sodium-derived renderer installer."""
import argparse, hashlib, json, os, re, shutil, tempfile, urllib.request, zipfile
from pathlib import Path
from rylune import scan
# These are native feature substitutes. Original modern bytecode is NEVER loaded.
ADAPTERS={
 'dynamic_fps':({'backgroundFps':'30','hiddenFps':'15'},'Native unfocused/minimized frame caps'),
 'zoomify':({'zoom':'true'},'Native C-key zoom; no modern settings or smooth transition'),
 'lithium':({'stateCache':'true'},'Experimental immutable block-state hash cache only'),
 'ferritecore':({'stringPool':'true'},'Experimental resource identifier string deduplication only'),
}
RENDERER_VERSION='nZyz0uhf'
RENDERER_PROJECT='URs5boj6'
def adapter_for(mod): return ADAPTERS.get(mod)
def write_options(instance, changes):
    p=instance/'config'/'rylune.properties';p.parent.mkdir(parents=True,exist_ok=True)
    lines=p.read_text(encoding='iso-8859-1').splitlines() if p.exists() else []
    if p.exists():
        if any(x.rstrip().endswith('\\') for x in lines): raise ValueError('Multiline properties require manual editing.')
        shutil.copy2(p,p.with_suffix('.properties.bridge.bak'))
    out=[];seen=set()
    for line in lines:
        m=re.match(r'^\s*([^#!\s:=]+)\s*[:=\s]',line)
        k=m.group(1) if m else None
        if k in changes:
            if k not in seen:out.append(k+'='+changes[k]);seen.add(k)
        else: out.append(line)
    out.extend(k+'='+v for k,v in changes.items() if k not in seen)
    fd,tmp=tempfile.mkstemp(prefix='rylune-',suffix='.tmp',dir=p.parent)
    try:
        with os.fdopen(fd,'w',encoding='iso-8859-1') as f:f.write('\n'.join(out)+'\n')
        os.replace(tmp,p)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return p

def request(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'RyluneFabric/0.2 (local installer)'}),timeout=60)
def renderer(instance, java, install=False):
    with request('https://api.modrinth.com/v2/version/'+RENDERER_VERSION) as r: meta=json.load(r)
    if meta['project_id']!=RENDERER_PROJECT or meta['id']!=RENDERER_VERSION or '1.8.9' not in meta['game_versions'] or 'fabric' not in meta['loaders']:raise ValueError('Unexpected upstream renderer metadata')
    f=next((f for f in meta['files'] if f.get('primary')),meta['files'][0]);name=f['filename']
    if Path(name).name!=name or not name.endswith('.jar') or not f['url'].startswith('https://cdn.modrinth.com/'):raise ValueError('Unexpected renderer download URL')
    if f['size']>100_000_000:raise ValueError('Renderer download exceeds size limit')
    stage=instance/'rylune-downloads';stage.mkdir(parents=True,exist_ok=True);p=stage/name
    with request(f['url']) as r:data=r.read(100_000_001)
    if len(data)!=f['size'] or hashlib.sha512(data).hexdigest()!=f['hashes']['sha512']:raise ValueError('Renderer checksum mismatch')
    p.write_bytes(data)
    result=scan(p,java=java);print(json.dumps(result,indent=2));print('Upstream dependencies:',json.dumps(meta.get('dependencies',[])))
    print('Staged (not active):',p)
    if not install:return
    raise ValueError('Automatic renderer installation disabled on Ornithe Gen 2: the pinned Radium build has not been verified for these mappings. Obtain a compatible Ornithe renderer manually.')

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('adapt');a.add_argument('instance',type=Path);a.add_argument('mod',choices=ADAPTERS)
    a=sub.add_parser('renderer');a.add_argument('instance',type=Path);a.add_argument('--java',type=int,default=25,choices=range(8,26));a.add_argument('--install',action='store_true',help='Actually copy into mods after preflight; experimental')
    args=p.parse_args()
    if args.cmd=='adapt':
        changes,desc=ADAPTERS[args.mod];print(desc);print('Updated',write_options(args.instance,changes));print('Do not place original modern JAR in mods.')
    else:renderer(args.instance,args.java,args.install)
if __name__=='__main__':main()
