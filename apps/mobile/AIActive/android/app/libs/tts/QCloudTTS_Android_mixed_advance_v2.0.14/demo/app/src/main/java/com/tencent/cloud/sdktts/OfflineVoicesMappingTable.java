package com.tencent.cloud.sdktts;



import java.util.ArrayList;
import java.util.HashMap;

/**
 * 在线 离线音色映射表，记录了部分在线音色对应的离线音色，方便在线切换离线时选择
 */
public class OfflineVoicesMappingTable {

    static  HashMap<Integer, String> voices ;

    static String getOfflineVoice(int OnlineVoice){
        if (null == voices){
            initVoices();
        }

        if (voices.containsKey(OnlineVoice)) {
            String offlineVoice = (String) voices.get(OnlineVoice);
            ArrayList<String>  offlineVoiceList = OfflineResourceManager.getVioceList(); //读取资源文件内已集成的离线音色列表
            for(String voice:offlineVoiceList){
                if (voice.equals(offlineVoice)){
                    return offlineVoice;  //找到了匹配的离线音色
                }
            }
        }
        return null;    //没找到匹配的离线音色
    }


    /**
     * db1           --- 智聆 1002  101002
     * db3           --- 智萌 101015
     * db7           --- 智甜 101016
     * f0            --- 智莉 101005 1005
     * f2            --- 智芸 1009 101009
     * femozhifou    --- 智蓉 1017  101017
     * fn            --- 智瑜 1001 101001
     * kefu          --- 智美 1003 101003
     * kefu2         --- 智娜 1007 101007
     * kefu3         --- 智琪 1008  101008
     * m0            --- 智云 1004 101004
     * m25           --- 智华 1010 101010
     * M206          --- 智皓 101024
     * memozhifou    --- 智靖 1018 101018
     * newsman       --- 智宁 101014
     * pb            --- 智逍遥 10510000 100510000
     * xiaowei       --- 智言 101006
     */

    /**
     * HashMap<在线音色id, 离线音色名>
     */
    private static void initVoices() {

        voices = new HashMap<Integer, String>() ;

        voices.put(1001, "fn"); 
        voices.put(101001, "fn");

        voices.put(1002, "db1");
        voices.put(101002, "db1");

        voices.put(1004, "m0");
        voices.put(101004, "m0");

        voices.put(1005, "f0");
        voices.put(101005, "f0");

        voices.put(1003, "kefu");
        voices.put(101003, "kefu");

        voices.put(1007, "kefu2");
        voices.put(101007, "kefu2");

        voices.put(101006, "xiaowei");

        voices.put(101014, "newsman");

        voices.put(101016, "db7");

        voices.put(1017, "femozhifou");
        voices.put(101017, "femozhifou");

        voices.put(1008, "kefu3");
        voices.put(101008, "kefu3");

        voices.put(10510000, "pb");
        voices.put(100510000, "pb");

        voices.put(101015, "db3");

        voices.put(1009, "f2");
        voices.put(101009, "f2");

        voices.put(1010, "m25");
        voices.put(101010, "m25");

        voices.put(101024, "M206");

        voices.put(1018, "memozhifou");
        voices.put(101018, "memozhifou");

    }



}
