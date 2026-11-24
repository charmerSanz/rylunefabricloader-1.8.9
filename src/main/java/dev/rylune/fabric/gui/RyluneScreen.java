package dev.rylune.fabric.gui;
import dev.rylune.fabric.*;
import net.minecraft.unmapped.C_85740840;
import java.util.Properties;
/** A standalone vanilla GuiScreen: does not patch HUD, chat or inventory rendering. */
public final class RyluneScreen extends C_85740840 {
    private final Properties draft=RyluneClient.config().properties();
    private String message="Click to change. Save applies immediately.";
    private static final String[] KEYS={"enabled","backgroundFps","hiddenFps","particleBudget","stateCache","stringPool","zoom","benchmark"};
    private static final String[] LABELS={"Rylune enabled","Background FPS","Hidden FPS","Particle budget / sec","Block-state hash cache*","Resource string pool*","Hold C to zoom","Frame benchmark"};
    private int left(){return Math.max(4,(f_05230747-Math.min(290,f_05230747-8))/2);}
    private int right(){return f_05230747-left();}
    private int top(){return Math.max(2,(f_07021018-208)/2);}
    private int step(){return Math.max(10,Math.min(17,(f_07021018-60)/9));}
    private void text(String s,int x,int y,int c){f_11884601.m_27673420(s,(float)x,(float)y,c);}
    private void center(String s,int y,int c){text(s,(f_05230747-f_11884601.m_09235706(s))/2,y,c);}
    @Override public void m_93956703(int mx,int my,float partial){
        int l=left(),r=right(),t=top(),h=step();m_57734177(0,0,f_05230747,f_07021018,0xE8101010);
        center("RYLUNE FABRIC  /  0.4 ALPHA",t+2,0xFFFFFF);center(RyluneClient.renderer(),t+14,0xAAAAAA);
        for(int i=0;i<KEYS.length;i++){int y=t+27+i*h;boolean hover=mx>=l&&mx<r&&my>=y&&my<y+h-1;
            m_57734177(l,y,r,y+h-1,hover?0xFF383838:0xFF242424);text(LABELS[i],l+5,y+Math.max(0,(h-8)/2),0xEEEEEE);
            String value=draft.getProperty(KEYS[i]);if("true".equals(value))value="ON";else if("false".equals(value))value="OFF";else if("0".equals(value))value="OFF";
            text(value,r-5-f_11884601.m_09235706(value),y+Math.max(0,(h-8)/2),0xFFFFFF);
        }
        int y=t+27+8*h;m_57734177(l,y,(l+r)/2-2,y+h,0xFFEEEEEE);m_57734177((l+r)/2+2,y,r,y+h,0xFF444444);
        text("Save & close",l+5,y+Math.max(0,(h-8)/2),0x111111);text("Cancel",(l+r)/2+7,y+Math.max(0,(h-8)/2),0xFFFFFF);
        if(y+h+9<f_07021018)center(message,y+h+3,0xCCCCCC);
        if(y+h+19<f_07021018)center("* Experimental; test before competitive play.",y+h+13,0x999999);
    }
    @Override protected void m_23755539(int x,int y,int button){
        if(button!=0||x<left()||x>=right())return;int relative=y-top()-27;if(relative<0)return;int i=relative/step();
        if(i==8){if(x<(left()+right())/2){if(RyluneClient.save(draft))f_78495264.m_52715402(null);else message="Save failed. See latest.log.";}else f_78495264.m_52715402(null);return;}
        if(i<0||i>=KEYS.length)return;String k=KEYS[i],v=draft.getProperty(k);
        if(i>=1&&i<=3){int[] options=i==3?new int[]{0,100,250,500,1000,2000}:new int[]{0,15,30,60,120};int current=Integer.parseInt(v),next=options[0];for(int n:options)if(n>current){next=n;break;}draft.setProperty(k,String.valueOf(next));}
        else draft.setProperty(k,String.valueOf(!Boolean.parseBoolean(v)));
    }
    @Override protected void m_29116903(char ch,int key){if(key==1)f_78495264.m_52715402(null);}
}
