package dev.rylune.fabric.mixin;
import dev.rylune.fabric.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
/** Opt-in resource identifier string deduplication, inspired by FerriteCore. */
@Mixin(targets="net.minecraft.unmapped.C_22168528",remap=false)
public abstract class ResourceMemoryMixin {
    @Shadow @Final @Mutable protected String f_47860744;
    @Shadow @Final @Mutable protected String f_49544811;
    @Unique private static final StringPool rylune$pool=new StringPool(8192);
    @Inject(method="<init>(I[Ljava/lang/String;)V",at=@At("RETURN"),remap=false)
    private void rylune$dedup(int unused,String[] names,CallbackInfo ci){
        Config c=RyluneClient.config();if(c.enabled&&c.stringPool){f_47860744=rylune$pool.canonical(f_47860744);f_49544811=rylune$pool.canonical(f_49544811);}
    }
}
