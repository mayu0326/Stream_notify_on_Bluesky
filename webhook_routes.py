from flask import Blueprint, jsonify, request, current_app, send_from_directory
import eventsub
import bluesky  # BlueskyPosterはbluesky経由で参照
from markupsafe import escape
import os
import threading
import time

webhook_bp = Blueprint('webhook', __name__)

# --- 直近のRaidイベントを保存するための簡易メモリキャッシュ ---
raid_event_cache = {}
raid_event_cache_lock = threading.Lock()
RAID_CACHE_EXPIRE_SEC = 180  # 180秒以内のRaidを有効とみなす

@webhook_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@webhook_bp.route("/webhook", methods=["POST", "GET"])
@webhook_bp.route("/webhook/", methods=["POST", "GET"])
def handle_webhook():
    app = current_app
    if request.method == "GET":
        app.logger.info("Webhookエンドポイントは正常に稼働しています。")
        return "Webhook endpoint is working! POST requests only.", 200
    if not eventsub.verify_signature(request):
        return jsonify({"status": "signature mismatch"}), 403
    try:
        data = request.get_json()
        if data is None:
            app.logger.warning("Webhook受信: 無効なJSONデータまたは空のボディ")
            return jsonify({"error": "Invalid JSON or empty body"}), 400
    except Exception as e:
        app.logger.error(f"Webhook受信: JSON解析エラー: {e}", exc_info=e)
        return jsonify({"error": "Invalid JSON"}), 400
    message_type = request.headers.get("Twitch-Eventsub-Message-Type")
    subscription_payload = data.get("subscription", {}) if isinstance(data, dict) else {}
    subscription_type = subscription_payload.get("type")
    if message_type == "webhook_callback_verification":
        challenge = data.get("challenge", "") if isinstance(data, dict) else ""
        app.logger.info(f"Webhook検証チャレンジ受信 ({subscription_type if subscription_type else 'タイプ不明'}): {challenge[:50]}...")
        return challenge, 200, {"Content-Type": "text/plain"}
    if message_type == "notification":
        event_data = data.get("event", {}) if isinstance(data, dict) else {}
        broadcaster_user_login_from_event = event_data.get("broadcaster_user_login")
        if not broadcaster_user_login_from_event:
            app.logger.warning(f"Webhook通知 ({subscription_type}): 'event.broadcaster_user_login' が不足しています。処理をスキップします。イベントデータ: {event_data}")
            return jsonify({"error": "Missing required field: event.broadcaster_user_login"}), 400
        broadcaster_user_name_from_event = event_data.get("broadcaster_user_name", broadcaster_user_login_from_event)
        app.logger.info(f"通知受信 ({subscription_type}) for {broadcaster_user_name_from_event or broadcaster_user_login_from_event}")
        notify_on_online_str = os.getenv("NOTIFY_ON_TWITCH_ONLINE")
        notify_on_online_str = notify_on_online_str.lower()
        NOTIFY_ON_ONLINE = notify_on_online_str == "true"
        notify_on_offline_str = os.getenv("NOTIFY_ON_TWITCH_OFFLINE", "False").lower()
        NOTIFY_ON_OFFLINE = notify_on_offline_str == "true"
        if subscription_type == "stream.online" and NOTIFY_ON_ONLINE:
            # title, category_nameをTwitch APIで補完
            title_val = event_data.get("title")
            category_val = event_data.get("category_name")
            # API補完が必要な場合のみ呼び出し
            if not title_val or not category_val:
                channel_info = eventsub.get_channel_information(event_data.get("broadcaster_user_id"))
                if not title_val:
                    title_val = channel_info.get("title") or f"{broadcaster_user_name_from_event}の配信"
                if not category_val:
                    category_val = channel_info.get("game_name") or ""
            event_context = {
                "broadcaster_user_id": event_data.get("broadcaster_user_id"),
                "broadcaster_user_login": broadcaster_user_login_from_event,
                "broadcaster_user_name": broadcaster_user_name_from_event,
                "title": title_val,
                "category_name": category_val,
                "game_id": event_data.get("game_id"),
                "game_name": event_data.get("game_name", category_val),
                "language": event_data.get("language"),
                "started_at": event_data.get("started_at"),
                "type": event_data.get("type"),
                "is_mature": event_data.get("is_mature"),
                "tags": event_data.get("tags", []),
                "stream_url": f"https://twitch.tv/{broadcaster_user_login_from_event}"
            }
            try:
                bluesky_poster = bluesky.BlueskyPoster(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_APP_PASSWORD"))
                success = bluesky_poster.post_stream_online(event_context=event_context, image_path=os.getenv("BLUESKY_IMAGE_PATH"))
                app.logger.info(f"Bluesky投稿試行 (stream.online): {event_context.get('broadcaster_user_login')}, 成功: {success}")
                return jsonify({"status": "success" if success else "bluesky error processing stream.online"}), 200
            except Exception as e:
                app.logger.error(f"Bluesky投稿エラー (stream.online): {str(e)}", exc_info=True)
                return jsonify({"error": "Internal server error during stream.online processing"}), 500
        elif subscription_type == "stream.offline":
            if NOTIFY_ON_OFFLINE:
                import datetime
                ended_at = datetime.datetime.now().isoformat()
                # --- 直近のRaidイベントと突き合わせて判定 ---
                raid_info = None
                with raid_event_cache_lock:
                    raid_entry = raid_event_cache.get(broadcaster_user_login_from_event)
                    if raid_entry and (time.time() - raid_entry["timestamp"] <= RAID_CACHE_EXPIRE_SEC):
                        raid_info = raid_entry
                        # 使い終わったらキャッシュから削除
                        del raid_event_cache[broadcaster_user_login_from_event]
                event_context = {
                    "broadcaster_user_id": event_data.get("broadcaster_user_id"),
                    "broadcaster_user_login": broadcaster_user_login_from_event,
                    "broadcaster_user_name": broadcaster_user_name_from_event,
                    "channel_url": f"https://twitch.tv/{broadcaster_user_login_from_event}",
                    "ended_at": ended_at,
                }
                if raid_info:
                    event_context["to_broadcaster_user_name"] = raid_info["to_broadcaster_user_name"]
                    event_context["to_broadcaster_user_login"] = raid_info["to_broadcaster_user_login"]
                    event_context["to_stream_url"] = raid_info["to_stream_url"]
                app.logger.info(f"stream.offlineイベント処理開始: {event_context.get('broadcaster_user_name')} ({event_context.get('broadcaster_user_login')})")
                try:
                    bluesky_poster = bluesky.BlueskyPoster(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_APP_PASSWORD"))
                    success = bluesky_poster.post_stream_offline(event_context=event_context)
                    app.logger.info(f"Bluesky投稿試行 (stream.offline): {event_context.get('broadcaster_user_login')}, 成功: {success}")
                    return jsonify({"status": "success, offline notification posted" if success else "bluesky error, offline notification not posted"}), 200
                except Exception as e:
                    app.logger.error(f"Bluesky投稿エラー (stream.offline): {str(e)}", exc_info=True)
                    return jsonify({"error": "Internal server error during stream.offline processing"}), 500
            else:
                app.logger.info(f"stream.offline通知は設定によりスキップされました: {broadcaster_user_login_from_event}")
                return jsonify({"status": "skipped, offline notifications disabled"}), 200
        elif subscription_type == "channel.raid":
            # outgoing（自分がRaidを送った場合）のみ通知
            if event_data.get("from_broadcaster_user_login") == broadcaster_user_login_from_event:
                raid_to_name = event_data.get("to_broadcaster_user_name")
                raid_to_login = event_data.get("to_broadcaster_user_login")
                # --- Raidイベントをキャッシュに保存 ---
                with raid_event_cache_lock:
                    raid_event_cache[broadcaster_user_login_from_event] = {
                        "to_broadcaster_user_name": raid_to_name,
                        "to_broadcaster_user_login": raid_to_login,
                        "to_stream_url": f"https://twitch.tv/{raid_to_login}" if raid_to_login else None,
                        "timestamp": time.time()
                    }
                event_context = {
                    "from_broadcaster_user_id": event_data.get("from_broadcaster_user_id"),
                    "from_broadcaster_user_login": event_data.get("from_broadcaster_user_login"),
                    "from_broadcaster_user_name": event_data.get("from_broadcaster_user_name"),
                    "to_broadcaster_user_id": event_data.get("to_broadcaster_user_id"),
                    "to_broadcaster_user_login": raid_to_login,
                    "to_broadcaster_user_name": raid_to_name,
                    "raid_url": f"https://twitch.tv/{raid_to_login}" if raid_to_login else None,
                    "viewers": event_data.get("viewers"),
                    "ended_at": None  # Raid時刻は省略またはサーバー時刻を入れてもOK
                }
                app.logger.info(f"channel.raid(outgoing)イベント処理開始: {event_context.get('from_broadcaster_user_name')} → {raid_to_name}")
                try:
                    bluesky_poster = bluesky.BlueskyPoster(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_APP_PASSWORD"))
                    # Raid用テンプレートを明示的に指定
                    success = bluesky_poster.post_stream_offline(event_context=event_context, image_path=None, platform="twitch", template_path="templates/twitch/twitch_raid_template.txt")
                    app.logger.info(f"Bluesky投稿試行 (channel.raid): {event_context.get('from_broadcaster_user_login')} → {raid_to_name}, 成功: {success}")
                    return jsonify({"status": "success, raid notification posted" if success else "bluesky error, raid notification not posted"}), 200
                except Exception as e:
                    app.logger.error(f"Bluesky投稿エラー (channel.raid): {str(e)}", exc_info=True)
                    return jsonify({"error": "Internal server error during channel.raid processing"}), 500
        if subscription_type == "stream.online" and not NOTIFY_ON_ONLINE:
            app.logger.info(f"stream.online通知は設定によりスキップされました: {broadcaster_user_login_from_event}")
            return jsonify({"status": "skipped, online notifications disabled"}), 200
        else:
            app.logger.warning(f"不明なサブスクリプションタイプ ({subscription_type}) の通知受信: {broadcaster_user_login_from_event}")
            return jsonify({"status": "error", "message": f"Unknown or unhandled subscription type: {subscription_type}"}), 400
    if message_type == 'revocation':
        revocation_status = subscription_payload.get("status", "不明なステータス")
        app.logger.warning(f"Twitch EventSubサブスクリプション失効通知受信: タイプ - {subscription_type}, ステータス - {revocation_status}, ユーザー - {data.get('event', {}).get('broadcaster_user_login', 'N/A')}")
        return jsonify({"status": "revocation notification received"}), 200
    app.logger.info(f"受信した未処理のTwitch EventSubメッセージタイプ: {message_type if message_type else '不明'}. データ: {data}")
    return jsonify({"status": "unhandled message type or event"}), 200

@webhook_bp.route("/api/tunnel_status", methods=["GET"])
def api_tunnel_status():
    from tunnel_manager import get_tunnel_proc
    import socket
    tunnel_proc = get_tunnel_proc()
    # まず従来通りプロセス変数で判定
    if tunnel_proc and hasattr(tunnel_proc, 'poll') and tunnel_proc.poll() is None:
        return jsonify({"status": "UP"})
    # プロセス変数がNoneでも、ポート疎通で判定（例: 3000番ポートがLISTENしているか）
    try:
        sock = socket.create_connection(("127.0.0.1", 3000), timeout=1)
        sock.close()
        return jsonify({"status": "UP"})
    except Exception:
        pass
    return jsonify({"status": "DOWN"})

@webhook_bp.route("/api/tunnel_ping", methods=["GET"])
def api_tunnel_ping():
    from tunnel_manager import get_tunnel_proc
    tunnel_proc = get_tunnel_proc()
    if tunnel_proc and hasattr(tunnel_proc, 'poll') and tunnel_proc.poll() is None:
        return jsonify({"status": "UP"})
    else:
        return jsonify({"status": "DOWN"})

@webhook_bp.route("/api/server_status", methods=["GET"])
def api_server_status():
    try:
        # サーバーの状態を確認するロジックを追加
        from main import is_server_running
        if is_server_running():
            return jsonify({"status": "UP"})
        else:
            return jsonify({"status": "DOWN"})
    except Exception as e:
        current_app.logger.error(f"サーバー状態確認エラー: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)})

@webhook_bp.route("/api/url_status", methods=["GET"])
def api_url_status():
    try:
        # URL状態を確認するロジックを追加
        url_status = "OK"  # 仮の状態
        return jsonify({"status": url_status})
    except Exception as e:
        current_app.logger.error(f"URL状態確認エラー: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)})

def handle_404(e):
    try:
        safe_url = escape(request.url)
        safe_ua = escape(request.user_agent.string)
        current_app.logger.warning(f"404エラー発生: {safe_url} (User agent: {safe_ua})")
    except AttributeError:
        print("Warning: 404 error (URL情報取得不可)")
    return "Not Found", 404
