package com.jcoding.aiactivity.opengl;

import android.content.Context;
import android.graphics.Bitmap;
import android.opengl.GLES20;
import android.opengl.GLSurfaceView;
import android.opengl.Matrix;
import android.util.Log;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.util.ArrayList;
import java.util.List;

import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/**
 * 3D球体OpenGL ES渲染器
 * 用于渲染抽奖球体和卡片
 */
public class SphereGLRenderer implements GLSurfaceView.Renderer {

    private static final String TAG = "SphereGLRenderer";

    private Context context;
    private List<CardData> cards = new ArrayList<>();
    private List<Bitmap> cardTextures = new ArrayList<>();

    // 顶点着色器代码
    private final String vertexShaderCode =
        "uniform mat4 uMVPMatrix;" +
        "attribute vec4 aPosition;" +
        "attribute vec2 aTexCoord;" +
        "varying vec2 vTexCoord;" +
        "void main() {" +
        "  gl_Position = uMVPMatrix * aPosition;" +
        "  vTexCoord = aTexCoord;" +
        "}";

    // 片段着色器代码
    private final String fragmentShaderCode =
        "precision mediump float;" +
        "varying vec2 vTexCoord;" +
        "uniform sampler2D uTexture;" +
        "void main() {" +
        "  gl_FragColor = texture2D(uTexture, vTexCoord);" +
        "}";

    private int program;
    private int mVPMatrixHandle;
    private int positionHandle;
    private int texCoordHandle;
    private int textureHandle;

    // 矩阵
    private final float[] mMVPMatrix = new float[16];
    private final float[] mProjectionMatrix = new float[16];
    private final float[] mViewMatrix = new float[16];
    private final float[] mModelMatrix = new float[16];

    // 旋转角度
    private float angleX = 0;
    private float angleY = 0;
    private boolean isRotating = true;
    private float rotationSpeed = 0.5f;

    // 选中卡片索引
    private int selectedIndex = -1;

    public SphereGLRenderer(Context context) {
        this.context = context;
    }

    @Override
    public void onSurfaceCreated(GL10 gl, EGLConfig config) {
        // 使用深蓝色背景便于调试
        GLES20.glClearColor(0.1f, 0.1f, 0.3f, 1.0f);
        GLES20.glEnable(GLES20.GL_DEPTH_TEST);
        GLES20.glEnable(GLES20.GL_BLEND);
        GLES20.glBlendFunc(GLES20.GL_SRC_ALPHA, GLES20.GL_ONE_MINUS_SRC_ALPHA);

        // 编译着色器
        int vertexShader = loadShader(GLES20.GL_VERTEX_SHADER, vertexShaderCode);
        int fragmentShader = loadShader(GLES20.GL_FRAGMENT_SHADER, fragmentShaderCode);

        // 创建程序
        program = GLES20.glCreateProgram();
        GLES20.glAttachShader(program, vertexShader);
        GLES20.glAttachShader(program, fragmentShader);
        GLES20.glLinkProgram(program);

        // 获取属性位置
        positionHandle = GLES20.glGetAttribLocation(program, "aPosition");
        texCoordHandle = GLES20.glGetAttribLocation(program, "aTexCoord");
        mVPMatrixHandle = GLES20.glGetUniformLocation(program, "uMVPMatrix");
        textureHandle = GLES20.glGetUniformLocation(program, "uTexture");

        Log.d(TAG, "OpenGL ES program created, positionHandle=" + positionHandle);
    }

    @Override
    public void onSurfaceChanged(GL10 gl, int width, int height) {
        GLES20.glViewport(0, 0, width, height);

        float ratio = (float) width / height;
        Matrix.frustumM(mProjectionMatrix, 0, -ratio, ratio, -1, 1, 1, 100);
    }

    private int frameCount = 0;

    @Override
    public void onDrawFrame(GL10 gl) {
        frameCount++;
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT | GLES20.GL_DEPTH_BUFFER_BIT);

        // 每100帧记录一次日志
        if (frameCount % 100 == 0) {
            Log.d(TAG, "onDrawFrame: 渲染第 " + frameCount + " 帧，卡片数量=" + cards.size());
        }

        // 设置相机位置
        Matrix.setLookAtM(mViewMatrix, 0,
            0, 0, 5,  // 相机位置
            0, 0, 0,  // 看向原点
            0, 1, 0); // 上方向

        // 自动旋转
        if (isRotating) {
            angleY += rotationSpeed;
        }

        // 计算模型矩阵（旋转）
        Matrix.setRotateM(mModelMatrix, 0, angleY, 0, 1, 0);
        Matrix.rotateM(mModelMatrix, 0, angleX, 1, 0, 0);

        // 计算MVP矩阵
        Matrix.multiplyMM(mMVPMatrix, 0, mViewMatrix, 0, mModelMatrix, 0);
        Matrix.multiplyMM(mMVPMatrix, 0, mProjectionMatrix, 0, mMVPMatrix, 0);

        // 使用程序
        GLES20.glUseProgram(program);

