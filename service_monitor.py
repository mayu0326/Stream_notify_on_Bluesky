from youtube_monitor import YouTubeMonitor
from niconico_monitor import NiconicoMonitor
import os

def start_youtube_monitor():
    def on_youtube_live(live_info):
        # NOTE: YouTubeMonitor から詳細情報dictが渡されるようになったので、
        # event_contextにそのまま渡すことでテンプレートでtitle等が利用可能。
        if os.getenv("NOTIFY_ON_YOUTUBE_ONLINE", "False") == "True":
            from bluesky import BlueskyPoster
            import logging
            logger = logging.getLogger("AppLogger")
            logger.info("[YouTube] 配信開始検出！")
            try:
                bluesky_poster = BlueskyPoster(
                    os.getenv("BLUESKY_USERNAME"),
                    os.getenv("BLUESKY_APP_PASSWORD")
                )
                event_context = live_info or {}
                # platform="yt_nico"のまま
                success = bluesky_poster.post_stream_online(
                    event_context=event_context,
                    image_path=os.getenv("BLUESKY_IMAGE_PATH"),
                    platform="yt_nico"
                )
                if success:
                    logger.info("[YouTube] Bluesky投稿成功（配信開始）")
                else:
                    logger.error("[YouTube] Bluesky投稿失敗（配信開始）")
            except Exception as e:
                logger.error(f"[YouTube] Bluesky投稿中に例外発生: {e}", exc_info=e)
    def on_youtube_new_video(video_id):
        if os.getenv("NOTIFY_ON_YOUTUBE_NEW_VIDEO", "False") == "True":
            from bluesky import BlueskyPoster
            import logging
            logger = logging.getLogger("AppLogger")
            logger.info(f"[YouTube] 新着動画検出: {video_id}")
            try:
                bluesky_poster = BlueskyPoster(
                    os.getenv("BLUESKY_USERNAME"),
                    os.getenv("BLUESKY_APP_PASSWORD")
                )
                event_context = {
                    "title": "YouTube新着動画投稿",
                    "video_id": video_id,
                    "video_url": f"https://www.youtube.com/watch?v={video_id}"
                }
                success = bluesky_poster.post_new_video(
                    event_context=event_context,
                    image_path=os.getenv("BLUESKY_IMAGE_PATH")
                )
                if success:
                    logger.info("[YouTube] Bluesky投稿成功（新着動画）")
                else:
                    logger.error("[YouTube] Bluesky投稿失敗（新着動画）")
            except Exception as e:
                logger.error(f"[YouTube] Bluesky投稿中に例外発生: {e}", exc_info=e)
    yt_monitor = YouTubeMonitor(
        os.getenv("YOUTUBE_API_KEY"), os.getenv("YOUTUBE_CHANNEL_ID"), int(os.getenv("YOUTUBE_POLL_INTERVAL", 60)),
        on_youtube_live, on_youtube_new_video
    )
    yt_monitor.start()
    return yt_monitor

def handle_youtube_offline(live_info):
    """
    YouTube配信終了時の通知処理
    Args:
        live_info (dict): 配信終了時の詳細情報
    """
    if os.getenv("NOTIFY_ON_YOUTUBE_OFFLINE", "False").lower() != "true":
        return
    from bluesky import BlueskyPoster
    import logging
    logger = logging.getLogger("AppLogger")
    logger.info("[YouTube] 配信終了検出！")
    try:
        bluesky_poster = BlueskyPoster(
            os.getenv("BLUESKY_USERNAME"),
            os.getenv("BLUESKY_APP_PASSWORD")
        )
        event_context = live_info or {}
        # 必要な情報がなければ最低限埋める
        event_context.setdefault("title", "YouTube配信終了")
        event_context.setdefault("channel_name", os.getenv("YOUTUBE_CHANNEL_ID", ""))
        event_context.setdefault("stream_url", "")
        event_context.setdefault("start_time", "")
        # テンプレートパス
        tpl_path = os.getenv("BLUESKY_YT_OFFLINE_TEMPLATE_PATH", "templates/yt_offline_template.txt")
        # post_stream_offlineはTwitch用だが、YouTubeでも使えるようにする
        success = bluesky_poster.post_stream_offline(
            event_context=event_context,
            image_path=os.getenv("BLUESKY_IMAGE_PATH"),
            platform="youtube"
        )
        if success:
            logger.info("[YouTube] Bluesky投稿成功（配信終了）")
        else:
            logger.error("[YouTube] Bluesky投稿失敗（配信終了）")
    except Exception as e:
        logger.error(f"[YouTube] Bluesky投稿中に例外発生: {e}", exc_info=e)

def start_niconico_monitor():
    def on_niconico_live(event_context):
        if os.getenv("NOTIFY_ON_NICONICO_ONLINE", "False") == "True":
            from bluesky import BlueskyPoster
            import logging
            logger = logging.getLogger("AppLogger")
            logger.info(f"[ニコ生] 配信開始検出: {event_context.get('live_id')}")
            try:
                bluesky_poster = BlueskyPoster(
                    os.getenv("BLUESKY_USERNAME"),
                    os.getenv("BLUESKY_APP_PASSWORD")
                )
                # titleが空ならデフォルト
                if not event_context.get("title"):
                    event_context["title"] = "ニコニコ生放送配信開始"
                if not event_context.get("stream_url") and event_context.get("live_id"):
                    event_context["stream_url"] = f"https://live.nicovideo.jp/watch/{event_context['live_id']}"
                success = bluesky_poster.post_stream_online(
                    event_context=event_context,
                    image_path=os.getenv("BLUESKY_IMAGE_PATH"),
                    platform="yt_nico"
                )
                if success:
                    logger.info("[ニコ生] Bluesky投稿成功（配信開始）")
                else:
                    logger.error("[ニコ生] Bluesky投稿失敗（配信開始）")
            except Exception as e:
                logger.error(f"[ニコ生] Bluesky投稿中に例外発生: {e}", exc_info=e)
    def on_niconico_new_video(event_context):
        if os.getenv("NOTIFY_ON_NICONICO_NEW_VIDEO", "False") == "True":
            from bluesky import BlueskyPoster
            import logging
            logger = logging.getLogger("AppLogger")
            logger.info(f"[ニコ動] 新着動画検出: {event_context.get('video_id')}")
            try:
                bluesky_poster = BlueskyPoster(
                    os.getenv("BLUESKY_USERNAME"),
                    os.getenv("BLUESKY_APP_PASSWORD")
                )
                if not event_context.get("title"):
                    event_context["title"] = "ニコニコ動画新着投稿"
                if not event_context.get("video_url") and event_context.get("video_id"):
                    event_context["video_url"] = f"https://www.nicovideo.jp/watch/{event_context['video_id']}"
                success = bluesky_poster.post_new_video(
                    event_context=event_context,
                    image_path=os.getenv("BLUESKY_IMAGE_PATH")
                )
                if success:
                    logger.info("[ニコ動] Bluesky投稿成功（新着動画）")
                else:
                    logger.error("[ニコ動] Bluesky投稿失敗（新着動画）")
            except Exception as e:
                logger.error(f"[ニコ動] Bluesky投稿中に例外発生: {e}", exc_info=e)
    nn_monitor = NiconicoMonitor(
        os.getenv("NICONICO_USER_ID"), int(os.getenv("NICONICO_LIVE_POLL_INTERVAL", 60)),
        on_niconico_live, on_niconico_new_video
    )
    nn_monitor.start()
    return nn_monitor

