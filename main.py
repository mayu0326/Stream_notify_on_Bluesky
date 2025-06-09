# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

# Stream notify on Bluesky
# Copyright (C) 2025 mayuneco(mayunya)
#
# このプログラムはフリーソフトウェアです。フリーソフトウェア財団によって発行された
# GNU 一般公衆利用許諾契約書（バージョン2またはそれ以降）に基づき、再配布または
# 改変することができます。
#
# このプログラムは有用であることを願って配布されていますが、
# 商品性や特定目的への適合性についての保証はありません。
# 詳細はGNU一般公衆利用許諾契約書をご覧ください。
#
# このプログラムとともにGNU一般公衆利用許諾契約書が配布されているはずです。
# もし同梱されていない場合は、フリーソフトウェア財団までご請求ください。
# 住所: 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from app_initializer import initialize_app
from tunnel_manager import stop_tunnel_and_monitor
from webhook_routes import webhook_bp, handle_404
from cleanup import cleanup_application, signal_handler
from cleanup import cleanup_from_gui as _cleanup_from_gui
from flask import Flask
import atexit
import signal
import sys
import os

app = Flask(__name__, static_folder="static")
app.register_blueprint(webhook_bp)
app.register_error_handler(404, handle_404)

def start_server_in_thread():
    from threading import Thread
    from tunnel_manager import run_cherrypy_server
    server_thread = Thread(target=run_cherrypy_server, daemon=True)
    server_thread.start()
    return server_thread

def stop_cherrypy_server():
    import cherrypy
    cherrypy.engine.exit()

def cleanup_from_gui():
    _cleanup_from_gui()

def is_server_running():
    import cherrypy
    return cherrypy.engine.state == cherrypy.engine.states.STARTED

SETTINGS_ENV_PATH = "settings.env"

if not os.path.exists(SETTINGS_ENV_PATH):
    print("[ERROR] 設定ファイルが見つかりません。'settings.env' を作成してください。")
    sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    if sys.platform.startswith('win'):
        signal.signal(signal.SIGBREAK, signal_handler)
    atexit.register(cleanup_application)
    if initialize_app(app, None):
        from threading import Thread
        from tunnel_manager import run_cherrypy_server
        server_thread = Thread(target=run_cherrypy_server, daemon=True)
        server_thread.start()
        try:
            while server_thread.is_alive():
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
        cleanup_application()
    else:
        sys.exit(1)
