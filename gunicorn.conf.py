# =============================================================================
# Gunicorn Configuration for CloudType.io
# =============================================================================

import multiprocessing
import os

# 서버 설정
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# 워커 설정
workers = min(2, multiprocessing.cpu_count())  # CloudType 무료 플랜에 최적화
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 120
keepalive = 5

# 로깅 설정
accesslog = "-"  # stdout으로 출력
errorlog = "-"   # stderr으로 출력
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 프로세스 설정
user = None
group = None
tmp_upload_dir = None
proc_name = "vans_search_service"

# 보안 설정
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 성능 튜닝
worker_tmp_dir = "/dev/shm"  # 메모리 기반 임시 디렉토리 사용

# 그레이스풀 셧다운
graceful_timeout = 30
max_worker_memory = 200 * 1024 * 1024  # 200MB per worker

def when_ready(server):
    """서버 시작 시 호출되는 콜백"""
    server.log.info("VansDevBlog Search Service is ready to serve requests")

def worker_int(worker):
    """워커 인터럽트 시 호출되는 콜백"""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """워커 포크 전 호출되는 콜백"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """워커 포크 후 호출되는 콜백"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_exec(server):
    """서버 재시작 전 호출되는 콜백"""
    server.log.info("Forked child, re-executing.")

def worker_abort(worker):
    """워커 중단 시 호출되는 콜백"""
    worker.log.info("worker received SIGABRT signal")


