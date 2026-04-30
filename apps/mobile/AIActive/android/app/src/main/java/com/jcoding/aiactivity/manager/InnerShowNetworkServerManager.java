package com.jcoding.aiactivity.manager;

import android.content.Context;
import android.util.Log;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.jcoding.aiactivity.manager.InnerShowDataManager.GenerationResult;
import com.jcoding.aiactivity.manager.InnerShowDataManager.LotteryWinner;
import com.jcoding.aiactivity.manager.InnerShowDataManager.QuizWinner;
import com.jcoding.aiactivity.utils.NetworkUtils;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CopyOnWriteArrayList;

import fi.iki.elonen.NanoHTTPD;
import fi.iki.elonen.NanoWSD;
import fi.iki.elonen.NanoWSD.WebSocketFrame;

/**
 * 内场秀网络服务器管理器
 * 实现主服务器架构，提供HTTP API和WebSocket服务
 */
public class InnerShowNetworkServerManager {

    private static final String TAG = "InnerShowNetworkServer";
    private static final int DEFAULT_HTTP_PORT = 8080;
    private static final int DEFAULT_WS_PORT = 8081;

    private static InnerShowNetworkServerManager instance;
    private Context context;
    private InnerShowDataManager dataManager;
    private Gson gson;

    // HTTP服务器
    private InnerShowHTTPServer httpServer;
    private int httpPort = DEFAULT_HTTP_PORT;

    // WebSocket服务器
    private InnerShowWebSocketServer wsServer;
    private int wsPort = DEFAULT_WS_PORT;

    // WebSocket连接列表
    private List<NanoWSD.Socket> webSocketConnections = new CopyOnWriteArrayList<>();

    private boolean isRunning = false;

    private InnerShowNetworkServerManager(Context context) {
        this.context = context.getApplicationContext();
        this.dataManager = InnerShowDataManager.getInstance(context);
        this.gson = new Gson();
    }

    public static synchronized InnerShowNetworkServerManager getInstance(Context context) {
        if (instance == null) {
            instance = new InnerShowNetworkServerManager(context);
        }
        return instance;
    }

    /**
     * 启动服务器
     */
    public boolean startServer() {
        return startServer(DEFAULT_HTTP_PORT, DEFAULT_WS_PORT);
    }

    /**
     * 启动服务器（指定端口）
     */
    public boolean startServer(int httpPort, int wsPort) {
        if (isRunning) {
            Log.w(TAG, "服务器已在运行");
            return true;
        }

        this.httpPort = httpPort;
        this.wsPort = wsPort;

        try {
            // 启动HTTP服务器
            httpServer = new InnerShowHTTPServer(httpPort);
            httpServer.start(NanoHTTPD.SOCKET_READ_TIMEOUT, false);
            Log.i(TAG, "HTTP服务器已启动，端口: " + httpPort);

            // 启动WebSocket服务器
            wsServer = new InnerShowWebSocketServer(wsPort);
            wsServer.start();
            Log.i(TAG, "WebSocket服务器已启动，端口: " + wsPort);

            isRunning = true;
            return true;

        } catch (IOException e) {
            Log.e(TAG, "启动服务器失败", e);
            stopServer();
            return false;
        }
    }

    /**
     * 停止服务器
     */
    public void stopServer() {
        if (httpServer != null) {
            httpServer.stop();
            httpServer = null;
        }

        if (wsServer != null) {
            wsServer.stop();
            wsServer = null;
        }

        webSocketConnections.clear();
        isRunning = false;

        Log.i(TAG, "服务器已停止");
    }

    /**
     * 检查服务器是否运行
     */
    public boolean isRunning() {
        return isRunning;
    }

    /**
     * 获取HTTP端口
     */
    public int getHttpPort() {
        return httpPort;
    }

    /**
     * 获取WebSocket端口
     */
    public int getWsPort() {
        return wsPort;
    }

    /**
     * 获取本机IP地址
     */
    public String getServerUrl() {
        return "http://" + NetworkUtils.getLocalIpAddress() + ":" + httpPort;
    }

    /**
     * 获取WebSocket地址
     */
    public String getWebSocketUrl() {
        return "ws://" + NetworkUtils.getLocalIpAddress() + ":" + wsPort;
    }

    /**
     * 广播消息到所有WebSocket客户端
     */
    public void broadcastWebSocketMessage(String message) {
        if (wsServer != null) {
            wsServer.broadcast(message);
        }
    }

