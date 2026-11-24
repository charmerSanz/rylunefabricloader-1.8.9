package dev.rylune.fabric.gui;
import net.minecraft.client.Minecraft;
import org.lwjgl.input.Keyboard;
import org.lwjgl.opengl.Display;
/** F8 avoids the OneClient Right Shift menu; open only during gameplay; never consume input in other GUI screens. */
public final class MenuInput {
    private static boolean wasDown;
    private MenuInput(){}
    public static void poll(Object game){
        if(!Keyboard.isCreated()||!Display.isCreated())return;
        Minecraft mc=(Minecraft)game;boolean down=Keyboard.isKeyDown(Keyboard.KEY_F8);
        if(down&&!wasDown&&Display.isActive()&&mc.f_70816363==null&&mc.f_26407825!=null)mc.m_52715402(new RyluneScreen());
        wasDown=down;
    }
    public static boolean zoomHeld(){Minecraft mc=Minecraft.m_20213497();return mc!=null&&mc.f_70816363==null&&mc.f_26407825!=null&&Display.isCreated()&&Display.isActive()&&Keyboard.isCreated()&&Keyboard.isKeyDown(Keyboard.KEY_C);}
}
