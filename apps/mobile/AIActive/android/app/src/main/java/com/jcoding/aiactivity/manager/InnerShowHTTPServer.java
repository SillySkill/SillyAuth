package com.jcoding.aiactivity.manager;

import fi.iki.elonen.NanoHTTPD;

public interface InnerShowHTTPServer {
    NanoHTTPD.Response serve(NanoHTTPD.IHTTPSession session);
}