    /**
     * 广播新生成图片事件
     */
    public void broadcastNewImage(String resultId) {
        JsonObject data = new JsonObject();
        data.addProperty("type", "new_image");
        data.addProperty("result_id", resultId);
        broadcastWebSocketMessage(gson.toJson(data));
    }

    /**
     * 广播新中奖人事件
     */
    public void broadcastNewLotteryWinner(String winnerId) {
        JsonObject data = new JsonObject();
        data.addProperty("type", "new_lottery_winner");
        data.addProperty("winner_id", winnerId);
        broadcastWebSocketMessage(gson.toJson(data));
    }

    /**
     * 广播新答题中奖事件
     */
    public void broadcastNewQuizWinner(String quizWinnerId) {
        JsonObject data = new JsonObject();
        data.addProperty("type", "new_quiz_winner");
        data.addProperty("quiz_winner_id", quizWinnerId);
        broadcastWebSocketMessage(gson.toJson(data));
    }

    /**
     * 广播刷新事件
     */
    public void broadcastRefresh() {
        JsonObject data = new JsonObject();
        data.addProperty("type", "refresh");
        broadcastWebSocketMessage(gson.toJson(data));
    }

    // ==================== HTTP服务器实现 ====================

    /**
     * 内场秀HTTP服务器
     */
    private class InnerShowHTTPServer extends NanoHTTPD implements com.jcoding.aiactivity.manager.InnerShowHTTPServer {

        public InnerShowHTTPServer(int port) {
            super(port);
        }

        @Override
        public Response serve(IHTTPSession session) {
            String uri = session.getUri();
            Method method = session.getMethod();

            Log.d(TAG, "HTTP请求: " + method + " " + uri);

            // CORS预检请求
            if (method == Method.OPTIONS) {
                return addCorsHeaders(newFixedLengthResponse(Response.Status.OK, "text/plain", ""));
            }

            // API路由
            if (uri.startsWith("/api/")) {
                return handleApiRequest(session);
            }

            // 健康检查
            if (uri.equals("/health")) {
                return addCorsHeaders(newFixedLengthResponse(Response.Status.OK,
                    "application/json", "{\"status\":\"ok\",\"service\":\"inner_show_server\"}"));
            }

            // 404
            return addCorsHeaders(newFixedLengthResponse(Response.Status.NOT_FOUND,
                "application/json", "{\"error\":\"Not Found\"}"));
        }

        /**
         * 处理API请求
         */
        private Response handleApiRequest(IHTTPSession session) {
            String uri = session.getUri();
            Method method = session.getMethod();

            try {
                // GET /api/generations - 获取所有生成结果
                if (uri.equals("/api/generations") && method == Method.GET) {
                    return getGenerations();
                }

                // POST /api/generations - 添加生成结果
                if (uri.equals("/api/generations") && method == Method.POST) {
                    return addGeneration(session);
                }

                // GET /api/lottery-winners - 获取中奖记录
                if (uri.equals("/api/lottery-winners") && method == Method.GET) {
                    return getLotteryWinners();
                }

                // POST /api/lottery-winners - 添加中奖记录
                if (uri.equals("/api/lottery-winners") && method == Method.POST) {
                    return addLotteryWinner(session);
                }

                // GET /api/quiz-winners - 获取答题中奖记录
                if (uri.equals("/api/quiz-winners") && method == Method.GET) {
                    return getQuizWinners();
                }

                // POST /api/quiz-winners - 添加答题中奖记录
                if (uri.equals("/api/quiz-winners") && method == Method.POST) {
                    return addQuizWinner(session);
                }

                // GET /api/current-display - 获取当前显示内容
                if (uri.equals("/api/current-display") && method == Method.GET) {
                    return getCurrentDisplay();
                }

                // POST /api/current-display - 设置当前显示内容
                if (uri.equals("/api/current-display") && method == Method.POST) {
                    return setCurrentDisplay(session);
                }

                // GET /api/data - 获取所有数据
                if (uri.equals("/api/data") && method == Method.GET) {
                    return getAllData();
                }

                // POST /api/broadcast - 广播消息
                if (uri.equals("/api/broadcast") && method == Method.POST) {
                    return broadcastMessage(session);
                }

                return addCorsHeaders(newFixedLengthResponse(Response.Status.NOT_FOUND,
                    "application/json", "{\"error\":\"API endpoint not found\"}"));

            } catch (Exception e) {
                Log.e(TAG, "处理API请求失败", e);
                return addCorsHeaders(newFixedLengthResponse(Response.Status.INTERNAL_ERROR,
                    "application/json", "{\"error\":\"Internal server error\"}"));
            }
        }

