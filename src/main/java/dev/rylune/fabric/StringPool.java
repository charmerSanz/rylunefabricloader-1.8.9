package dev.rylune.fabric;
import java.lang.ref.WeakReference;
import java.util.WeakHashMap;
/** Bounded weak canonicalization for immutable strings. Never uses String.intern. */
public final class StringPool {
    private final WeakHashMap<String,WeakReference<String>> values=new WeakHashMap<>();
    private final int capacity;
    public StringPool(int capacity){if(capacity<1)throw new IllegalArgumentException();this.capacity=capacity;}
    public synchronized String canonical(String value){
        if(value==null)return null;
        WeakReference<String> ref=values.get(value);String existing=ref==null?null:ref.get();if(existing!=null)return existing;
        if(values.size()<capacity)values.put(value,new WeakReference<>(value));return value;
    }
    public synchronized int size(){return values.size();}
}
