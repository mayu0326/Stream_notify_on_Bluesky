from tunnel_manager import start_tunnel_and_monitor
from service_monitor import start_youtube_monitor, start_niconico_monitor
from eventsub import setup_broadcaster_id, get_valid_app_access_token, create_eventsub_subscription, cleanup_eventsub_subscriptions
from logging_config import configure_logging
from utils import rotate_secret_if_needed
import os

def initialize_app(app, tunnel_logger):
    # ロギング設定
    logger, app_logger_handlers, audit_logger, tunnel_logger, youtube_logger, niconico_logger = configure_logging(app)
    WEBHOOK_SECRET = rotate_secret_if_needed(logger)
    os.environ["WEBHOOK_SECRET"] = WEBHOOK_SECRET
    # --- サービス有効判定 ---
    twitch_enabled = os.getenv("NOTIFY_ON_TWITCH_ONLINE", "False").lower() == "true" or \
                     os.getenv("NOTIFY_ON_TWITCH_OFFLINE", "False").lower() == "true"
    twitch_id_ok = os.getenv("TWITCH_CLIENT_ID") and os.getenv("TWITCH_CLIENT_SECRET") and os.getenv("TWITCH_BROADCASTER_ID")
    twitch_ready = twitch_enabled and twitch_id_ok
    youtube_enabled = os.getenv("NOTIFY_ON_YT_ONLINE", "False").lower() == "true" or \
                      os.getenv("NOTIFY_ON_YT_NEWVIDEO", "False").lower() == "true"
    youtube_id_ok = os.getenv("YOUTUBE_API_KEY") and os.getenv("YOUTUBE_CHANNEL_ID")
    youtube_ready = youtube_enabled and youtube_id_ok
    nico_enabled = os.getenv("NOTIFY_ON_NICONICO_ONLINE", "False").lower() == "true" or \
                   os.getenv("NOTIFY_ON_NICONICO_NEW_VIDEO", "False").lower() == "true"
    nico_id_ok = os.getenv("NICONICO_USER_ID")
    nico_ready = nico_enabled and nico_id_ok
    if not (twitch_ready or youtube_ready or nico_ready):
        logger.critical("Twitch/YouTube/ニコニコのいずれも有効な設定がありません。アプリケーションは起動できません。")
        print("[CRITICAL] Twitch/YouTube/ニコニコのいずれも有効な設定がありません。settings.envを確認してください。")
        return False
    # --- トンネル起動 ---
    webhook_url = None
    tunnel_service = os.getenv("TUNNEL_SERVICE", "").lower()
    disable_tunnel_autostart = os.getenv("DISABLE_TUNNEL_AUTOSTART", "False").lower() == "true"
    if tunnel_service in ("cloudflare", "cloudflare_domain", "custom"):
        webhook_url = os.getenv("WEBHOOK_CALLBACK_URL_PERMANENT")
    elif tunnel_service in ("cloudflare_tempurl", "ngrok", "localtunnel"):
        webhook_url = os.getenv("WEBHOOK_CALLBACK_URL_TEMPORARY")
    else:
        webhook_url = os.getenv("WEBHOOK_CALLBACK_URL")
    cleanup_eventsub_subscriptions(webhook_url, logger_to_use=logger)
    tunnel_proc = None
    if not disable_tunnel_autostart:
        tunnel_proc = start_tunnel_and_monitor(tunnel_logger)
        if not tunnel_proc:
            tunnel_logger.critical("トンネルの起動に失敗しました。アプリケーションは起動できません。")
            return False
    else:
        logger.info("DISABLE_TUNNEL_AUTOSTARTが有効のため、トンネル自動起動をスキップします。")
    # --- Twitch初期化 ---
    if twitch_ready:
        setup_broadcaster_id(logger_to_use=logger)
        TWITCH_APP_ACCESS_TOKEN = get_valid_app_access_token(logger_to_use=logger)
        if not TWITCH_APP_ACCESS_TOKEN:
            logger.critical("TwitchAPIアクセストークンの取得に失敗しました。Twitch通知は無効化されます。")
        else:
            logger.info("TwitchAPIアクセストークン取得を確認しました。")
            event_types_to_subscribe = []
            if os.getenv("NOTIFY_ON_TWITCH_ONLINE", "False").lower() == "true":
                event_types_to_subscribe.append("stream.online")
            if os.getenv("NOTIFY_ON_TWITCH_OFFLINE", "False").lower() == "true":
                event_types_to_subscribe.append("stream.offline")
            all_subscriptions_successful = True
            for event_type in event_types_to_subscribe:
                logger.info(f"{event_type} のEventSubサブスクリプションを作成します...")
                sub_response = create_eventsub_subscription(
                    event_type, logger_to_use=logger, webhook_url=webhook_url)
                if not sub_response or not isinstance(sub_response, dict) or not sub_response.get("data") or not isinstance(sub_response["data"], list) or not sub_response["data"]:
                    logger.critical(f"{event_type} EventSubサブスクリプションの作成に失敗しました。詳細: {sub_response}")
                    all_subscriptions_successful = False
                    break
                if sub_response.get("status") == "already exists":
                    logger.info(f"{event_type} EventSubサブスクリプションは既に存在します。ID: {sub_response.get('id')}")
                else:
                    subscription_details = sub_response['data'][0]
                    logger.info(f"{event_type} EventSubサブスクリプション作成成功。ID: {subscription_details.get('id')}, ステータス: {subscription_details.get('status')}")
            if not all_subscriptions_successful:
                logger.critical("必須EventSubサブスクリプションの作成に失敗したため、Twitch通知は無効化されます。")
    else:
        logger.info("Twitch通知は無効または設定不足のためスキップされます。")
    # --- YouTube・ニコニコ監視スレッド起動 ---
    if youtube_ready:
        start_youtube_monitor()
    if nico_ready:
        start_niconico_monitor()
    logger.info("アプリケーションの初期化が完了しました。")
    return True