        /**
         * 获取所有生成结果
         */
        private Response getGenerations() {
            List<GenerationResult> results = dataManager.getGenerationResults();
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", results);
            return addCorsHeaders(newFixedLengthResponse(Response.Status.OK,
                "application/json", gson.toJson(response)));
        }

        /**
         * 添加生成结果
         */
        private Response addGeneration(IHTTPSession session) {
            try {
                String body = readRequestBody(session);
                GenerationResult result = gson.fromJson(body, GenerationResult.class);

                // 添加到数据管理器
                dataManager.addGenerationResult(result);

                // 广播通知
                broadcastNewImage(result.id);

                Map<String, Object> response = new HashMap<>();
                response.put("success", true);
                response.put("message", "添加成功");
                response.put("id", result.id);

                return addCorsHeaders(newFixedLengthResponse(Response.Status.OK,
                    "application/json", gson.toJson(response)));

            } catch (Exception e) {
                Log.e(TAG, "添加生成结果失败", e);
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("error", e.getMessage());
                return addCorsHeaders(newFixedLengthResponse(Response.Status.BAD_REQUEST,
                    "application/json", gson.toJson(response)));
            }
        }

        /**
         * 获取中奖记录
         */
        private Response getLotteryWinners() {
            List<LotteryWinner> winners = dataManager.getLotteryWinners();
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", winners);
            return addCorsHeaders(newFixedLengthResponse(Response.Status.OK,
                "application/json", gson.toJson(response)));
        }

        /**
         * 添加中奖记录
         */
        private Response addLotteryWinner(IHTTPSession session) {
            try {
                String body = readRequestBody(session);
                LotteryWinner winner = gson.fromJson(body, LotteryWinner.class);

                // 添加到数据管理器
                dataManager.addLotteryWinner(winner);

                // 广播通知
                broadcastNewLotteryWinner(winner.id);

                Map<String, Object> response = new HashMap<>();
                response.put("success", true);
                response.put("message", "添加成功");
                response.put("id", winner.id);

                return addCorsHeaders(newFixedLengthResponse(Response.Status.OK,
                    "application/json", gson.toJson(response)));

            } catch (Exception e) {
                Log.e(TAG, "添加中奖记录失败", e);
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("error", e.getMessage());
                return addCorsHeaders(newFixedLengthResponse(Response.Status.BAD_REQUEST,
                    "application/json", gson.toJson(response)));
            }
        }

        /**
         * 获取答题中奖记录
         */
        private Response getQuizWinners() {
            List<QuizWinner> winners = dataManager.getQuizWinners();
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", winners);
            return addCorsHeaders(newFixedLengthResponse(Response.Status.OK,
                "application/json", gson.toJson(response)));
        }

        /**
         * 添加答题中奖记录
         */
        private Response addQuizWinner(IHTTPSession session) {
            try {
                String body = readRequestBody(session);
                QuizWinner winner = gson.fromJson(body, QuizWinner.class);

                // 添加到数据管理器
                dataManager.addQuizWinner(winner);

                // 广播通知
                broadcastNewQuizWinner(winner.id);

                Map<String, Object> response = new HashMap<>();
                response.put("success", true);
                response.put("message", "添加成功");
                response.put("id", winner.id);

                return addCorsHeaders(newFixedLengthResponse(Response.Status.OK,
                    "application/json", gson.toJson(response)));

            } catch (Exception e) {
                Log.e(TAG, "添加答题中奖记录失败", e);
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("error", e.getMessage());
                return addCorsHeaders(newFixedLengthResponse(Response.Status.BAD_REQUEST,
                    "application/json", gson.toJson(response)));
            }
        }

        /**
         * 获取当前显示内容
         */
        private Response getCurrentDisplay() {
            String currentDisplayId = dataManager.getCurrentDisplayImageId();
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("current_display_id", currentDisplayId);
            return addCorsHeaders(newFixedLengthResponse(Response.Status.OK,
                "application/json", gson.toJson(response)));
        }

        /**
         * 设置当前显示内容
         */
        private Response setCurrentDisplay(IHTTPSession session) {
            try {
                String body = readRequestBody(session);
                JsonObject json = JsonParser.parseString(body).getAsJsonObject();
                String displayId = json.get("display_id").getAsString();

                dataManager.setCurrentDisplayImage(displayId);

                // 广播刷新通知
                broadcastRefresh();

                Map<String, Object> response = new HashMap<>();
                response.put("success", true);
                response.put("message", "设置成功");

                return addCorsHeaders(newFixedLengthResponse(Response.Status.OK,
                    "application/json", gson.toJson(response)));

            } catch (Exception e) {
                Log.e(TAG, "设置当前显示内容失败", e);
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("error", e.getMessage());
                return addCorsHeaders(newFixedLengthResponse(Response.Status.BAD_REQUEST,
                    "application/json", gson.toJson(response)));
            }
        }

