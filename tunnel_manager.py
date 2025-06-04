import threading
import os

# グローバルでトンネルプロセスを管理
_tunnel_proc = None
_tunnel_proc_lock = threading.Lock()

def start_tunnel_and_monitor(tunnel_logger):
    from tunnel import start_tunnel
    global _tunnel_proc
    with _tunnel_proc_lock:
        _tunnel_proc = start_tunnel(tunnel_logger)
        tunnel_proc = _tunnel_proc
    tunnel_service = os.getenv("TUNNEL_SERVICE", "").lower()
    if tunnel_service in ("ngrok", "localtunnel"):
        def get_proc():
            with _tunnel_proc_lock:
                return _tunnel_proc
        def set_proc(p):
            global _tunnel_proc
            with _tunnel_proc_lock:
                _tunnel_proc = p
        monitor_thread = threading.Thread(
            target=tunnel_monitor_loop,
            args=(
                tunnel_service,
                os.getenv("NGROK_CMD") if tunnel_service == "ngrok" else os.getenv("LOCALTUNNEL_CMD"),
                tunnel_logger,
                get_proc,
                set_proc),
            daemon=True)
        monitor_thread.start()
    return tunnel_proc

def stop_tunnel_and_monitor():
    from tunnel import stop_tunnel
    global _tunnel_proc
    with _tunnel_proc_lock:
        if _tunnel_proc:
            stop_tunnel(_tunnel_proc)
            _tunnel_proc = None

def get_tunnel_proc():
    global _tunnel_proc
    with _tunnel_proc_lock:
        return _tunnel_proc

def tunnel_monitor_loop(
        tunnel_service,
        tunnel_cmd,
        logger,
        proc_getter,
        proc_setter,
        env_path=None):
    import time
    import select
    import re
    from utils import get_ngrok_public_url, set_webhook_callback_url_temporary, get_settings_env_abspath
    if env_path is None:
        env_path = get_settings_env_abspath()
    while True:
        proc = proc_getter()
        if proc is None or proc.poll() is not None:
            logger.warning(f"トンネルプロセス({tunnel_service})が停止しました。自動再起動します。")
            from tunnel import start_tunnel
            new_proc = start_tunnel(logger)
            proc_setter(new_proc)
            time.sleep(2)
            url = None
            if tunnel_service == "ngrok":
                url = get_ngrok_public_url(logger=logger)
            elif tunnel_service == "localtunnel":
                try:
                    if proc is not None and hasattr(proc, "stdout") and proc.stdout:
                        url = None
                        for _ in range(20):
                            ready, _, _ = select.select([proc.stdout], [], [], 0.5)
                            if ready:
                                line = proc.stdout.readline()
                                if not line:
                                    break
                                decoded = line.decode("utf-8", errors="ignore").strip()
                                match = re.search(r"(https://[a-zA-Z0-9\-]+\.loca\.lt)", decoded)
                                if match:
                                    url = match.group(1)
                                    logger.info(f"localtunnel URL検出: {url}")
                                    break
                            else:
                                continue
                except Exception as e:
                    logger.error(f"localtunnelのURL取得中に例外発生: {e}", exc_info=e)
            if url:
                set_webhook_callback_url_temporary(url, env_path=env_path)
                logger.info(f"新しい一時URL({tunnel_service}): {url} をsettings.envに反映しました。")
        time.sleep(5)

def run_cherrypy_server():
    import cherrypy
    from main import app
    cherrypy.tree.graft(app, '/')
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 3000,
        'engine.autoreload.on': False,
    })
    cherrypy.engine.start()
    cherrypy.engine.block()
