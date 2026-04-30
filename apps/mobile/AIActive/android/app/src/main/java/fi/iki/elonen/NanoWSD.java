package fi.iki.elonen;

import java.net.Socket;
import java.util.Map;

/**
 * NanoWSD存根类
 * WebSocket服务器存根实现
 */
public abstract class NanoWSD extends NanoHTTPD {
    public NanoWSD(int port) {
        super(port);
    }

    public static class WebSocketFrame {
        private String textPayload;

        public String getTextPayload() {
            return textPayload;
        }

        public void setTextPayload(String textPayload) {
            this.textPayload = textPayload;
        }
    }

    public static class Socket {
        private java.net.Socket socket;

        public Socket(java.net.Socket socket) {
            this.socket = socket;
        }

        public void send(String message) {
            // 存根实现
        }

        public void close() {
            // 存根实现
        }

        public String getRemoteIpAddress() {
            // 存根实现 - 返回本地地址
            return "127.0.0.1";
        }
    }

    // 抽象方法需要子类实现
    protected abstract void onOpen(WebSocketFrame handshake, Socket connection);
    protected abstract void onClose(Socket connection, WebSocketFrame frame);
    protected abstract void onMessage(WebSocketFrame message, Socket connection);
    protected abstract void onPong(WebSocketFrame frame, Socket connection);
    protected abstract void onException(Socket connection, Exception e);
}