        /**
         * 获取所有数据
         */
        private Response getAllData() {
            Map<String, Object> allData = new HashMap<>();
            allData.put("generations", dataManager.getGenerationResults());
            allData.put("lottery_winners", dataManager.getLotteryWinners());
            allData.put("quiz_winners", dataManager.getQuizWinners());
            allData.put("check_in_records", dataManager.getCheckInRecords());
            allData.put("current_display_id", dataManager.getCurrentDisplayImageId());

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", allData);

            return addCorsHeaders(newFixedLengthResponse(Response.Status.OK,
                "application/json", gson.toJson(response)));
        }

        /**
         * 广播消息
         */
        private Response broadcastMessage(IHTTPSession session) {
            try {
                String body = readRequestBody(session);
                JsonObject json = JsonParser.parseString(body).getAsJsonObject();
                String message = json.get("message").getAsString();

                broadcastWebSocketMessage(message);

                Map<String, Object> response = new HashMap<>();
                response.put("success", true);
                response.put("message", "广播成功");

                return addCorsHeaders(newFixedLengthResponse(Response.Status.OK,
                    "application/json", gson.toJson(response)));

            } catch (Exception e) {
                Log.e(TAG, "广播消息失败", e);
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("error", e.getMessage());
                return addCorsHeaders(newFixedLengthResponse(Response.Status.BAD_REQUEST,
                    "application/json", gson.toJson(response)));
            }
        }

        /**
         * 读取请求体
         */
        private String readRequestBody(IHTTPSession session) {
            try {
                Map<String, String> files = new HashMap<>();
                session.parseBody(files);
                return files.get("postData");
            } catch (Exception e) {
                Log.e(TAG, "读取请求体失败", e);
                return "";
            }
        }

        /**
         * 添加CORS头
         */
        @Override
        protected Response addCorsHeaders(Response response) {
            response = super.addCorsHeaders(response);
            response.addHeader("Access-Control-Allow-Origin", "*");
            response.addHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
            response.addHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
            response.addHeader("Access-Control-Max-Age", "86400");
            return response;
        }
    }

    // ==================== WebSocket服务器实现 ====================

    /**
     * 内场秀WebSocket服务器
     */
    private class InnerShowWebSocketServer extends NanoWSD {

        public InnerShowWebSocketServer(int port) {
            super(port);
        }

        @Override
        protected void onOpen(NanoWSD.WebSocketFrame handshake, NanoWSD.Socket connection) {
            Log.d(TAG, "WebSocket连接打开: " + connection.getRemoteIpAddress());
            webSocketConnections.add(connection);

            // 发送欢迎消息
            try {
                connection.send(gson.toJson(new WelcomeMessage()));
            } catch (Exception e) {
                Log.e(TAG, "发送欢迎消息失败", e);
            }
        }

        @Override
        protected void onClose(NanoWSD.Socket connection, NanoWSD.WebSocketFrame frame) {
            Log.d(TAG, "WebSocket连接关闭: " + connection.getRemoteIpAddress());
            webSocketConnections.remove(connection);
        }

        @Override
        protected void onMessage(NanoWSD.WebSocketFrame message, NanoWSD.Socket connection) {
            Log.d(TAG, "收到WebSocket消息: " + message.getTextPayload());
            // 可以处理客户端发送的消息
        }

        @Override
        protected void onPong(NanoWSD.WebSocketFrame frame, NanoWSD.Socket connection) {
            // 处理pong
        }

        @Override
        protected void onException(NanoWSD.Socket connection, Exception e) {
            Log.e(TAG, "WebSocket异常", e);
            webSocketConnections.remove(connection);
        }

        /**
         * 广播消息到所有连接
         */
        public void broadcast(String message) {
            for (NanoWSD.Socket connection : webSocketConnections) {
                try {
                    connection.send(message);
                } catch (Exception e) {
                    Log.e(TAG, "广播消息失败", e);
                }
            }
            Log.d(TAG, "广播消息到 " + webSocketConnections.size() + " 个客户端");
        }
    }

    /**
     * 欢迎消息
     */
    private static class WelcomeMessage {
        public String type = "welcome";
        public String message = "已连接到内场秀服务器";
        public long timestamp = System.currentTimeMillis();
    }
}
