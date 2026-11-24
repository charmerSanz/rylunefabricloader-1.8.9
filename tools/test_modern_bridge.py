import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from modern_bridge import assess, convert

class ModernBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        sources = {
            'net/fabricmc/api/ClientModInitializer.java': 'package net.fabricmc.api; public interface ClientModInitializer {void onInitializeClient();}',
            'demo/Portable.java': 'package demo; public class Portable implements net.fabricmc.api.ClientModInitializer {public void onInitializeClient(){System.out.println("portable");}}',
            'net/minecraft/ModernGame.java': 'package net.minecraft; public class ModernGame {public static void call(){}}',
            'demo/GameDependent.java': 'package demo; public class GameDependent implements net.fabricmc.api.ClientModInitializer {public void onInitializeClient(){net.minecraft.ModernGame.call();}}'
        }
        for name,code in sources.items():
            p=cls.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(code)
        subprocess.run(['javac','--release','8','-d',str(cls.root/'classes')]+[str(cls.root/name) for name in sources],check=True)
        subprocess.run(['javac','--release','17','-d',str(cls.root/'java17')]+[str(cls.root/name) for name in sources],check=True)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def fixture(self, name='Portable', updates=None, java=8, extra=None):
        meta={'schemaVersion':1,'id':'portable_demo','version':'1.0','environment':'client',
              'entrypoints':{'client':['demo.'+name]},
              'depends':{'minecraft':'>=1.21','java':'>=8','fabricloader':'>=0.16.0'}}
        meta.update(updates or {})
        p=self.root/(self._testMethodName+'.jar')
        with zipfile.ZipFile(p,'w') as z:
            z.writestr('fabric.mod.json',json.dumps(meta))
            z.write(self.root/('classes' if java==8 else 'java17')/'demo'/(name+'.class'),'demo/'+name+'.class')
            for k,v in (extra or {}).items(): z.writestr(k,v)
        return p

    def test_portable_conversion(self):
        p=self.fixture()
        self.assertEqual(assess(p)[0]['status'],'PORTABLE_CANDIDATE')
        out=self.root/'converted.jar'
        with self.assertRaises(ValueError): convert(p,out)
        convert(p,out,permission=True)
        with zipfile.ZipFile(p) as original,zipfile.ZipFile(out) as result:
            self.assertEqual(result.read('demo/Portable.class'),original.read('demo/Portable.class'))
            self.assertEqual(result.read('META-INF/rylune-original-fabric.mod.json'),original.read('fabric.mod.json'))
            self.assertEqual(json.loads(result.read('fabric.mod.json'))['depends']['minecraft'],'1.8.9')
            self.assertEqual(json.loads(result.read('fabric.mod.json'))['depends']['fabricloader'],'>=0.16.0')
        with self.assertRaises(ValueError): convert(p,out,permission=True)

    def test_reject_modern_game(self):
        p=self.fixture('GameDependent')
        r=assess(p)[0]
        self.assertEqual(r['status'],'REJECTED')
        self.assertTrue(any('modern game' in s for s in r['reasons']))

    def test_reject_java_mismatch(self):
        p=self.fixture(java=17)
        self.assertEqual(assess(p)[0]['status'],'REJECTED')
        self.assertEqual(assess(p,java=17)[0]['status'],'PORTABLE_CANDIDATE')

    def test_reject_mixin_and_dependencies(self):
        p=self.fixture(updates={'mixins':['example.json'],'depends':{'minecraft':'1.21.11','fabric-api':'*'}})
        r=assess(p)[0]
        self.assertEqual(r['status'],'REJECTED')
        self.assertTrue(any('mixins' in s for s in r['reasons']))
        self.assertTrue(any('fabric-api' in s for s in r['reasons']))

    def test_reject_signed(self):
        p=self.fixture(extra={'META-INF/TEST.SF':b'signed'})
        self.assertEqual(assess(p)[0]['status'],'REJECTED')

    def test_native_adapter(self):
        p=self.fixture(updates={'id':'lithium','mixins':['lithium.json']})
        r=assess(p)[0]
        self.assertEqual(r['status'],'REJECTED')
        self.assertEqual(r['native_adapter'],'lithium')

    def test_native_no_conversion(self):
        p=self.fixture(updates={'depends':{'minecraft':'1.8.9'}})
        self.assertEqual(assess(p)[0]['status'],'NATIVE_CANDIDATE')

    def test_loader_requirement(self):
        p=self.fixture(updates={'depends':{'minecraft':'1.21.11','fabricloader':'>=0.18.0'}})
        self.assertEqual(assess(p)[0]['status'],'REJECTED')

if __name__=='__main__': unittest.main()
