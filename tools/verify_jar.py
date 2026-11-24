import json, sys, zipfile, struct
with zipfile.ZipFile(sys.argv[1]) as z:
    names=z.namelist(); meta=json.loads(z.read('fabric.mod.json'))
    assert meta['depends']['minecraft']=='1.8.9'
    assert 'dev/rylune/fabric/RyluneClient.class' in names
    assert 'dev/rylune/fabric/gui/RyluneScreen.class' in names
    assert 'dev/rylune/fabric/StringPool.class' in names
    assert meta['version']=='0.3.0-alpha'
    for n in names:
        if n.endswith('.class'):
            assert n.startswith('dev/rylune/fabric/'), n
            assert struct.unpack('>H',z.read(n)[6:8])[0]==52, n
    mix=json.loads(z.read('rylune.mixins.json'))
    for c in mix['client']:
        assert mix['package'].replace('.','/')+'/'+c+'.class' in names
print('JAR layout and Java 8 bytecode verified (not a game launch).')
