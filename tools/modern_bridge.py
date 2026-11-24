#!/usr/bin/env python3
"""Conservative offline compatibility preflight and packaging for portable Fabric mods.

Not a sandbox, bytecode translator or modern Minecraft API implementation.
"""
import argparse
import hashlib
import io
import json
import re
import struct
import sys
import zipfile
from pathlib import Path, PurePosixPath

from rylune import matches, version
from bridge import adapter_for, write_options

MAX_BYTES = 64 * 1024 * 1024
MAX_ENTRIES = 10000
TARGET = (1, 8, 9)
LOADER_API = {'net/fabricmc/api/ClientModInitializer', 'net/fabricmc/api/ModInitializer'}
BAD_FEATURES = ('mixins', 'accessWidener', 'classTweakers', 'jars', 'languageAdapters', 'provides')
BLOCKED_PREFIXES = ('net/minecraft/', 'net.minecraft.', 'com/mojang/', 'com.mojang.',
                    'net/fabricmc/fabric/', 'net.fabricmc.fabric.', 'org/spongepowered/',
                    'org.spongepowered.', 'org/lwjgl/', 'org.lwjgl.')
# Disallow common dynamic linkage mechanisms. This does not prove a JAR safe.
DYNAMIC_CLASSES = ('java/lang/reflect/', 'java/lang/invoke/MethodHandles',
                   'java/lang/ClassLoader', 'java/net/URLClassLoader', 'sun/', 'jdk/internal/')
ADAPTER_IDS = {'dynamicfps': 'dynamic_fps', 'dynamic_fps': 'dynamic_fps',
               'zoomify': 'zoomify', 'lithium': 'lithium', 'ferritecore': 'ferritecore'}
RENDERERS = {'sodium', 'radium', 'iris', 'indium'}

def read_pool(data):
    stream = io.BytesIO(data)
    def get(n):
        b = stream.read(n)
        if len(b) != n:
            raise ValueError('Truncated class file')
        return b
    def u1(): return get(1)[0]
    def u2(): return struct.unpack('>H', get(2))[0]
    if get(4) != b'\xca\xfe\xba\xbe':
        raise ValueError('Invalid class magic')
    minor, major = u2(), u2()
    if minor == 65535:
        raise ValueError('Preview Java bytecode is unsupported')
    count = u2()
    entries = {}
    i = 1
    while i < count:
        tag = u1()
        if tag == 1:
            # Class names/descriptors are ASCII. Replacement of modified UTF-8
            # null/surrogate sequences in other constants is conservative.
            entries[i] = (tag, get(u2()).decode('utf-8', 'replace'))
        elif tag in (7, 8, 16, 19, 20):
            entries[i] = (tag, u2())
        elif tag in (3, 4):
            get(4)
        elif tag in (5, 6):
            get(8)
            i += 1
        elif tag in (9, 10, 11, 12, 17, 18):
            get(4)
        elif tag == 15:
            get(3)
        else:
            raise ValueError('Unsupported constant pool tag '+str(tag))
        i += 1
    access = u2()
    this_class = u2()
    def utf(idx):
        if idx not in entries or entries[idx][0] != 1:
            raise ValueError('Invalid constant pool index')
        return entries[idx][1]
    if this_class not in entries or entries[this_class][0] != 7:
        raise ValueError('Missing class name')
    name = utf(entries[this_class][1])
    strings = [v for tag,v in entries.values() if tag == 1]
    refs = {utf(v) for tag,v in entries.values() if tag == 7}
    # Descriptors may contain references absent from CONSTANT_Class entries.
    for s in strings:
        refs.update(re.findall(r'L([A-Za-z0-9_$/]+)(?=[;<])', s))
    return major, name, strings, refs

