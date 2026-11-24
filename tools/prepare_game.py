#!/usr/bin/env python3
"""Fetch official 1.8.9 client + generation-1 mappings for local compilation only."""
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
    output=ROOT/'client-intermediary.jar'
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
    mappings=ROOT/'1.8.9.tiny';fetch('https://raw.githubusercontent.com/Legacy-Fabric/Legacy-Intermediaries/master/mappings/1.8.9.tiny',mappings)
    content=mappings.read_text();assert content.startswith('v1\tofficial\tintermediary');assert 'CLASS\taxu\tnet/minecraft/class_388' in content
    remapper=ROOT/'tiny-remapper.jar';fetch('https://maven.fabricmc.net/net/fabricmc/tiny-remapper/0.10.4/tiny-remapper-0.10.4-fat.jar',remapper)
    tmp=ROOT/'client-intermediary.tmp.jar';tmp.unlink(missing_ok=True)
    subprocess.run(['java','-jar',str(remapper),str(src),str(tmp),str(mappings),'official','intermediary']+[str(p) for p in libs]+['--ignoreConflicts'],check=True)
    with zipfile.ZipFile(tmp) as z:
        for name in ['class_388','class_1600','class_1653','class_2233$class_2234','class_524']:
            assert 'net/minecraft/'+name+'.class' in z.namelist(),name
    tmp.replace(output)
if __name__=='__main__': main()
