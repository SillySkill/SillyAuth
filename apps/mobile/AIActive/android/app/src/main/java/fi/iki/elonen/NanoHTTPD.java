package fi.iki.elonen;

import java.io.IOException;
import java.util.Map;

/**
 * NanoHTTPD存根类
 */
public class NanoHTTPD {
    // Socket读取超时常量
    public static final int SOCKET_READ_TIMEOUT = 5000; // 5秒超时

    public NanoHTTPD(int port) {
        // 存根实现
    }

    /**
     * 处理HTTP请求（子类应重写此方法）
     */
    public Response serve(IHTTPSession session) {
        return null;
    }

    public void start() throws IOException {
        // 存根实现
    }

    public void start(int timeout, boolean daemon) throws IOException {
        // 存根实现 - 带超时参数的启动
    }

    public void stop() {
        // 存根实现
    }

    public enum Method {
        GET, PUT, POST, DELETE, HEAD, OPTIONS
    }

    public static class Response {
        public static enum Status {
            OK(200), BAD_REQUEST(400), NOT_FOUND(404), INTERNAL_ERROR(500);

            private int code;

            Status(int code) {
                this.code = code;
            }

            public int getRequestStatus() {
                return code;
            }
        }

        private Status status;
        private Map<String, String> headers;

        public Response(Status status) {
            this.status = status;
        }

        public Status getStatus() {
            return status;
        }

        /**
         * 添加响应头
         */
        public Response addHeader(String name, String value) {
            if (headers == null) {
                headers = new java.util.HashMap<>();
            }
            headers.put(name, value);
            return this;
        }

        /**
         * 获取所有响应头
         */
        public Map<String, String> getHeaders() {
            return headers;
        }
    }

    public static class IHTTPSession {
        private String uri;
        private Method method;
        private Map<String, String> headers;
        private Map<String, String> params;

        public String getUri() {
            return uri;
        }

        public Method getMethod() {
            return method;
        }

        /**
         * 解析请求体
         */
        public void parseBody(Map<String, String> files) {
            // 存根实现 - 解析请求体数据
        }

        public Map<String, String> getHeaders() {
            return headers;
        }

        public Map<String, String> getParams() {
            return params;
        }
    }

    protected Response newFixedLengthResponse(Response.Status status, String mimeType, String message) {
        return new Response(status);
    }

    protected Response addCorsHeaders(Response response) {
        return response;
    }
}