        // 绘制所有卡片
        for (int i = 0; i < cards.size(); i++) {
            drawCard(i);
        }
    }

    private void drawCard(int index) {
        CardData card = cards.get(index);

        // 设置顶点数据
        FloatBuffer vertexBuffer = card.getVertexBuffer();
        FloatBuffer texCoordBuffer = card.getTexCoordBuffer();

        GLES20.glEnableVertexAttribArray(positionHandle);
        GLES20.glVertexAttribPointer(positionHandle, 3, GLES20.GL_FLOAT, false, 0, vertexBuffer);

        GLES20.glEnableVertexAttribArray(texCoordHandle);
        GLES20.glVertexAttribPointer(texCoordHandle, 2, GLES20.GL_FLOAT, false, 0, texCoordBuffer);

        // 绑定纹理
        if (index < cardTextures.size()) {
            GLES20.glActiveTexture(GLES20.GL_TEXTURE0);
            GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, loadTexture(cardTextures.get(index)));
            GLES20.glUniform1i(textureHandle, 0);
        }

        // 设置MVP矩阵
        GLES20.glUniformMatrix4fv(mVPMatrixHandle, 1, false, mMVPMatrix, 0);

        // 绘制
        GLES20.glDrawArrays(GLES20.GL_TRIANGLES, 0, 6);
    }

    private int loadShader(int type, String shaderCode) {
        int shader = GLES20.glCreateShader(type);
        GLES20.glShaderSource(shader, shaderCode);
        GLES20.glCompileShader(shader);
        return shader;
    }

    private int loadTexture(Bitmap bitmap) {
        if (bitmap == null) return 0;

        int[] textures = new int[1];
        GLES20.glGenTextures(1, textures, 0);
        int textureId = textures[0];

        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, textureId);

        // 设置纹理参数
        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MIN_FILTER, GLES20.GL_LINEAR);
        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MAG_FILTER, GLES20.GL_LINEAR);
        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_S, GLES20.GL_CLAMP_TO_EDGE);
        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_T, GLES20.GL_CLAMP_TO_EDGE);

        // 加载位图到纹理
        android.opengl.GLUtils.texImage2D(GLES20.GL_TEXTURE_2D, 0, bitmap, 0);

        return textureId;
    }

    /**
     * 添加卡片到球体表面
     */
    public void addCard(String name, Bitmap texture) {
        CardData card = new CardData(name);
        cards.add(card);
        cardTextures.add(texture);

        // 计算卡片在球体上的位置（斐波那契球体分布）
        int totalCards = cards.size();
        int index = totalCards - 1; // 当前卡片的索引
        float phi = (float) Math.acos(1 - 2.0 * (index + 0.5) / totalCards);
        float theta = (float) (Math.PI * (1 + Math.sqrt(5)) * (index + 0.5));

        float x = (float) (Math.sin(phi) * Math.cos(theta));
        float y = (float) Math.cos(phi);
        float z = (float) (Math.sin(phi) * Math.sin(theta));

        card.setPosition(x, y, z);
    }

    /**
     * 清除所有卡片
     */
    public void clearCards() {
        cards.clear();
        for (Bitmap bitmap : cardTextures) {
            if (bitmap != null && !bitmap.isRecycled()) {
                bitmap.recycle();
            }
        }
        cardTextures.clear();
    }

    /**
     * 开始旋转
     */
    public void startRotation() {
        isRotating = true;
    }

    /**
     * 停止旋转
     */
    public void stopRotation() {
        isRotating = false;
    }

    /**
     * 设置旋转速度
     */
    public void setRotationSpeed(float speed) {
        this.rotationSpeed = speed;
    }

    /**
     * 选择随机卡片
     */
    public int selectRandomCard() {
        if (cards.isEmpty()) return -1;
        selectedIndex = (int) (Math.random() * cards.size());
        return selectedIndex;
    }

    /**
     * 卡片数据类
     */
    private static class CardData {
        private String name;
        private float x, y, z;

        private FloatBuffer vertexBuffer;
        private FloatBuffer texCoordBuffer;

        public CardData(String name) {
            this.name = name;
            initBuffers();
        }

        private void initBuffers() {
            // 矩形顶点（围绕法线方向）
            float[] vertices = {
                -0.1f, -0.15f, 0.0f,
                 0.1f, -0.15f, 0.0f,
                -0.1f,  0.15f, 0.0f,
                -0.1f,  0.15f, 0.0f,
                 0.1f, -0.15f, 0.0f,
                 0.1f,  0.15f, 0.0f
            };

            // 纹理坐标
            float[] texCoords = {
                0.0f, 1.0f,
                1.0f, 1.0f,
                0.0f, 0.0f,
                0.0f, 0.0f,
                1.0f, 1.0f,
                1.0f, 0.0f
            };

            vertexBuffer = ByteBuffer.allocateDirect(vertices.length * 4)
                .order(ByteOrder.nativeOrder())
                .asFloatBuffer();
            vertexBuffer.put(vertices).position(0);

            texCoordBuffer = ByteBuffer.allocateDirect(texCoords.length * 4)
                .order(ByteOrder.nativeOrder())
                .asFloatBuffer();
            texCoordBuffer.put(texCoords).position(0);
        }

        public void setPosition(float x, float y, float z) {
            this.x = x;
            this.y = y;
            this.z = z;
        }

        public FloatBuffer getVertexBuffer() {
            return vertexBuffer;
        }

        public FloatBuffer getTexCoordBuffer() {
            return texCoordBuffer;
        }

        public String getName() {
            return name;
        }
    }
}
