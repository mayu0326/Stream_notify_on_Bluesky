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

from version_info import __version__
import time
import requests
from threading import Thread, Event
import sys
import os
import logging
from logging_config import configure_logging
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__


class YouTubeMonitor(Thread):
    """
    YouTubeライブ配信および動画投稿の新着を監視するスレッド。
    """

    def __init__(
            self,
            api_key,
            channel_id,
            poll_interval,
            on_live,
            on_new_video,
            shutdown_event=None,
            initial_wait=30):
        # APIキー、チャンネルID、ポーリング間隔、コールバック関数を初期化
        super().__init__(daemon=True)
        self.api_key = api_key
        self.channel_id = channel_id
        self.poll_interval = poll_interval
        self.on_live = on_live
        self.on_new_video = on_new_video
        self.last_live_status = False
        self.last_video_id = None
        self.shutdown_event = shutdown_event if shutdown_event is not None else Event()
        self.initial_wait = initial_wait
        _, _, _, _, youtube_logger, _ = configure_logging()
        self.logger = youtube_logger
        print(f"[YouTubeMonitor] __init__ called: api_key={api_key}, channel_id={channel_id}, poll_interval={poll_interval}, initial_wait={initial_wait}")

    def run(self):
        print("[YouTubeMonitor] run() started")
        # スレッドのメインループ。shutdown_eventがセットされたら安全に終了
        import service_monitor
        poll_interval_online = int(os.getenv("YOUTUBE_POLL_INTERVAL_ONLINE", 30))
        poll_interval_offline = int(os.getenv("YOUTUBE_POLL_INTERVAL_OFFLINE", 180))
        # --- 起動後initial_wait秒待機し、公開設定がOnなら1度だけ新着動画チェック ---
        self.logger.info(f"[YouTubeMonitor] スレッド開始。初回新着動画チェックまで{self.initial_wait}秒待機")
        time.sleep(self.initial_wait)
        if os.getenv("NOTIFY_ON_YT_NEWVIDEO", "False").lower() == "true":
            self.logger.info("[YouTubeMonitor] 初回新着動画チェック実行")
            video_id = self.get_latest_video_id()
            if video_id and video_id != self.last_video_id:
                self.logger.info(f"[YouTubeMonitor] 新着動画検出: {video_id}")
                self.on_new_video(video_id)
                self.last_video_id = video_id
        # --- 通常の監視ループ ---
        while not self.shutdown_event.is_set():
            try:
                # ライブ配信の有無と詳細情報を確認
                live_info = self.check_live()
                if live_info and not self.last_live_status:
                    self.on_live(live_info)
                if not live_info and self.last_live_status:
                    service_monitor.handle_youtube_offline({})
                self.last_live_status = bool(live_info)

                # 新着動画の有無を確認
                self.logger.debug(f"[YouTubeMonitor] ライブ状態: {self.last_live_status}, 最新動画ID: {self.last_video_id}")
                if os.getenv("NOTIFY_ON_YT_NEWVIDEO", "False").lower() == "true":
                    video_id = self.get_latest_video_id()
                    if video_id:
                        if video_id != self.last_video_id:
                            self.logger.info(f"[YouTubeMonitor] 新着動画検出: {video_id}")
                            self.on_new_video(video_id)
                            self.last_video_id = video_id
                    else:
                        if self.last_video_id is not None:
                            self.logger.info("[YouTubeMonitor] 公開動画がなくなったためlast_video_idをリセット")
                        self.last_video_id = None
            except Exception as e:
                self.logger.error(f"[YouTubeMonitor] エラー発生: {e}", exc_info=e)
            # 配信中は短く、配信外は長く
            wait_time = poll_interval_online if self.last_live_status else poll_interval_offline
            self.shutdown_event.wait(wait_time)

    def check_live(self):
        """
        チャンネルで現在ライブ配信中かどうかを判定し、配信中なら詳細情報を返す。
        """
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&channelId={self.channel_id}&eventType=live&type=video&key={self.api_key}"
        )
        self.logger.debug(f"[YouTubeMonitor] ライブ確認APIリクエスト: {url}")
        resp = requests.get(url)
        data = resp.json()
        items = data.get("items", [])
        if not items:
            self.logger.debug("[YouTubeMonitor] ライブ配信中なし")
            return None
        # 1件目のライブ情報を取得
        item = items[0]
        snippet = item.get("snippet", {})
        live_info = {
            "title": snippet.get("title"),
            "video_id": item["id"].get("videoId"),
            "stream_url": f"https://www.youtube.com/watch?v={item['id'].get('videoId')}" if item["id"].get("videoId") else None,
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
            "start_time": snippet.get("publishedAt"),
            "channel_id": snippet.get("channelId"),
            "channel_name": snippet.get("channelTitle"),
            "channel_url": f"https://www.youtube.com/channel/{snippet.get('channelId')}" if snippet.get("channelId") else None,
            "description": snippet.get("description"),
        }
        self.logger.info(f"[YouTubeMonitor] ライブ配信中検出: {live_info.get('title')} ({live_info.get('stream_url')})")
        return live_info

    def get_latest_video_id(self):
        """
        チャンネルの最新動画IDを取得（公開動画のみ）。
        """
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&channelId={self.channel_id}&order=date&type=video&key={self.api_key}&maxResults=3"
        )
        self.logger.debug(f"[YouTubeMonitor] 新着動画確認APIリクエスト: {url}")
        resp = requests.get(url)
        data = resp.json()
        items = data.get("items", [])
        for item in items:
            video_id = item["id"].get("videoId")
            if not video_id:
                continue
            # 動画の公開状態を取得
            video_url = (
                f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=status&key={self.api_key}"
            )
            self.logger.debug(f"[YouTubeMonitor] 動画ステータス確認APIリクエスト: {video_url}")
            vresp = requests.get(video_url)
            vdata = vresp.json()
            vitems = vdata.get("items", [])
            if vitems:
                privacy = vitems[0]["status"].get("privacyStatus")
                self.logger.info(f"[YouTubeMonitor] 動画ID: {video_id}, 公開状態: {privacy}")
                if privacy == "public":
                    return video_id
        self.logger.debug("[YouTubeMonitor] 公開動画なし")
        return None
