package dev.rylune.fabric;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.loader.api.FabricLoader;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.concurrent.*;
import java.util.logging.Logger;
public final class RyluneClient implements ClientModInitializer {
    private static final Logger LOG=Logger.getLogger("RyluneFabric");
    private static volatile Config config=Config.defaults();
    private static volatile boolean ready=false;
    private static boolean frameHookSeen;
    public static void markFrameHook(){if(!frameHookSeen){frameHookSeen=true;LOG.info("Rylune Ornithe Gen 2 frame hook active; F8 opens settings in-game.");}}
    private static Path file, csv;
    private static final ScheduledExecutorService worker=Executors.newSingleThreadScheduledExecutor(r->{Thread t=new Thread(r,"Rylune-IO");t.setDaemon(true);return t;});
    private static final Performance.Frames frames=new Performance.Frames();
    private static long sampleStart=0;
    public static Config config(){return config;}
    public static boolean ready(){return ready;}
    @Override public void onInitializeClient(){
        file=FabricLoader.getInstance().getConfigDir().resolve("rylune.properties");
        csv=FabricLoader.getInstance().getGameDir().resolve("rylune-benchmark.csv");
        reload(); ready=true; worker.scheduleWithFixedDelay(RyluneClient::reload,2,2,TimeUnit.SECONDS);
        LOG.info("Rylune Fabric Ornithe Gen 2 initialized; awaiting frame hook; config: "+file);
    }
    private static long stamp=Long.MIN_VALUE;
    private static synchronized void reload(){try{long next=Files.exists(file)?Files.getLastModifiedTime(file).toMillis():Long.MIN_VALUE;if(next!=stamp||!Files.exists(file)){config=Config.load(file);stamp=Files.getLastModifiedTime(file).toMillis();}}catch(Exception e){LOG.warning("Config retained: "+e.getMessage());}}
    public static synchronized boolean save(java.util.Properties edits){if(!ready)return false;try{Config.save(file,edits);config=Config.load(file);stamp=Files.getLastModifiedTime(file).toMillis();return true;}catch(Exception e){LOG.warning("Config save failed: "+e);return false;}}
    public static String renderer(){return FabricLoader.getInstance().isModLoaded("radium")||FabricLoader.getInstance().isModLoaded("sodium")?"External renderer detected":"Vanilla renderer";}
    public static void record(long ns, boolean active){
        Config c=config;if(!ready||!c.enabled||!c.benchmark||!active){if(sampleStart!=0){frames.clear();sampleStart=0;}return;}
        long now=System.nanoTime();if(sampleStart==0)sampleStart=now;
        frames.add(ns);if(now-sampleStart<10_000_000_000L)return;
        Runtime r=Runtime.getRuntime();String row=String.format(Locale.ROOT,"%d,%d,%.2f,%.2f,%.3f,%d%n",System.currentTimeMillis(),frames.count(),frames.fps(),frames.low(),frames.p99ms(),(r.totalMemory()-r.freeMemory())/1048576);
        frames.clear();sampleStart=now;worker.execute(()->{try{if(!Files.exists(csv))Files.write(csv,"epoch_ms,frames,avg_fps,one_percent_low_fps,p99_ms,used_heap_mib\n".getBytes(StandardCharsets.UTF_8),StandardOpenOption.CREATE_NEW);Files.write(csv,row.getBytes(StandardCharsets.UTF_8),StandardOpenOption.APPEND);}catch(Exception e){LOG.warning("Benchmark write failed: "+e.getMessage());}});
    }
}
