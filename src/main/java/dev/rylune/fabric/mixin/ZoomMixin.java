package dev.rylune.fabric.mixin;
import dev.rylune.fabric.*;
import dev.rylune.fabric.gui.MenuInput;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
/** Native hold-to-zoom replacement, not a Zoomify JAR translator. */
@Mixin(targets="net.minecraft.class_524",remap=false)
public abstract class ZoomMixin {
    @Inject(method="method_1327(FZ)F",at=@At("RETURN"),cancellable=true,remap=false)
    private void rylune$zoom(float tick,boolean worldFov,CallbackInfoReturnable<Float> ci){Config c=RyluneClient.config();if(worldFov&&c.enabled&&c.zoom&&MenuInput.zoomHeld())ci.setReturnValue(Math.max(1f,ci.getReturnValue()/3f));}
}