def assess(path, java=8, loader='0.16.14'):
    result = {'file': path.name, 'status': 'REJECTED', 'reasons': [],
              'java': java, 'loader': loader, 'target': '1.8.9'}
    reasons = result['reasons']
    metadata = None
    entries = {}
    try:
        loader_version = version(loader)
        if loader_version is None: raise ValueError('Use a numeric Fabric Loader version')
        if path.stat().st_size > MAX_BYTES: raise ValueError('Compressed file too large')
        with zipfile.ZipFile(path) as z:
            infos = z.infolist()
            if len(infos) > MAX_ENTRIES or sum(x.file_size for x in infos) > MAX_BYTES:
                raise ValueError('Archive exceeds compatibility scanner limits')
            for x in infos:
                p = PurePosixPath(x.filename)
                if (p.is_absolute() or '..' in p.parts or '\\' in x.filename
                        or ':' in x.filename or x.filename in entries):
                    raise ValueError('Unsafe or duplicate ZIP entry')
                if x.is_dir(): continue
                entries[x.filename] = z.read(x)
        metadata = json.loads(entries['fabric.mod.json'])
        if not isinstance(metadata, dict) or metadata.get('schemaVersion') != 1:
            raise ValueError('Only Fabric metadata schema 1 is supported')
        mod_id = metadata.get('id')
        result['id'] = mod_id
        if not isinstance(mod_id, str) or not re.fullmatch(r'[a-z][a-z0-9_-]{1,63}', mod_id):
            raise ValueError('Invalid mod ID')
        if mod_id in ADAPTER_IDS:
            result['native_adapter'] = ADAPTER_IDS[mod_id]
        if mod_id in RENDERERS:
            result['renderer_alternative'] = 'Use a separately tested native 1.8.9 renderer'
        if not isinstance(metadata.get('version'), str): reasons.append('Missing mod version')
        if metadata.get('environment', '*') not in ('*', 'client'):
            reasons.append('Not a client-compatible mod')
        for k in BAD_FEATURES:
            if metadata.get(k): reasons.append('Unsupported Fabric feature: '+k)
        deps = metadata.get('depends', {})
        if not isinstance(deps, dict): raise ValueError('Invalid depends object')
        mc = matches(deps.get('minecraft'))
        result['original_minecraft_constraint'] = deps.get('minecraft')
        # Preserve loader/Java requirements. Never silently relax them.
        for k, target in [('java', (java,0,0)), ('fabricloader', loader_version)]:
            if k in deps and matches(deps[k], target) is not True:
                reasons.append('Selected '+k+' does not satisfy '+str(deps[k]))
        extra = sorted(set(deps) - {'minecraft','java','fabricloader'})
        if extra: reasons.append('Unsupported required dependencies: '+', '.join(extra))
        for field in ('breaks', 'conflicts'):
            if metadata.get(field):
                reasons.append('Explicit conflict declarations require manual port review: '+field)
        eps = metadata.get('entrypoints', {})
        if not isinstance(eps, dict) or not eps:
            reasons.append('A standard main or client entrypoint is required')
            eps = {}
        requested = []
        for k, values in eps.items():
            if k not in ('main','client') or not isinstance(values, list) or not values:
                reasons.append('Unsupported entrypoint type: '+str(k))
                continue
            for v in values:
                if isinstance(v, dict) and v.get('adapter','default') == 'default':
                    v = v.get('value')
                if not isinstance(v,str) or not re.fullmatch(r'[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*',v,re.ASCII):
                    reasons.append('Unsupported entrypoint declaration')
                    continue
                requested.append((k,v.replace('.','/')))
        classes = {}
        for name,data in entries.items():
            upper=name.upper()
            if (upper.startswith('META-INF/VERSIONS/') or upper.startswith('META-INF/SERVICES/')
                or upper.startswith('META-INF/RYLUNE-') or upper.endswith(('.SF','.RSA','.DSA','.EC'))
                or upper.startswith('META-INF/SIG-') or name.lower().endswith(('.jar','.dll','.so','.dylib','.accesswidener','.classtweaker'))
                or name == 'module-info.class'):
                reasons.append('Unsupported archive entry: '+name)
            if upper == 'META-INF/MANIFEST.MF' and re.search(rb'(?im)(?:-Digest(?:-[A-Za-z]+)?:|^Multi-Release:\s*true)',data):
                reasons.append('Signed or multi-release manifest')
            if name.endswith('.class'):
                major, cname, strings, refs = read_pool(data)
                if name != cname+'.class': reasons.append('Class path mismatch: '+name)
                if major > java+44: reasons.append('Bytecode '+cname+' requires Java '+str(major-44))
                if cname.startswith(('java/','javax/','net/fabricmc/','net/minecraft/','org/lwjgl/','com/mojang/')):
                    reasons.append('Reserved class namespace: '+cname)
                classes[cname] = (strings, refs)
        if not classes: reasons.append('No Java classes')
        result['classes'] = len(classes)
        for kind,cname in requested:
            if cname not in classes:
                reasons.append('Entrypoint class missing: '+cname)
            else:
                want = 'net/fabricmc/api/'+('ClientModInitializer' if kind=='client' else 'ModInitializer')
                if want not in classes[cname][1]:
                    reasons.append('Entrypoint lacks expected Fabric initializer reference: '+cname)
        blocked = set()
        for cname,(strings,refs) in classes.items():
            for s in strings:
                if any(prefix in s for prefix in BLOCKED_PREFIXES):
                    blocked.add(cname+': modern game/API reference')
                    break
            for ref in refs:
                if ref.startswith('['): continue # component descriptors handled above
                if ref in classes or ref in LOADER_API: continue
                if ref.startswith(DYNAMIC_CLASSES):
                    blocked.add(cname+': '+ref)
                elif not ref.startswith(('java/','javax/')):
                    blocked.add(cname+': '+ref)
        if blocked:
            reasons.extend('Unsupported linkage: '+x for x in sorted(blocked)[:30])
            if len(blocked)>30: reasons.append('Additional unsupported references omitted')
        if mc is True and not reasons:
            result['status'] = 'NATIVE_CANDIDATE'
        elif not reasons and mc is False and requested:
            result['status'] = 'PORTABLE_CANDIDATE'
        elif not reasons:
            reasons.append('Minecraft version constraint cannot be confidently interpreted')
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError, zipfile.BadZipFile, struct.error) as exc:
        reasons.append(str(exc))
    return result, metadata, entries

