package dev.rylune.fabric.gui;
import net.minecraft.class_1600;
import org.lwjgl.input.Keyboard;
import org.lwjgl.opengl.Display;
/** Open only during gameplay; never consume input in other GUI screens. */
public final class MenuInput {
    private static boolean wasDown;
    private MenuInput(){}
    public static void poll(Object game){
        if(!Keyboard.isCreated()||!Display.isCreated())return;
        class_1600 mc=(class_1600)game;boolean down=Keyboard.isKeyDown(Keyboard.KEY_RSHIFT);
        if(down&&!wasDown&&Display.isActive()&&mc.field_3816==null&&mc.field_3803!=null)mc.method_2928(new RyluneScreen());
        wasDown=down;
    }
    public static boolean zoomHeld(){class_1600 mc=class_1600.method_2965();return mc!=null&&mc.field_3816==null&&mc.field_3803!=null&&Display.isCreated()&&Display.isActive()&&Keyboard.isCreated()&&Keyboard.isKeyDown(Keyboard.KEY_C);}
}
