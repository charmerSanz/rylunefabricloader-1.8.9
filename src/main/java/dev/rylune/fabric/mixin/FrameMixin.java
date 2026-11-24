package dev.rylune.fabric.mixin;
import dev.rylune.fabric.*;
import org.lwjgl.opengl.Display;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.concurrent.locks.LockSupport;
// Legacy Fabric intermediary generation 1, Minecraft 1.8.9 only.
@Mixin(targets="net.minecraft.class_1600",remap=false)
public abstract class FrameMixin {
    @Unique private long rylune$started;
    @Inject(method="method_2916()V",at=@At("HEAD"),remap=false)
    private void rylune$begin(CallbackInfo ci){rylune$started=System.nanoTime();if(RyluneClient.ready()&&!Boolean.getBoolean("rylune.noMenu"))dev.rylune.fabric.gui.MenuInput.poll(this);}
    @Inject(method="method_2916()V",at=@At("RETURN"),remap=false)
    private void rylune$end(CallbackInfo ci){
        if(!RyluneClient.ready()||!Display.isCreated())return;
        Config c=RyluneClient.config();if(!c.enabled){RyluneClient.record(0,false);return;}
        boolean active=Display.isActive(),visible=Display.isVisible();
        int cap=Performance.cap(c,active,visible);
        long wait=Performance.remaining(System.nanoTime()-rylune$started,cap);
        if(wait>0)LockSupport.parkNanos(wait);
        RyluneClient.record(System.nanoTime()-rylune$started,active&&visible);
    }
}
