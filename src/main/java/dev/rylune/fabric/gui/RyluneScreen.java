package dev.rylune.fabric.gui;
import dev.rylune.fabric.*;
import net.minecraft.class_388;
import java.util.Properties;
/** A standalone vanilla GuiScreen: does not patch HUD, chat or inventory rendering. */
public final class RyluneScreen extends class_388 {
    private final Properties draft=RyluneClient.config().properties();
    private String message="Click to change. Save applies immediately.";
    private static final String[] KEYS={"enabled","backgroundFps","hiddenFps","particleBudget","stateCache","stringPool","zoom","benchmark"};
    private static final String[] LABELS={"Rylune enabled","Background FPS","Hidden FPS","Particle budget / sec","Block-state hash cache*","Resource string pool*","Hold C to zoom","Frame benchmark"};
    private int left(){return Math.max(4,(field_1230-Math.min(290,field_1230-8))/2);}
    private int right(){return field_1230-left();}
    private int top(){return Math.max(2,(field_1231-208)/2);}
    private int step(){return Math.max(10,Math.min(17,(field_1231-60)/9));}
    private void text(String s,int x,int y,int c){field_1234.method_956(s,(float)x,(float)y,c);}
    private void center(String s,int y,int c){text(s,(field_1230-field_1234.method_954(s))/2,y,c);}
    @Override public void method_1025(int mx,int my,float partial){
        int l=left(),r=right(),t=top(),h=step();method_988(0,0,field_1230,field_1231,0xE8101010);
        center("RYLUNE FABRIC  /  0.3 ALPHA",t+2,0xFFFFFF);center(RyluneClient.renderer(),t+14,0xAAAAAA);
        for(int i=0;i<KEYS.length;i++){int y=t+27+i*h;boolean hover=mx>=l&&mx<r&&my>=y&&my<y+h-1;
            method_988(l,y,r,y+h-1,hover?0xFF383838:0xFF242424);text(LABELS[i],l+5,y+Math.max(0,(h-8)/2),0xEEEEEE);
            String value=draft.getProperty(KEYS[i]);if("true".equals(value))value="ON";else if("false".equals(value))value="OFF";else if("0".equals(value))value="OFF";
            text(value,r-5-field_1234.method_954(value),y+Math.max(0,(h-8)/2),0xFFFFFF);
        }
        int y=t+27+8*h;method_988(l,y,(l+r)/2-2,y+h,0xFFEEEEEE);method_988((l+r)/2+2,y,r,y+h,0xFF444444);
        text("Save & close",l+5,y+Math.max(0,(h-8)/2),0x111111);text("Cancel",(l+r)/2+7,y+Math.max(0,(h-8)/2),0xFFFFFF);
        if(y+h+9<field_1231)center(message,y+h+3,0xCCCCCC);
        if(y+h+19<field_1231)center("* Experimental; test before competitive play.",y+h+13,0x999999);
    }
    @Override protected void method_1026(int x,int y,int button){
        if(button!=0||x<left()||x>=right())return;int relative=y-top()-27;if(relative<0)return;int i=relative/step();
        if(i==8){if(x<(left()+right())/2){if(RyluneClient.save(draft))field_1229.method_2928(null);else message="Save failed. See latest.log.";}else field_1229.method_2928(null);return;}
        if(i<0||i>=KEYS.length)return;String k=KEYS[i],v=draft.getProperty(k);
        if(i>=1&&i<=3){int[] options=i==3?new int[]{0,100,250,500,1000,2000}:new int[]{0,15,30,60,120};int current=Integer.parseInt(v),next=options[0];for(int n:options)if(n>current){next=n;break;}draft.setProperty(k,String.valueOf(next));}
        else draft.setProperty(k,String.valueOf(!Boolean.parseBoolean(v)));
    }
    @Override protected void method_1024(char ch,int key){if(key==1)field_1229.method_2928(null);}
}