def convert(source, destination, java=8, loader='0.16.14', *, permission=False):
    if not permission:
        raise ValueError('Confirm that you have permission to adapt the JAR')
    if destination.suffix.lower() != '.jar' or source.resolve() == destination.resolve():
        raise ValueError('Choose a separate output JAR')
    if destination.exists(): raise ValueError('Output already exists; will not overwrite')
    if destination.parent.name.lower() == 'mods':
        raise ValueError('Stage the output outside mods and test it explicitly')
    report, meta, entries = assess(source, java, loader)
    if report['status'] != 'PORTABLE_CANDIDATE':
        raise ValueError('Conversion refused: '+json.dumps(report))
    updated = dict(meta)
    updated['depends'] = dict(meta.get('depends', {}))
    updated['depends']['minecraft'] = '1.8.9'
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Keep original metadata and all class bytes; no signature or dependency bypass.
    original = entries['fabric.mod.json']
    provenance = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                  'preflight': report, 'notice': 'Experimental metadata adaptation; no bytecode translation or runtime guarantee.'}
    try:
        with destination.open('xb') as out:
            try:
                with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
                    for name,data in entries.items():
                        if name != 'fabric.mod.json': z.writestr(name,data)
                    z.writestr('fabric.mod.json',json.dumps(updated,indent=2))
                    z.writestr('META-INF/rylune-original-fabric.mod.json',original)
                    z.writestr('META-INF/rylune-compatibility.json',json.dumps(provenance,indent=2))
            except Exception:
                out.close()
                destination.unlink()
                raise
    except FileExistsError:
        raise ValueError('Output already exists; will not overwrite')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='cmd',required=True)
    for cmd in ('inspect','convert','native'):
        s=sub.add_parser(cmd)
        s.add_argument('jar',type=Path)
        s.add_argument('--java',type=int,choices=(8,17,21),default=8)
        s.add_argument('--loader',default='0.16.14')
        if cmd=='convert':
            s.add_argument('output',type=Path)
            s.add_argument('--permission-to-adapt',action='store_true')
        elif cmd=='native':
            s.add_argument('instance',type=Path)
    args=p.parse_args()
    try:
        if args.cmd=='inspect':
            report,_,_=assess(args.jar,args.java,args.loader)
            print(json.dumps(report,indent=2));return
        if args.cmd=='convert':
            print(json.dumps(convert(args.jar,args.output,args.java,args.loader,permission=args.permission_to_adapt),indent=2))
            print('Staged:',args.output,'— test in an isolated 1.8.9 profile before use.')
        else:
            report,_,_=assess(args.jar,args.java,args.loader)
            adapter=report.get('native_adapter')
            if not adapter: raise ValueError('No native feature adapter for this mod')
            options,description=adapter_for(adapter)
            print(description)
            print('Updated',write_options(args.instance,options))
            print('Do not install the original modern JAR; this enables a Rylune feature instead.')
    except (ValueError,OSError) as exc:
        p.exit(1,str(exc)+'\n')
if __name__=='__main__':
    main()
