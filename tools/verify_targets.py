#!/usr/bin/env python3
"""Fail CI if any injection or shadow target is absent from the remapped game."""
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT/'.gradle'/'rylune-game'/'client-ornithe-gen2.jar'
MIXINS=ROOT/'src/main/java/dev/rylune/fabric/mixin'
def members(target):
    output=subprocess.check_output(['javap','-p','-s','-classpath',str(GAME),target],text=True)
    found=set()
    lines=output.splitlines()
    for i,line in enumerate(lines[:-1]):
        descriptor=re.search(r'descriptor:\s*(\S+)',lines[i+1])
        if not descriptor:continue
        if '(' in line:
            name=line.split('(')[0].strip().split()[-1]
            if name==target:name='<init>'
        else:
            name=line.strip().rstrip(';').split()[-1]
        found.add((name,descriptor.group(1)))
    return found
for p in sorted(MIXINS.glob('*Mixin.java')):
    src=p.read_text()
    target=re.search(r'@Mixin\(targets="([^"]+)"',src).group(1)
    actual=members(target)
    for method in set(re.findall(r'@Inject\(method="([^"]+)"',src)):
        name,desc=method.split('(',1)
        assert (name,'('+desc) in actual,(p.name,target,method,actual)
        print(p.name, target, method, 'OK')
    for field in re.findall(r'@Shadow[^\n]*String\s+(\w+);',src):
        assert (field,'Ljava/lang/String;') in actual,(p.name,target,field)
print('All declared Mixin targets present in Ornithe Gen 2 client.')
