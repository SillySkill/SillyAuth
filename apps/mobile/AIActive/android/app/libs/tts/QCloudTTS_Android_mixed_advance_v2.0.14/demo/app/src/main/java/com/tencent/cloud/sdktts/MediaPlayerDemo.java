package com.tencent.cloud.sdktts;

import android.media.AudioManager;
import android.media.MediaPlayer;
import android.text.TextUtils;

import com.tencent.cloud.libqcloudtts.MediaPlayer.QCloudPlayerCallback;
import com.tencent.cloud.libqcloudtts.MediaPlayer.QPlayerError;
import com.tencent.cloud.libqcloudtts.MediaPlayer.QplayerErrorCode;
import com.tencent.cloud.libqcloudtts.engine.Subtitle;
import com.tencent.cloud.libqcloudtts.utils.AAILogger;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

public class MediaPlayerDemo
        implements MediaPlayer.OnPreparedListener
        , MediaPlayer.OnCompletionListener
        , MediaPlayer.OnErrorListener {

    private String TAG = MediaPlayerDemo.class.getSimpleName();

    public static int STATE_INIT = 0; //初始化

    public static int STATE_PLAY = 1; //播放中

    public static int STATE_WAIT = 2; //等待下一句

    public static int STATE_COMPLETE = 3; //播放结束


    private int MaxQueue = 10;
    //播放器回调
    private QCloudPlayerCallback callback;

    private BlockingQueue<File> audioQueue; //语音队列

    private BlockingQueue<ArrayList<Subtitle>> allSubtitles;

    private List<String> audioTextQueue; //语音文本队列

    private List<String>  utteranceIdQueue; //语音文本队列对应的utteranceId

    private List<Boolean>  isDeleteFlags; //是否在播放完成后删除音频文件，入参音频支持byte[]和File，入参File时保留音频文件，入参byte[]时需要删除临时文件

    private String currentSentenceString; //正在播放的文本

    private int currentTextIndex; //当前播放的文本下标

    private MediaPlayer mediaPlayer; //播放器

    private File playingFile; //正在播放的文件

    private boolean isDeleteFlag;//正在播放的文件播放完成后是否需要删除

    private FileInputStream fis;

    private AtomicBoolean isPlaying = new AtomicBoolean(false); //是否正在播放

    private volatile boolean pauseFlag = false; //暂停标识

    private volatile boolean isExceptionCompletion = false; //pause 异常结束播放的标识

    private AtomicInteger state = new AtomicInteger(STATE_INIT);

    private List<Subtitle> subtitles;

    private int index = 0;

    public MediaPlayerDemo(QCloudPlayerCallback callback) {
        this.callback = callback;
        mediaPlayer = new MediaPlayer();
        mediaPlayer.setAudioStreamType(AudioManager.STREAM_MUSIC);
        mediaPlayer.setLooping(false);
        mediaPlayer.setOnCompletionListener(this);
        mediaPlayer.setOnErrorListener(this);
        mediaPlayer.setOnPreparedListener(this);
        this.audioQueue = new ArrayBlockingQueue<>(MaxQueue + 5);
        this.allSubtitles = new ArrayBlockingQueue<>(MaxQueue + 5);
        this.audioTextQueue = new ArrayList<>();
        this.utteranceIdQueue = new ArrayList<>();
        this.isDeleteFlags = new ArrayList<>();
        currentSentenceString = "";
        currentTextIndex = 0;


        Timer timer = new Timer();
        TimerTask timerTask = new TimerTask() {
            @Override
            public void run() {
                if (isPlaying.get() && mediaPlayer != null && !pauseFlag) {
                    try {
                        if (mediaPlayer.isPlaying()) { //防止报-38的错误
                            int duration = mediaPlayer.getDuration();
                            if (subtitles == null || subtitles.size() == 0) {
                                // 使用平均时长计算progress
                                if (duration != 0) {
                                    int currentPosition = mediaPlayer.getCurrentPosition();
                                    int textIndex = currentSentenceString.length() * currentPosition / duration;
                                    if (currentTextIndex == textIndex && textIndex < currentSentenceString.length()) {
                                        currentTextIndex = currentTextIndex + 1;
                                        String currentPlayString = currentSentenceString.substring(textIndex, textIndex + 1);
                                        if (callback != null) {
                                            callback.onTTSPlayProgress(currentPlayString, textIndex);
                                        }
                                    }
                                }
                            } else {
                                // 使用Server端回复的subtitiles计算progress，前提是设置mTtsController.setOnlineParam("EnableSubtitle", true);
                                if (duration != 0 && subtitles != null) {
                                    int currentPosition = mediaPlayer.getCurrentPosition();
                                    for (int i = subtitles.size() - 1; i >= index; i--) {
                                        int beginTime = subtitles.get(i).getBeginTime();
                                        if (currentPosition >= beginTime) {
                                            for (int j = index; j < i; j++) {
                                                if (callback != null)  {
                                                    String text = subtitles.get(j).getText();
                                                    int beginIndex = subtitles.get(j).getBeginIndex();
                                                    callback.onTTSPlayProgress(text, beginIndex);
                                                }
                                            }
                                            index = i;
                                        }
                                    }
                                }
                            }
                        }
                    }catch (Exception e){
                        //因这里与播放器不在同一个线程，调用mediaPlayer相关方法可能引发IllegalStateException、空指针等异常，这里try catch所有可能的异常
                        //不影响下次执行，无需处理
                        AAILogger.e(TAG, "MediaPlayerTimer Exception:" + e);
                    }
                }
            }
        };
        timer.schedule(timerTask, 0,16);
        pauseFlag = false;
    }

    synchronized public QPlayerError enqueue(byte[] audio,String text,String utteranceId) {
        return this.enqueue(audio, text, utteranceId, "");
    }

    synchronized public QPlayerError enqueue(byte[] audio,String text,String utteranceId, String responseJson) {
        if (audioQueue.size() >= MaxQueue){    //播放队列上限，请在onTTSPlayNext回调后再入参
            return new QPlayerError(null,QplayerErrorCode.QPLAYER_ERROR_CODE_PLAY_QUEUE_IS_FULL);
        }
        if (audio == null){
            return new QPlayerError(null,QplayerErrorCode.QPLAYER_ERROR_CODE_AUDIO_READ_FAILEDL);
        }

        //将byteBuffer保存到文件
        try {
            File file = File.createTempFile("MediaPlayerDemo", ".mp3");
            OutputStream os = new FileOutputStream(file);
            os.write(audio);
            os.flush();
            os.close();

            //数据入库
            try {
                this.audioQueue.put(file);
                this.audioTextQueue.add(text);
                this.utteranceIdQueue.add(utteranceId);
                this.isDeleteFlags.add(true);
                this.allSubtitles.put(parseJson(responseJson));

                // 检查是否需要
                if (!pauseFlag && isPlaying.compareAndSet(false, true)) {
                    playAudio(dequeue());
                }
                return null;

            } catch (InterruptedException e) {
                return new QPlayerError(e, QplayerErrorCode.QPLAYER_ERROR_CODE_UNKNOW);
            }

        } catch (IOException e) {
            return new QPlayerError(e,QplayerErrorCode.QPLAYER_ERROR_CODE_UNKNOW);
        }
    }


    synchronized public QPlayerError enqueue(File audio,String text,String utteranceId, String responseJson) {
        if (audioQueue.size() >= MaxQueue){    //播放队列上限，请在onTTSPlayNext回调后再入参
            return new QPlayerError(null,QplayerErrorCode.QPLAYER_ERROR_CODE_PLAY_QUEUE_IS_FULL);
        }
        if (audio == null){
            return new QPlayerError(null,QplayerErrorCode.QPLAYER_ERROR_CODE_AUDIO_READ_FAILEDL);
        }
        try{
            if(!audio.exists())
            {
                return new QPlayerError(null,QplayerErrorCode.QPLAYER_ERROR_CODE_AUDIO_READ_FAILEDL);
            }
        } catch (SecurityException e){
            return new QPlayerError(null,QplayerErrorCode.QPLAYER_ERROR_CODE_AUDIO_READ_FAILEDL);
        }

        //数据入库
        try {
            this.audioQueue.put(audio);
            this.audioTextQueue.add(text);
            this.utteranceIdQueue.add(utteranceId);
            this.isDeleteFlags.add(false);
            this.allSubtitles.add(parseJson(responseJson));

            // 检查是否需要
            if (!pauseFlag && isPlaying.compareAndSet(false, true)) {
                playAudio(dequeue());
            }
            return null;

        } catch (InterruptedException e) {
            return new QPlayerError(e,QplayerErrorCode.QPLAYER_ERROR_CODE_UNKNOW);
        }
    }

    private ArrayList<Subtitle> parseJson(String json) {
        ArrayList<Subtitle> subtitles = new ArrayList<>();
        try {
            if (TextUtils.isEmpty(json)) {
                return subtitles;
            }
            JSONObject jsonObject = new JSONObject(json);
            JSONObject response = jsonObject.getJSONObject("Response");
            if (response == null) {
                return subtitles;
            }
            // 解析Subtitles
            JSONArray subtitlesArray = response.getJSONArray("Subtitles");
            for (int i = 0; i < subtitlesArray.length(); i++) {
                JSONObject item = subtitlesArray.getJSONObject(i);
                subtitles.add(new Subtitle(
                        item.getString("Text"),
                        item.getInt("BeginTime"),
                        item.getInt("EndTime"),
                        item.getInt("BeginIndex"),
                        item.getInt("EndIndex"),
                        item.getString("Phoneme")
                ));
            }
            return subtitles;
        } catch (JSONException e) {
            AAILogger.e(TAG,"parse json error: "+ e.getMessage());
        }
        return subtitles;
    }


    public int getAudioQueueSize(){
        return audioQueue.size();
    }

    public int getAudioAvailableQueueSize(){
        return MaxQueue - audioQueue.size();
    }

    public int getPlayState(){
        return state.get();
    }

    /**
     * 数据出队列
     * @return audio
     */
    public File dequeue() {
        try {
            if (this.audioTextQueue.size() > 0) {
                this.currentSentenceString = this.audioTextQueue.get(0);
                this.audioTextQueue.remove(0);

                String utteranceId = this.utteranceIdQueue.get(0);
                this.utteranceIdQueue.remove(0);

                isDeleteFlag = isDeleteFlags.get(0);
                isDeleteFlags.remove(0);

                if (callback != null){
                    callback.onTTSPlayNext(currentSentenceString, utteranceId);
                }
            }
            ArrayList<Subtitle> tempSubtitles = this.allSubtitles.poll(100, TimeUnit.MILLISECONDS);
            if (tempSubtitles != null) {
                subtitles = Collections.synchronizedList(tempSubtitles);
            }
            index = 0;
            return this.audioQueue.poll(100, TimeUnit.MILLISECONDS);
        } catch (InterruptedException e) {
            if (callback != null) {
                callback.onTTSPlayError(new QPlayerError(e,QplayerErrorCode.QPLAYER_ERROR_CODE_UNKNOW));
            }
            AAILogger.e(TAG, "dequeue Exception:" + e);
            return null;
        }

    }



    @Override
    public void onCompletion(MediaPlayer mediaPlayer) {
//        AAILogger.d("sendError","MusicService.onCompletion()"+"mp.isPlaying()?"+mediaPlayer.isPlaying());
        //删除音频文件
        deleteAudioFile();
        if (pauseFlag) {
            isExceptionCompletion=true;
            return;
        }

        playOnCompletionException();

    }

    private void playOnCompletionException(){
        // 检查是否需要
        File audio = dequeue();
        if (audio != null) {
            //还有数据，继续播放
            playAudio(audio);
        } else {
            //没有数据了，设置未播放
            isPlaying.set(false);
            //设置为等待状态
            state.set(STATE_WAIT);
            if (callback != null)  {
                callback.onTTSPlayWait();
            }
        }
    }


    @Override
    public boolean onError(MediaPlayer mediaPlayer, int i, int i1) {
        //出错了
        if (callback != null) {
            callback.onTTSPlayStop();
        }

        //设置没有播放
        isPlaying.set(false);

        //删除音频文件
        deleteAudioFile();

        //设置状态为结束
        state.set(STATE_COMPLETE);

        if (callback != null) {
            callback.onTTSPlayError(new QPlayerError(null,QplayerErrorCode.QPLAYER_ERROR_CODE_EXCEPTION));
        }

        return false;
    }

    @Override
    public void onPrepared(MediaPlayer mediaPlayer) {
        int status = state.get();
        //设置正在播放
        isPlaying.set(true);

        //开始播放
        mediaPlayer.start();

        //设置为播放状态
        state.set(STATE_PLAY);

        if (callback != null) {
            //播放器准备好了
            if (status == STATE_INIT) {
                //第一次播放
                callback.onTTSPlayStart();
            } else if (status == STATE_WAIT) {
                //非连续，恢复播放
                callback.onTTSPlayResume();

            }
        }
    }

    //播放音频
    private void playAudio(File audio) {
        if (mediaPlayer == null){
            mediaPlayer = new MediaPlayer();
            mediaPlayer.setAudioStreamType(AudioManager.STREAM_MUSIC);
            mediaPlayer.setLooping(false);
            mediaPlayer.setOnCompletionListener(this);
            mediaPlayer.setOnErrorListener(this);
            mediaPlayer.setOnPreparedListener(this);
        }
        try {
            playingFile = audio;
            //先reset mediaplayer
            mediaPlayer.reset();
            //设置播放文件的目录
            fis = new FileInputStream(playingFile);
            int fileLen = fis.available();
            mediaPlayer.setDataSource(fis.getFD(), 0, fileLen);
            //当句的下标重置
            currentTextIndex = 0;
            // 开始播放
            mediaPlayer.prepare();
            fis.close();

        } catch (Exception e) {
            if (callback != null) {
                callback.onTTSPlayError(new QPlayerError(e,QplayerErrorCode.QPLAYER_ERROR_CODE_EXCEPTION));
            }
            AAILogger.e(TAG, "playAudio Exception:" + e);
        }
    }

    //停止播放
    private QPlayerError stopAudio() {
        try {
            pauseFlag = true;
            if(mediaPlayer != null){
                mediaPlayer.stop();
                mediaPlayer.release();
            }
            mediaPlayer = null;
            state.set(STATE_INIT);
            return null;
        } catch (Exception e) {
            return null;
//            return new QPlayerError(e,QPLAYER_ERROR_CODE_EXCEPTION);
        }
    }

    private void deleteAudioFile() {
        if (!isDeleteFlag){
            playingFile = null;
            return;
        }

        if (playingFile != null
                && playingFile.exists()) {
            if(!playingFile.delete() ) {
                AAILogger.e(TAG, "remove file " + playingFile.getName() + " fail");
            }
            playingFile = null;
        }
    }

    //stop后清理所有音频文件
    private void deleteAllAudioFile() {
        try {
            File f = null;
            do {
                if (audioQueue.size() < 1) {
                    f = null;
                    break;
                }
                f = audioQueue.poll(200, TimeUnit.MILLISECONDS);
                boolean b  = isDeleteFlags.get(0);
                isDeleteFlags.remove(0);

                if (b && f != null && f.exists()) {
                    f.delete();
                    f = null;
                }
            }while (f != null);
        } catch (InterruptedException e) {
            e.printStackTrace();
            AAILogger.e(TAG, "io Exception:" + e);
        }
        isDeleteFlags.clear();
        audioQueue.clear();
        allSubtitles.clear();
    }




    /**
     * 停止播放
     */
    public QPlayerError StopPlay() {

        QPlayerError error = stopAudio();
        deleteAllAudioFile();
        this.audioTextQueue.clear();
        this.utteranceIdQueue.clear();
        isPlaying.set(false);
        pauseFlag = false;
        //调用回调
        if (callback != null) {
            callback.onTTSPlayStop();
        }
        return error;
    }

    public QPlayerError PausePlay(){
        if(mediaPlayer == null){
            return null;
        }

        //处于播放状态时 才会调pause
        if(state.get() == STATE_PLAY){
            pauseFlag = true;
            mediaPlayer.pause();
            if (callback != null) {
                callback.onTTSPlayPause();
            }
        }
        return null;
    }

    public QPlayerError ResumePlay(){

        if (!pauseFlag) return null;
        pauseFlag = false;
        //设置为播放状态
        if(isExceptionCompletion){
            //点击pause 时调 mediaPlayer方法调用的方法
            playOnCompletionException();
            isExceptionCompletion = false;
        }else{
            if(mediaPlayer == null){
                return null;
            }
            mediaPlayer.start();
        }
        if (callback != null) {
            callback.onTTSPlayResume();
        }
        return null;
    }

}
