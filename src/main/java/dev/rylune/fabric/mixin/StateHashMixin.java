package dev.rylune.fabric.mixin;
import dev.rylune.fabric.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
/** Memoizes vanilla immutable block-state property hashes, not world state or physics. */
@Mixin(targets="net.minecraft.unmapped.C_06229646$C_07015679",remap=false)
public abstract class StateHashMixin {
    @Unique private int rylune$hash;
    @Unique private volatile boolean rylune$cached;
    @Inject(method="hashCode()I",at=@At("HEAD"),cancellable=true,remap=false)
    private void rylune$read(CallbackInfoReturnable<Integer> ci){Config c=RyluneClient.config();if(c.enabled&&c.stateCache&&rylune$cached)ci.setReturnValue(rylune$hash);}
    @Inject(method="hashCode()I",at=@At("RETURN"),remap=false)
    private void rylune$write(CallbackInfoReturnable<Integer> ci){Config c=RyluneClient.config();if(c.enabled&&c.stateCache&&!rylune$cached){rylune$hash=ci.getReturnValue();rylune$cached=true;}}
}
