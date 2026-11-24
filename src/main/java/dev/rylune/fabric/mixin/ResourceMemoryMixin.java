package dev.rylune.fabric.mixin;
import dev.rylune.fabric.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
/** Opt-in resource identifier string deduplication, inspired by FerriteCore. */
@Mixin(targets="net.minecraft.class_1653",remap=false)
public abstract class ResourceMemoryMixin {
    @Shadow @Final @Mutable protected String field_6615;
    @Shadow @Final @Mutable protected String field_6616;
    @Unique private static final StringPool rylune$pool=new StringPool(8192);
    @Inject(method="<init>(I[Ljava/lang/String;)V",at=@At("RETURN"),remap=false)
    private void rylune$dedup(int unused,String[] names,CallbackInfo ci){
        Config c=RyluneClient.config();if(c.enabled&&c.stringPool){field_6615=rylune$pool.canonical(field_6615);field_6616=rylune$pool.canonical(field_6616);}
    }
}
