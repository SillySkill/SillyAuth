package com.tencent.cloud.sdktts;

import android.content.Context;
import android.content.res.AssetManager;
import android.util.Log;

import com.tencent.cloud.libqcloudtts.utils.AAILogger;

import org.json.JSONException;
import org.json.JSONObject;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Iterator;



public class OfflineResourceManager {
    static String TAG = OfflineResourceManager.class.getSimpleName();
    static String mPath = "";
    static ArrayList<String> mVoicesList;


    static String initOfflineResource(Context context){
        mPath = context.getFilesDir().getAbsolutePath() + "/wxofflinevoice/synthesizer/";
        Log.d(TAG, String.format("path: %s", mPath));
        File file = new File(mPath);
        if (file.exists()) {
            deleteDir(file);
        }
        file.mkdirs();

        AssetManager am = context.getAssets();
        try {
            String[] commonFiles = context.getAssets().list("common"); //离线合成必须的资源
            for (String commonFile : commonFiles) {
                copyFileToLocal(am, "common/" + commonFile, mPath, mPath + "common/");
            }

            String[] voiceFiles = context.getAssets().list("voices");//音色文件所在的文件夹，最少需要有一个音色
            for (String voiceFile : voiceFiles) {
                copyFileToLocal(am, "voices/" + voiceFile, mPath, mPath + "voices/");
            }
        } catch (IOException e) {
            AAILogger.e(TAG, "initOfflineResource Exception:" + Log.getStackTraceString(e));
            return null;
        }
        return mPath;
    }



    static ArrayList<String> getVioceList()  {

        if (mVoicesList != null && !mVoicesList.isEmpty()){
            return mVoicesList;
        }

        mVoicesList = new ArrayList<>();
        String path = mPath + "voices/config.json";

        try {
            File file=new File(path);
            FileReader fileReader = new FileReader(file);
            Reader reader = new InputStreamReader(new FileInputStream(file), "Utf-8");
            int ch = 0;
            StringBuffer sb = new StringBuffer();
            while ((ch = reader.read()) != -1) {
                sb.append((char) ch);
            }
            fileReader.close();
            reader.close();
            String jsonStr = sb.toString();

            try {
                JSONObject jsonObject = new JSONObject(jsonStr);
                Iterator it = jsonObject.keys();
                while(it.hasNext()){
                    String key = (String) it.next();// 获得key(音色名称)
                    mVoicesList.add(key);
                }
            } catch (JSONException e) {
                AAILogger.e(TAG, "getVioceList Exception:" + Log.getStackTraceString(e));
            }
        } catch (IOException e){
            AAILogger.e(TAG, "getVioceList Exception:" + Log.getStackTraceString(e));
        }

        return mVoicesList;
    }


    static private void copyFileToLocal(AssetManager am, String fileName, String path, String dirpath) throws IOException {
        InputStream in = am.open(fileName);
        byte[] buf = new byte[2048];
        int byteread = 0;
        String name = path + fileName;
        Log.d(TAG, name);
        if (dirpath != null) {
            File dir = new File(dirpath);
            if (!dir.exists())
                dir.mkdirs();
        }

        File file = new File(name);
        file.createNewFile();
        FileOutputStream fout = new FileOutputStream(file);
        while ((byteread = in.read(buf)) != -1) {
            fout.write(buf, 0, byteread);
        }
        fout.close();
        in.close();
    }

    static private void deleteDir(File file) {
        File[] contents = file.listFiles();
        if (contents != null) {
            for (File f : contents) {
                deleteDir(f);
            }
        }
        file.delete();
    }



}
