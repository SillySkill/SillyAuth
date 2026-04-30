"""
Gunicorn配置文件
"""
import multiprocessing

# 绑定地址
bind = "127.0.0.1:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作进程类型
worker_class = "sync"

# 超时时间
timeout = 120
keepalive = 5

# 最大请求数（自动重启工作进程）
max_requests = 1000
max_requests_jitter = 50

# 预加载应用
preload_app = True

# 日志配置
accesslog = "/var/log/aiactivity-config/access.log"
errorlog = "/var/log/aiactivity-config/error.log"
loglevel = "info"

# 进程名称
proc_name = "aiactivity-config"

# 守护进程
daemon = False

# PID文件
pidfile = "/var/run/aiactivity-config.pid"
