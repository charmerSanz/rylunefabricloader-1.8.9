package dev.rylune.fabric;
import java.nio.file.*;
public final class SelfTest {
    private static void check(boolean v){if(!v)throw new AssertionError();}
    public static void main(String[] args)throws Exception{
        Path dir=Files.createTempDirectory("rylune-test"),file=dir.resolve("config.properties");
        Config c=Config.load(file);check(c.enabled&&c.particleBudget==0);check(Performance.cap(c,true,true)==0);check(Performance.cap(c,false,true)==30);check(Performance.cap(c,false,false)==15);
        check(Performance.remaining(10_000_000,20)==40_000_000);check(Performance.remaining(60_000_000,20)==0);
        Files.write(file,"enabled=false\nbackgroundFps=900\nparticleBudget=bad\n".getBytes("UTF-8"));c=Config.load(file);check(!c.enabled&&c.backgroundFps==240&&c.particleBudget==0);check(Performance.cap(c,false,false)==0);
        Performance.Budget b=new Performance.Budget();check(b.allow(0,2));check(b.allow(1,2));check(!b.allow(2,2));check(b.allow(1_000_000_000L,2));check(b.allow(1_000_000_001L,0));
        Performance.Frames f=new Performance.Frames();for(int i=0;i<100;i++)f.add(10_000_000);check(f.fps()==100&&f.low()==100&&f.p99ms()==10);f.clear();check(f.count()==0);
        java.util.Properties edits=new java.util.Properties();edits.setProperty("stateCache","true");edits.setProperty("stringPool","true");edits.setProperty("zoom","true");Config.save(file,edits);c=Config.load(file);check(c.stateCache&&c.stringPool&&c.zoom&&!c.enabled&&c.backgroundFps==240);
        StringPool pool=new StringPool(2);String x=new String("alpha"), y=new String("alpha"), z=new String("beta");check(x!=y&&pool.canonical(x)==x&&pool.canonical(y)==x);check(pool.canonical(z)==z);check(pool.canonical("gamma").equals("gamma")&&pool.size()<=2&&pool.canonical(null)==null);
        Files.delete(file);Files.delete(dir);System.out.println("Rylune self-tests passed");
    }
}
