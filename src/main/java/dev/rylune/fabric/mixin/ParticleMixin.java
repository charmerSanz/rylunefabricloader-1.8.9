package dev.rylune.fabric.mixin;
import dev.rylune.fabric.*;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(targets="net.minecraft.unmapped.C_16190149",remap=false)
public abstract class ParticleMixin {
    @Unique private Performance.Budget rylune$budget;
    @Inject(method="m_20116138(Lnet/minecraft/unmapped/C_47540058;)V",at=@At("HEAD"),cancellable=true,remap=false)
    private void rylune$limit(CallbackInfo ci){
        Config c=RyluneClient.config();if(!RyluneClient.ready()||!c.enabled||c.particleBudget==0)return;
        if(rylune$budget==null)rylune$budget=new Performance.Budget();
        if(!rylune$budget.allow(System.nanoTime(),c.particleBudget))ci.cancel();
    }
}
