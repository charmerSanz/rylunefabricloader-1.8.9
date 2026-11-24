#!/usr/bin/env python3
"""Fetch official 1.8.9 client + Ornithe Gen 2 mappings for local compilation only."""
import hashlib, json, subprocess, urllib.request, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'.gradle'/'rylune-game'
ROOT.mkdir(parents=True,exist_ok=True)
def fetch(url, path, sha1=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and sha1 and hashlib.sha1(path.read_bytes()).hexdigest()==sha1: return
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'RyluneFabric-build/0.2'}),timeout=90) as r: data=r.read()
    if sha1 and hashlib.sha1(data).hexdigest()!=sha1: raise ValueError('SHA1 mismatch: '+str(path))
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_bytes(data);tmp.replace(path)
def main():
    output=ROOT/'client-ornithe-gen2.jar'
    if output.exists() and zipfile.is_zipfile(output): return
    manifest=ROOT/'manifest.json';fetch('https://launchermeta.mojang.com/mc/game/version_manifest_v2.json',manifest)
    v=next(x for x in json.loads(manifest.read_text())['versions'] if x['id']=='1.8.9')
    info=ROOT/'1.8.9.json';fetch(v['url'],info,v.get('sha1'));data=json.loads(info.read_text());client=data['downloads']['client']
    src=ROOT/'client.jar';fetch(client['url'],src,client['sha1'])
    libs=[]
    for entry in data.get('libraries',[]):
        a=entry.get('downloads',{}).get('artifact');
        if not a: continue
        p=ROOT/'libs'/a['path'];fetch(a['url'],p,a.get('sha1'));libs.append(p)
    mappings=ROOT/'1.8.9-ornithe-gen2.tiny';fetch('https://raw.githubusercontent.com/OrnitheMC/calamus/gen2/mappings/1.8.9.tiny',mappings)
    content=mappings.read_text();assert content.startswith('v1\tofficial\tintermediary');assert 'CLASS\taxu\tnet/minecraft/unmapped/C_85740840' in content
    remapper=ROOT/'tiny-remapper.jar';fetch('https://maven.fabricmc.net/net/fabricmc/tiny-remapper/0.10.4/tiny-remapper-0.10.4-fat.jar',remapper)
    tmp=ROOT/'client-ornithe-gen2.tmp.jar';tmp.unlink(missing_ok=True)
    subprocess.run(['java','-jar',str(remapper),str(src),str(tmp),str(mappings),'official','intermediary']+[str(p) for p in libs]+['--ignoreConflicts'],check=True)
    with zipfile.ZipFile(tmp) as z:
        for name in ['unmapped/C_85740840','client/Minecraft','unmapped/C_22168528','unmapped/C_06229646$C_07015679','unmapped/C_03140863','unmapped/C_16190149','unmapped/C_47540058']:
            assert 'net/minecraft/'+name+'.class' in z.namelist(),name
    tmp.replace(output)
if __name__=='__main__': main()
