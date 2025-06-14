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
import json
from dotenv import load_dotenv

load_dotenv("settings.env")

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__

LATEST_VIDEOS_PATH = "latest_videos.json"
MAX_VIDEOS = 20


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
        self._manual_retrieve_flag = False
        _, _, _, _, youtube_logger, _ = configure_logging()
        self.logger = youtube_logger
        self.logger.info("YouTube監視モジュールを起動します。")

    def load_latest_videos(self):
        if os.path.exists(LATEST_VIDEOS_PATH):
            with open(LATEST_VIDEOS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_latest_videos(self, videos):
        with open(LATEST_VIDEOS_PATH, "w", encoding="utf-8") as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)

    def fetch_video_details(self, video_ids):
        if not video_ids:
            self.logger.debug("[YouTubeMonitor] fetch_video_details: video_idsが空です")
            return []
        if self.api_key:
            # APIキーがあれば詳細のみAPIで取得
            url = (
                f"https://www.googleapis.com/youtube/v3/videos?id={','.join(video_ids)}&part=snippet,status,liveStreamingDetails&key={self.api_key}"
            )
            self.logger.debug(f"[YouTubeMonitor] fetch_video_details: APIリクエストURL: {url}")
            resp = requests.get(url)
            try:
                data = resp.json()
            except Exception as e:
                self.logger.error(f"[YouTubeMonitor] fetch_video_details: JSONデコード失敗: {e}")
                return []
            self.logger.debug(f"[YouTubeMonitor] fetch_video_details: APIレスポンス: {data}")
            result = []
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                status = item.get("status", {})
                live = item.get("liveStreamingDetails", {})
                result.append({
                    "videoId": item["id"],
                    "title": snippet.get("title", "(タイトル不明)"),
                    "privacyStatus": status.get("privacyStatus", "unknown"),
                    "publishedAt": snippet.get("publishedAt", ""),
                    "scheduledStartTime": live.get("scheduledStartTime", ""),
                    "actualStartTime": live.get("actualStartTime", "")
                })
            self.logger.debug(f"[YouTubeMonitor] fetch_video_details: 取得詳細リスト: {result}")
            return result
        else:
            # APIキー未設定時はRSSから詳細取得
            return self.fetch_video_details_from_rss(video_ids)

    def fetch_latest_video_ids(self, max_results=MAX_VIDEOS):
        # APIキー有無に関わらず、まずRSSでIDリストを取得（APIクォータ節約）
        return self.fetch_latest_video_ids_from_rss(max_results)

    def fetch_latest_video_ids_from_rss(self, max_results=MAX_VIDEOS):
        """
        YouTube公式RSSから動画IDリストを取得
        https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
        """
        import feedparser
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={self.channel_id}"
        self.logger.info(f"[YouTubeMonitor] RSS取得: {rss_url}")
        feed = feedparser.parse(rss_url)
        ids = []
        for entry in feed.entries[:max_results]:
            # entry.yt_videoid で動画IDが取得できる
            video_id = getattr(entry, "yt_videoid", None)
            if video_id:
                ids.append(video_id)
        self.logger.info(f"[YouTubeMonitor] RSSから取得した動画IDリスト: {ids}")
        return ids

    def fetch_video_details_from_rss(self, video_ids):
        """
        RSSから動画詳細（タイトル・公開日など）を取得
        """
        import feedparser
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={self.channel_id}"
        self.logger.info(f"[YouTubeMonitor] RSS取得: {rss_url}")
        feed = feedparser.parse(rss_url)
        details = []
        for entry in feed.entries:
            video_id = getattr(entry, "yt_videoid", None)
            if video_id and video_id in video_ids:
                details.append({
                    "videoId": video_id,
                    "title": getattr(entry, "title", "(タイトル不明)"),
                    "privacyStatus": "public",  # RSSでは常にpublic扱い
                    "publishedAt": getattr(entry, "published", ""),
                    "scheduledStartTime": "",
                    "actualStartTime": ""
                })
        self.logger.info(f"[YouTubeMonitor] RSSから取得した動画詳細: {details}")
        return details

    def fetch_live_video_ids_from_rss(self, max_results=MAX_VIDEOS):
        """
        YouTubeライブ配信専用RSSからライブ動画IDリストを取得
        https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID&eventType=live
        """
        import feedparser
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={self.channel_id}&eventType=live"
        self.logger.info(f"[YouTubeMonitor] ライブRSS取得: {rss_url}")
        feed = feedparser.parse(rss_url)
        ids = []
        for entry in feed.entries[:max_results]:
            video_id = getattr(entry, "yt_videoid", None)
            if video_id:
                ids.append(video_id)
        self.logger.info(f"[YouTubeMonitor] ライブRSSから取得した動画IDリスト: {ids}")
        return ids

    def run(self):
        print("[YouTubeMonitor] run() started")
        self.logger.info("[YouTubeMonitor] スレッド開始。初回動画情報を取得しローカル保存")
        # 初回: 最新20件の詳細を取得し保存
        latest_ids = self.fetch_latest_video_ids()
        latest_videos = self.fetch_video_details(latest_ids)
        self.save_latest_videos(latest_videos)
        for v in latest_videos:
            self.logger.info(f"[YouTubeMonitor] {v.get('title', '')} ({v.get('videoId', '')}): {v.get('privacyStatus', '')}, publishedAt={v.get('publishedAt', '')}, scheduled={v.get('scheduledStartTime', '')}, actual={v.get('actualStartTime', '')}")
        # --- 通常の監視ループ ---
        # ポーリング間隔（分単位→秒、最小値制限）
        poll_interval_min = int(os.getenv("YOUTUBE_POLL_INTERVAL", 60))
        poll_interval_online_min = int(os.getenv("YOUTUBE_POLL_INTERVAL_ONLINE", 60))
        poll_interval = max(poll_interval_min, 30) * 60  # 最小30分
        poll_interval_online = max(poll_interval_online_min, 45) * 60  # 最小45分
        while not self.shutdown_event.is_set():
            try:
                # 新着動画検出
                prev_videos = self.load_latest_videos()
                prev_ids = {v.get("videoId", "") for v in prev_videos}
                new_ids = self.fetch_latest_video_ids(max_results=3)
                added = [vid for vid in new_ids if vid not in prev_ids]
                if added:
                    new_details = self.fetch_video_details(added)
                    for v in new_details:
                        self.logger.info(f"[YouTubeMonitor] 新着動画検出: {v.get('title', '')} ({v.get('videoId', '')}): {v.get('privacyStatus', '')}, publishedAt={v.get('publishedAt', '')}, scheduled={v.get('scheduledStartTime', '')}, actual={v.get('actualStartTime', '')}")
                    # 最新リストを更新
                    all_videos = new_details + prev_videos
                    # 重複除去し最新MAX_VIDEOS件に
                    uniq = {v.get("videoId", ""): v for v in all_videos}
                    latest = list(uniq.values())[:MAX_VIDEOS]
                    self.save_latest_videos(latest)
                # ポーリング間隔（ライブ中は短縮、通常は長め）
                wait_time = poll_interval_online if self.last_live_status else poll_interval
                self.logger.debug(f"[YouTubeMonitor] 次回監視まで{wait_time // 60}分待機")
                # 即時再取得フラグ監視
                waited = 0
                while waited < wait_time:
                    if self.shutdown_event.is_set():
                        break
                    if self._manual_retrieve_flag:
                        self.logger.info("[YouTubeMonitor] 手動再取得リクエストを検知し即時実行")
                        self._manual_retrieve_flag = False
                        break
                    sleep_time = min(5, wait_time - waited)
                    self.shutdown_event.wait(sleep_time)
                    waited += sleep_time
            except Exception as e:
                self.logger.error(f"[YouTubeMonitor] 監視ループ例外: {e}")
                self.shutdown_event.wait(60)

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
            # 動画の公開状態とタイトルを同時に取得
            video_url = (
                f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet,status&key={self.api_key}"
            )
            self.logger.debug(f"[YouTubeMonitor] 動画詳細APIリクエスト: {video_url}")
            vresp = requests.get(video_url)
            vdata = vresp.json()
            vitems = vdata.get("items", [])
            if vitems:
                privacy = vitems[0]["status"].get("privacyStatus")
                title = vitems[0]["snippet"].get("title", "(タイトル不明)")
                self.logger.info(f"[YouTubeMonitor] 動画ID: {video_id}, 公開状態: {privacy}, タイトル: {title}")
                if privacy == "public":
                    # 最初の公開動画のタイトルをログ出力
                    self.logger.info(f"[YouTubeMonitor] 最新動画タイトル: {title} (ID: {video_id})")
                    return video_id
        self.logger.debug("[YouTubeMonitor] 公開動画なし")
        return None
