import json, struct, tempfile, unittest, zipfile
from pathlib import Path
from rylune import scan, matches, apply_preset
from bridge import adapter_for,write_options
class Tests(unittest.TestCase):
    def test_ranges(self):
        self.assertTrue(matches('>=1.8 <1.9')); self.assertFalse(matches('>=1.20')); self.assertTrue(matches(['1.8.9','1.21'])); self.assertIsNone(matches('unknown')); self.assertTrue(matches('1.8.x'))
    def test_scan(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'mod.jar'
            def write(mc,major):
                with zipfile.ZipFile(p,'w') as z:
                    z.writestr('fabric.mod.json',json.dumps({'id':'test','depends':{'minecraft':mc}}));z.writestr('Test.class',b'\xca\xfe\xba\xbe'+struct.pack('>HH',0,major))
            write('1.8.9',52); self.assertEqual(scan(p)['status'],'CANDIDATE')
            write('1.21.11',65); self.assertEqual(scan(p)['status'],'UNSUPPORTED')
            write('1.8.9',61); self.assertEqual(scan(p)['status'],'UNSUPPORTED')
            p.write_text('broken');self.assertEqual(scan(p)['status'],'INVALID')
    def test_adapters(self):
        self.assertIsNone(adapter_for('unknown'))
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);write_options(p,{'custom':'keep','backgroundFps':'10'});changes,_=adapter_for('dynamic_fps');f=write_options(p,changes);data=f.read_text();self.assertIn('custom=keep',data);self.assertIn('backgroundFps=30',data);self.assertIn('hiddenFps=15',data);self.assertNotIn('backgroundFps=10',data);self.assertTrue(f.with_suffix('.properties.bridge.bak').exists());write_options(p,adapter_for('zoomify')[0]);self.assertIn('zoom=true',f.read_text())
    def test_java_constraint(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'mod.jar'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('fabric.mod.json',json.dumps({'id':'test','depends':{'minecraft':'1.8.9','java':'>=17'}}));z.writestr('Test.class',b'\xca\xfe\xba\xbe'+struct.pack('>HH',0,61))
            self.assertEqual(scan(p)['status'],'UNSUPPORTED');self.assertEqual(scan(p,java=17)['status'],'CANDIDATE')
    def test_preset(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); (p/'options.txt').write_text('key_key.attack:-100\nrenderDistance:12\n')
            apply_preset(p,'low'); data=(p/'options.txt').read_text();self.assertIn('key_key.attack:-100',data);self.assertIn('renderDistance:6',data);self.assertEqual(len(list(p.glob('*.bak'))),1)
if __name__=='__main__':unittest.main()
