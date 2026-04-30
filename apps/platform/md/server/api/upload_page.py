from fastapi import Request
from fastapi.responses import HTMLResponse

async def upload_page_handler(request: Request):
    session_id = request.query_params.get("session_id", "")
    timestamp = request.query_params.get("timestamp", "")
    style_id = request.query_params.get("style_id", "")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI百变秀 - 上传照片</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; text-align: center; background: #f5f5f5; }}
        h1 {{ color: #2196F3; }}
        .upload-box {{ border: 3px dashed #2196F3; padding: 40px; margin: 20px 0; border-radius: 10px; background: white; }}
        input[type=file] {{ display: none; }}
        .btn {{ background: #2196F3; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        .btn:hover {{ background: #1976D2; }}
        .btn:disabled {{ background: #ccc; cursor: not-allowed; }}
        #preview, #compressedPreview, #resultImage {{ max-width: 300px; max-height: 300px; margin: 10px 0; border-radius: 10px; }}
        #compressedPreview {{ border: 2px solid #4CAF50; }}
        #resultImage {{ border: 2px solid #FF9800; display: none; }}
        #status {{ color: #666; margin: 20px 0; font-size: 14px; padding: 10px; border-radius: 5px; }}
        .success {{ background: #d4edda; color: #155724; }}
        .error {{ background: #f8d7da; color: #721c24; }}
        .loading {{ background: #fff3cd; color: #856404; }}
        .info {{ background: #e7f3ff; color: #004085; font-size: 12px; padding: 8px; margin: 5px 0; border-radius: 4px; }}
        .arrow {{ color: #4CAF50; font-size: 24px; margin: 5px 0; }}
        #uploadSection {{ display: block; }}
        #resultSection {{ display: none; }}
        .spinner {{ border: 4px solid #f3f3f3; border-top: 4px solid #2196F3; border-radius: 50%; width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 20px auto; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    </style>
</head>
<body>
    <h1>AI百变秀</h1>
    <p>上传您的照片，立即体验AI换脸</p>

    <div id="uploadSection">
        <div class="upload-box">
            <input type="file" id="fileInput" accept="image/*">
            <p id="hint">点击选择照片</p>
            <button class="btn" id="selectBtn" onclick="document.getElementById('fileInput').click()">选择照片</button>
        </div>

        <div id="originalInfo" class="info" style="display:none;"></div>
        <img id="preview" src="" alt="原图预览" style="display:none;">
        <div class="arrow" style="display:none;" id="arrow">v</div>
        <div id="compressedInfo" class="info" style="display:none;"></div>
        <img id="compressedPreview" src="" alt="压缩后预览" style="display:none;">
        <div id="status"></div>
        <button class="btn" id="uploadBtn" style="display:none" onclick="uploadCompressedFile()">上传照片</button>
    </div>

    <div id="resultSection" style="display:none;">
        <div id="generatingStatus" class="loading" style="padding: 20px; border-radius: 10px;">
            <div class="spinner"></div>
            <p>AI正在生成图片，请稍候...</p>
        </div>
        <img id="resultImage" src="" alt="生成结果">
        <div id="resultActions" style="display:none; margin-top: 20px;">
            <button class="btn" onclick="location.reload()">重新开始</button>
        </div>
    </div>

    <script>
        let originalFile = null;
        let compressedBlob = null;
        const session_id = "{session_id}";
        const style_id = "{style_id}";
        const MAX_WIDTH = 800;
        const MAX_HEIGHT = 800;
        const MAX_SIZE = 500 * 1024;
        const QUALITY = 0.7;
        const POLL_INTERVAL = 3000;  // 轮询间隔3秒
        const MAX_POLL_TIME = 120000;  // 最多轮询2分钟

        function formatSize(bytes) {{
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
            return Math.round(bytes / 1024 / 1024) + ' MB';
        }}

        function compressImage(file, callback) {{
            const reader = new FileReader();
            reader.onload = function(e) {{
                const img = new Image();
                img.onload = function() {{
                    let width = img.width;
                    let height = img.height;
                    if (width > MAX_WIDTH || height > MAX_HEIGHT) {{
                        const ratio = Math.min(MAX_WIDTH / width, MAX_HEIGHT / height);
                        width = Math.round(width * ratio);
                        height = Math.round(height * ratio);
                    }}
                    const canvas = document.createElement('canvas');
                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);
                    canvas.toBlob(function(blob) {{
                        callback(blob, {{
                            originalWidth: img.width,
                            originalHeight: img.height,
                            compressedWidth: width,
                            compressedHeight: height,
                            originalSize: file.size,
                            compressedSize: blob ? blob.size : 0
                        }});
                    }}, 'image/jpeg', QUALITY);
                }};
                img.src = e.target.result;
            }};
            reader.readAsDataURL(file);
        }}

        document.getElementById('fileInput').addEventListener('change', function(e) {{
            originalFile = e.target.files[0];
            if (originalFile) {{
                document.getElementById('hint').textContent = '正在处理图片...';
                const originalInfo = document.getElementById('originalInfo');
                originalInfo.style.display = 'block';
                originalInfo.innerHTML = '<b>原图:</b> ' + formatSize(originalFile.size);
                const preview = document.getElementById('preview');
                preview.src = URL.createObjectURL(originalFile);
                preview.style.display = 'block';
                compressImage(originalFile, function(blob, info) {{
                    compressedBlob = blob;
                    document.getElementById('arrow').style.display = 'block';
                    const compressedInfo = document.getElementById('compressedInfo');
                    compressedInfo.style.display = 'block';
                    const reduction = Math.round((1 - info.compressedSize / info.originalSize) * 100);
                    compressedInfo.innerHTML = '<b>压缩后:</b> ' + formatSize(info.compressedSize) + ' (缩小' + reduction + '%) ' + info.compressedWidth + 'x' + info.compressedHeight;
                    const compressedPreview = document.getElementById('compressedPreview');
                    compressedPreview.src = URL.createObjectURL(blob);
                    compressedPreview.style.display = 'block';
                    document.getElementById('hint').textContent = originalFile.name;
                    // 自动上传，不需要点击按钮
                    uploadCompressedFile();
                }});
            }}
        }});

        async function uploadCompressedFile() {{
            if (!compressedBlob) {{
                alert('请先选择照片');
                return;
            }}
            const statusDiv = document.getElementById('status');
            const uploadBtn = document.getElementById('uploadBtn');
            const selectBtn = document.getElementById('selectBtn');
            statusDiv.className = 'loading';
            statusDiv.textContent = '正在上传...';
            uploadBtn.disabled = true;
            selectBtn.disabled = true;
            const formData = new FormData();
            const fileName = originalFile.name.replace(/\\.[^.]+$/, '.jpg');
            formData.append('file', compressedBlob, fileName);
            formData.append('module', 'style');
            formData.append('source', 'camera');
            formData.append('style_id', style_id);
            formData.append('session_id', session_id);
            try {{
                const response = await fetch('https://www.sillymd.com/application/upload/api', {{ method: 'POST', body: formData }});
                const result = await response.json();
                if (result.code === 200) {{
                    statusDiv.className = 'success';
                    statusDiv.innerHTML = '<b>上传成功！</b><br>AI正在生成图片，请稍候...';
                    document.getElementById('uploadBtn').style.display = 'none';
                    // 开始轮询生成结果
                    startPollingGeneration();
                }} else {{
                    statusDiv.className = 'error';
                    statusDiv.innerHTML = '<b>上传失败:</b> ' + (result.message || '未知错误');
                    uploadBtn.disabled = false;
                    selectBtn.disabled = false;
                }}
            }} catch (error) {{
                statusDiv.className = 'error';
                statusDiv.innerHTML = '<b>上传失败:</b> ' + error.message;
                uploadBtn.disabled = false;
                selectBtn.disabled = false;
            }}
        }}

        let pollStartTime = 0;
        let pollTimer = null;

        function startPollingGeneration() {{
            // 切换到生成等待界面
            document.getElementById('uploadSection').style.display = 'none';
            document.getElementById('resultSection').style.display = 'block';
            pollStartTime = Date.now();
            pollForResult();
        }}

        function pollForResult() {{
            fetch('https://www.sillymd.com/application/generation/query?session_id=' + session_id)
                .then(response => response.json())
                .then(data => {{
                    if (data.code === 200 && data.data && data.data.result_url) {{
                        // 生成成功，显示结果
                        showResult(data.data.result_url);
                    }} else if (data.code === 200 && data.data && data.data.status === 'processing') {{
                        // 还在处理中，继续轮询
                        if (Date.now() - pollStartTime < MAX_POLL_TIME) {{
                            pollTimer = setTimeout(pollForResult, POLL_INTERVAL);
                        }} else {{
                            showError('生成超时，请稍后重试');
                        }}
                    }} else {{
                        // 暂无结果，继续轮询
                        if (Date.now() - pollStartTime < MAX_POLL_TIME) {{
                            pollTimer = setTimeout(pollForResult, POLL_INTERVAL);
                        }} else {{
                            showError('生成超时，请稍后重试');
                        }}
                    }}
                }})
                .catch(error => {{
                    console.error('轮询错误:', error);
                    if (Date.now() - pollStartTime < MAX_POLL_TIME) {{
                        pollTimer = setTimeout(pollForResult, POLL_INTERVAL);
                    }} else {{
                        showError('查询失败，请稍后重试');
                    }}
                }});
        }}

        function showResult(url) {{
            document.getElementById('generatingStatus').style.display = 'none';
            const resultImage = document.getElementById('resultImage');
            resultImage.src = url;
            resultImage.style.display = 'block';
            document.getElementById('resultActions').style.display = 'block';
        }}

        function showError(message) {{
            document.getElementById('generatingStatus').innerHTML = '<p style="color: #721c24;">' + message + '</p>';
            document.getElementById('resultActions').style.display = 'block';
        }}
    </script>
</body>
</html>"""

    html = html.replace("{session_id}", session_id)
    html = html.replace("{style_id}", style_id)

    return HTMLResponse(content=html)
