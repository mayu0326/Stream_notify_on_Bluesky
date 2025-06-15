# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

from version_info import __version__
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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


# --- シングルトン用キャッシュ ---
_configure_logging_cache = {}
_discord_status_logged = False  # Discord通知状態メッセージの重複防止用グローバル


def configure_logging(app=None):
    # シングルトン: 既に初期化済みならキャッシュを返す
    global _configure_logging_cache
    if not app and _configure_logging_cache:
        return (
            _configure_logging_cache["logger"],
            _configure_logging_cache["app_logger_handlers"],
            _configure_logging_cache["audit_logger"],
            _configure_logging_cache["tunnel_logger"],
            _configure_logging_cache["youtube_logger"],
            _configure_logging_cache["niconico_logger"]
        )

    # 環境設定ファイルの場所を指定し、環境変数を読み込む
    env_path = Path(__file__).parent / "settings.env"
    load_dotenv(dotenv_path=env_path)

    # logsディレクトリがなければ作成
    os.makedirs("logs", exist_ok=True)

    # ログレベルや保管日数の設定
    LOG_LEVEL_CONSOLE = os.getenv("LOG_LEVEL_CONSOLE", "INFO").upper()
    LOG_LEVEL_FILE = os.getenv("LOG_LEVEL_FILE", "DEBUG").upper()
    LEVEL_MAP = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level_console = LEVEL_MAP.get(LOG_LEVEL_CONSOLE, logging.INFO)
    log_level_file = LEVEL_MAP.get(LOG_LEVEL_FILE, logging.DEBUG)

    # Discord通知のログレベル設定
    DISCORD_NOTIFY_LEVEL = os.getenv(
        "discord_notify_level", "CRITICAL").upper()
    discord_level = LEVEL_MAP.get(DISCORD_NOTIFY_LEVEL, logging.CRITICAL)

    # ログの保管日数を取得（デフォルト14日、異常値は14日にフォールバック）
    try:
        log_retention_days_str = os.getenv("LOG_RETENTION_DAYS", "14")
        log_retention_days = int(log_retention_days_str)
        if log_retention_days <= 0:
            print(
                f"Warning: LOG_RETENTION_DAYS value '{log_retention_days_str}' is not positive. Defaulting to 14 days.")
            log_retention_days = 14
    except ValueError:
        print(
            f"Warning: Invalid LOG_RETENTION_DAYS value '{
                os.getenv('LOG_RETENTION_DAYS')}'. Defaulting to 14 days.")
        log_retention_days = 14

    # 監査ログ専用ロガーとハンドラの設定
    audit_logger = logging.getLogger("AuditLogger")
    # 監査ログはINFOレベル以上のみ記録
    audit_logger.setLevel(logging.INFO)
    audit_format = logging.Formatter("%(asctime)s [AUDIT] %(message)s")
    audit_file_handler = TimedRotatingFileHandler(
        "logs/audit.log",
        when="D",
        interval=1,
        backupCount=log_retention_days,
        encoding="utf-8",
    )
    audit_file_handler.setLevel(logging.INFO)
    audit_file_handler.setFormatter(audit_format)
    audit_logger.addHandler(audit_file_handler)

    # アプリケーション用ロガーの作成
    logger = logging.getLogger("AppLogger")
    logger.setLevel(min(log_level_console, log_level_file))  # どちらか低い方でロガー自体のレベルを設定
    logger.propagate = False  # ルートロガーへの伝播を防止

    # 既存ハンドラの型を記録
    existing_handler_types = {type(h) for h in logger.handlers}

    # エラーログとコンソールハンドラの設定
    error_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # 一般ログファイル（app.log）のハンドラ
    if TimedRotatingFileHandler not in existing_handler_types:
        info_file_handler = TimedRotatingFileHandler(
            "logs/app.log",  # アプリケーション全体のログ
            when="D",
            interval=1,
            backupCount=log_retention_days,
            encoding="utf-8",
        )
        info_file_handler.setLevel(log_level_file)  # ファイル用ログレベル
        info_file_handler.setFormatter(error_format)
        logger.addHandler(info_file_handler)
    else:
        # 既存の同型ハンドラを再利用
        info_file_handler = next((h for h in logger.handlers if isinstance(h, TimedRotatingFileHandler)), None)

    # エラーログファイル（error.log）のハンドラ
    if TimedRotatingFileHandler not in existing_handler_types:
        error_file_handler = TimedRotatingFileHandler(
            "logs/error.log",  # エラー専用ログファイル
            when="D",
            interval=1,
            backupCount=log_retention_days,
            encoding="utf-8",
        )
        error_file_handler.setLevel(logging.ERROR)  # ERROR以上のみ記録
        error_file_handler.setFormatter(error_format)
        logger.addHandler(error_file_handler)  # AppLoggerに追加
    else:
        error_file_handler = next((h for h in logger.handlers if isinstance(h, TimedRotatingFileHandler)), None)

    # コンソール出力用ハンドラ
    if logging.StreamHandler not in existing_handler_types:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level_console)  # コンソール用ログレベル
        console_handler.setFormatter(error_format)
        logger.addHandler(console_handler)
    else:
        console_handler = next((h for h in logger.handlers if isinstance(h, logging.StreamHandler)), None)

    # Discord通知の有効/無効設定
    discord_enabled = os.getenv("DISCORD_NOTIFICATION_ENABLED", "false").lower() == "true"

    # Discord通知用Webhookの設定
    discord_webhook_url = os.getenv("discord_error_notifier_url")
    app_logger_handlers = [info_file_handler,
                           error_file_handler, console_handler]  # Flask用にも使うハンドラリスト

    if discord_enabled and discord_webhook_url and discord_webhook_url.startswith(
            "https://discord.com/api/webhooks/"):
        try:
            from discord_logging.handler import DiscordHandler
            discord_handler = DiscordHandler(
                "StreamApp_ErrorNotifier", discord_webhook_url)
            # 設定されたDiscord通知レベルを使用
            discord_handler.setLevel(discord_level)
            discord_handler.setFormatter(
                # ログフォーマットを統一
                logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            )
            logger.addHandler(discord_handler)
            app_logger_handlers.append(
                discord_handler)  # Flask用リストにも追加
        except ImportError:
            msg = "discord_loggingライブラリが見つかりません。Discord通知は無効化されます。'pip install discord-logging-handler'でインストールしてください。"
            logger.warning(msg)
            print(msg)  # ロガーが未初期化の場合も考慮してprint
        except Exception as e:
            msg = f"DiscordHandlerの初期化に失敗しました: {e}。Discord通知は無効化されます。"
            logger.warning(msg)
            print(msg)
    else:
        # ユーザー指定の日本語メッセージで出力
        global _discord_status_logged
        if not discord_webhook_url or not discord_webhook_url.startswith(
                "https://discord.com/api/webhooks/"):
            msg = "Discord通知はオフになっています。"
        elif not discord_enabled:
            msg = "Discord通知はオフになっています。"
        else:
            msg = "Discord通知はオンになっています。"
        # グローバルフラグで最初の1回だけINFOログに出力
        if not _discord_status_logged:
            logger.info(msg)  # 設定上の選択なのでINFOで記録
            _discord_status_logged = True

    # tunnel.log用ロガーの設定
    tunnel_logger = logging.getLogger("tunnel.logger")
    tunnel_logger.setLevel(log_level_file)
    for h in tunnel_logger.handlers:
        h.setLevel(log_level_file)
    tunnel_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    tunnel_file_handler = TimedRotatingFileHandler(
        "logs/tunnel.log",
        when="D",
        interval=1,
        backupCount=log_retention_days,
        encoding="utf-8",
    )
    tunnel_file_handler.setLevel(log_level_file)
    tunnel_file_handler.setFormatter(tunnel_format)
    tunnel_logger.addHandler(tunnel_file_handler)

    # YouTube専用ロガー
    youtube_logger = logging.getLogger("YouTubeLogger")
    youtube_logger.setLevel(log_level_file)
    for h in youtube_logger.handlers:
        h.setLevel(log_level_file)
    if not any(isinstance(h, TimedRotatingFileHandler) and getattr(h, 'baseFilename', '').endswith('youtube.log') for h in youtube_logger.handlers):
        yt_file_handler = FlushTimedRotatingFileHandler(
            "logs/youtube.log",
            when="D",
            interval=1,
            backupCount=log_retention_days,
            encoding="utf-8",
        )
        yt_file_handler.setLevel(log_level_file)
        yt_file_handler.setFormatter(error_format)
        youtube_logger.addHandler(yt_file_handler)

    # Niconico専用ロガー
    niconico_logger = logging.getLogger("NiconicoLogger")
    niconico_logger.setLevel(log_level_file)
    for h in niconico_logger.handlers:
        h.setLevel(log_level_file)
    if not any(isinstance(h, TimedRotatingFileHandler) and getattr(h, 'baseFilename', '').endswith('niconico.log') for h in niconico_logger.handlers):
        nico_file_handler = FlushTimedRotatingFileHandler(
            "logs/niconico.log",
            when="D",
            interval=1,
            backupCount=log_retention_days,
            encoding="utf-8",
        )
        nico_file_handler.setLevel(log_level_file)
        nico_file_handler.setFormatter(error_format)
        niconico_logger.addHandler(nico_file_handler)

    # Flaskアプリが渡された場合は、Flaskのロガーにも同じハンドラを追加
    if app is not None:
        app.logger.handlers.clear()  # Flaskデフォルトハンドラをクリア
        for h in app_logger_handlers:
            app.logger.addHandler(h)
        app.logger.setLevel(log_level_file)
        app.logger.propagate = False

    # --- シングルトンキャッシュに保存 ---
    _configure_logging_cache = {
        "logger": logger,
        "app_logger_handlers": app_logger_handlers,
        "audit_logger": audit_logger,
        "tunnel_logger": tunnel_logger,
        "youtube_logger": youtube_logger,
        "niconico_logger": niconico_logger,
    }
    return logger, app_logger_handlers, audit_logger, tunnel_logger, youtube_logger, niconico_logger

# --- flush付きハンドラ ---
class FlushTimedRotatingFileHandler(TimedRotatingFileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()
