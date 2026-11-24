package dev.rylune.fabric;
import java.io.*;
import java.nio.file.*;
import java.util.Properties;
public final class Config {
    public final boolean enabled, benchmark, stateCache, stringPool, zoom;
    public final int backgroundFps, hiddenFps, particleBudget;
    private Config(Properties p) {
        enabled=bool(p,"enabled",true); benchmark=bool(p,"benchmark",false);
        backgroundFps=num(p,"backgroundFps",30,0,240); hiddenFps=num(p,"hiddenFps",15,0,240);
        particleBudget=num(p,"particleBudget",0,0,20000);
        stateCache=bool(p,"stateCache",false); stringPool=bool(p,"stringPool",false); zoom=bool(p,"zoom",false);
    }
    private static boolean bool(Properties p,String k,boolean d){String v=p.getProperty(k);return v==null?d:"true".equalsIgnoreCase(v)?true:"false".equalsIgnoreCase(v)?false:d;}
    private static int num(Properties p,String k,int d,int min,int max){try{return Math.max(min,Math.min(max,Integer.parseInt(p.getProperty(k).trim())));}catch(RuntimeException e){return d;}}
    public Properties properties(){Properties p=new Properties();p.setProperty("enabled",String.valueOf(enabled));p.setProperty("benchmark",String.valueOf(benchmark));p.setProperty("backgroundFps",String.valueOf(backgroundFps));p.setProperty("hiddenFps",String.valueOf(hiddenFps));p.setProperty("particleBudget",String.valueOf(particleBudget));p.setProperty("stateCache",String.valueOf(stateCache));p.setProperty("stringPool",String.valueOf(stringPool));p.setProperty("zoom",String.valueOf(zoom));return p;}
    public static Config from(Properties p){return new Config(p);}
    public static void save(Path file,Properties edits)throws IOException{
        Properties p=new Properties();if(Files.exists(file))try(InputStream in=Files.newInputStream(file)){p.load(in);}p.putAll(edits);
        Path absolute=file.toAbsolutePath();Files.createDirectories(absolute.getParent());Path tmp=Files.createTempFile(absolute.getParent(),"rylune-",".tmp");
        try{try(OutputStream out=Files.newOutputStream(tmp)){p.store(out,"Rylune Fabric 0.4.0-alpha");}try{Files.move(tmp,absolute,StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}catch(AtomicMoveNotSupportedException e){Files.move(tmp,absolute,StandardCopyOption.REPLACE_EXISTING);}}finally{Files.deleteIfExists(tmp);}
    }
    public static Config defaults(){return new Config(new Properties());}
    public static Config load(Path file) throws IOException {
        if(!Files.exists(file)){
            if(file.getParent()!=null)Files.createDirectories(file.getParent());
            String text="# Rylune Fabric 0.4.0-alpha. Reloaded periodically while game runs.\n# 0 disables an individual FPS cap or particle budget.\nenabled=true\nbackgroundFps=30\nhiddenFps=15\n# Experimental: limits new particles per second. May hide visual cues.\nparticleBudget=0\n# Writes aggregate frame statistics every 10 seconds, only while focused.\nbenchmark=false\nstateCache=false\nstringPool=false\nzoom=false\n";
            Files.write(file,text.getBytes(java.nio.charset.StandardCharsets.UTF_8),StandardOpenOption.CREATE_NEW);
        }
        Properties p=new Properties();try(InputStream in=Files.newInputStream(file)){p.load(in);}return new Config(p);
    }
}
