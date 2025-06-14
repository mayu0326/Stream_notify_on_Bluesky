# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

from version_info import __version__
import subprocess
import os
import shlex  # コマンドライン引数の安全な分割用
import sys
import logging
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__


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


def start_tunnel(logger=None):
    """
    TUNNEL_SERVICEで選択されたサービスに応じてトンネルプロセスを起動する
    loggerが指定されていればログ出力も行う
    """
    if logger is None:
        logger = logging.getLogger("tunnel.logger")

    tunnel_service = os.getenv("TUNNEL_SERVICE", "").lower()
    tunnel_cmd = None

    # cloudflare系
    if tunnel_service in ("cloudflare", "cloudflare_domain"):
        tunnel_cmd = os.getenv("TUNNEL_CMD")
    elif tunnel_service == "cloudflare_tempurl":
        tunnel_cmd = os.getenv("CLOUDFLARE_TEMP_CMD")
    elif tunnel_service == "ngrok":
        tunnel_cmd = os.getenv("NGROK_CMD")
        # NGROK_CMDが未設定の場合はNGROK_AUTH_TOKEN等から組み立ててもよい
    elif tunnel_service == "localtunnel":
        tunnel_cmd = os.getenv("LOCALTUNNEL_CMD")
    elif tunnel_service == "custom":
        tunnel_cmd = os.getenv("CUSTOM_TUNNEL_CMD")
    else:
        # 未知または未設定の場合は従来通りTUNNEL_CMD
        tunnel_cmd = os.getenv("TUNNEL_CMD")

    if not tunnel_cmd:
        logger.warning("トンネルコマンドが設定されていません。トンネルは起動しません。")
        return None
    try:
        # ログファイルに標準出力・標準エラーをリダイレクト
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        tunnel_log_path = os.path.join(log_dir, 'tunnel.log')
        tunnel_log = open(tunnel_log_path, 'a', encoding='utf-8')
        proc = subprocess.Popen(
            shlex.split(tunnel_cmd),
            stdout=tunnel_log,
            stderr=subprocess.STDOUT
        )
        logger.info(f"トンネルを起動しました: {tunnel_cmd}")
        # 起動直後に即時終了していないかチェック
        import time
        time.sleep(1)
        if proc.poll() is not None:
            logger.error(f"トンネルプロセスが即時終了しました。コマンド: {tunnel_cmd}")
            with open(tunnel_log_path, 'r', encoding='utf-8') as f:
                log_tail = ''.join(f.readlines()[-20:])
            logger.error(f"tunnel.logの直近出力:\n{log_tail}")
            return None
        return proc
    except FileNotFoundError:
        err_msg = f"トンネルコマンド '{tunnel_cmd.split()[0] if tunnel_cmd else ''}' が見つかりません。Pathが通っているか確認してください。"
        logger.error(err_msg)
        return None
    except Exception as e:
        err_msg_generic = f"トンネル起動失敗: {e}"
        logger.error(err_msg_generic)
        return None


def stop_tunnel(proc, logger=None):
    """
    トンネルプロセスを終了させる
    proc: start_tunnelで返されたPopenオブジェクト
    logger: ログ出力用ロガー
    """
    if logger is None:
        logger = logging.getLogger("tunnel.logger")

    if proc:
        try:
            proc.terminate()  # 正常終了を試みる
            proc.wait(timeout=5)  # 最大5秒待機
            logger.info("トンネルを正常に終了しました。")
        except subprocess.TimeoutExpired:
            # 終了がタイムアウトした場合は強制終了
            logger.warning("トンネル終了がタイムアウトしました。強制終了します。")
            proc.kill()  # 強制終了
            logger.info("トンネルを強制終了しました。")
        except Exception as e:
            # terminate()で他の例外が出てもkillを試みる
            logger.error(f"トンネル終了中にエラーが発生しました: {e}")
            try:
                proc.kill()
                logger.info("トンネルを強制終了しました（例外対応）。")
            except Exception as e2:
                logger.error(f"トンネル強制終了にも失敗: {e2}")
    else:
        # プロセスがNoneの場合は何もしない
        logger.info("トンネルプロセスが存在しないため、終了処理はスキップされました。")
