package dev.rylune.fabric;
import java.util.Arrays;
public final class Performance {
    private Performance(){}
    public static int cap(Config c, boolean active, boolean visible){return !c.enabled?0:!visible?c.hiddenFps:!active?c.backgroundFps:0;}
    public static long remaining(long elapsed,int fps){return fps<=0?0:Math.max(0L,1_000_000_000L/fps-Math.max(0L,elapsed));}
    public static final class Budget {
        private long start; private int used; private boolean initialized;
        public boolean allow(long now,int limit){if(limit<=0)return true;if(!initialized||now-start>=1_000_000_000L){initialized=true;start=now;used=0;}if(used>=limit)return false;used++;return true;}
    }
    public static final class Frames {
        private final long[] values=new long[100000];private int count;private long total;
        public void add(long ns){if(ns<=0||count==values.length)return;values[count++]=ns;total+=ns;}
        public int count(){return count;}
        public double fps(){return count==0?0:count*1e9/total;}
        public double low(){if(count==0)return 0;long[] copy=Arrays.copyOf(values,count);Arrays.sort(copy);int n=Math.max(1,(int)Math.ceil(count*.01));double sum=0;for(int i=count-n;i<count;i++)sum+=copy[i];return n*1e9/sum;}
        public double p99ms(){if(count==0)return 0;long[] copy=Arrays.copyOf(values,count);Arrays.sort(copy);return copy[Math.max(0,(int)Math.ceil(count*.99)-1)]/1e6;}
        public void clear(){count=0;total=0;}
    }
}
