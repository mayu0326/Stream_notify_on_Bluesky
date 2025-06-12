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

import time
import feedparser
from threading import Thread, Event
from version_info import __version__
from logging_config import configure_logging

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__


class NiconicoMonitor(Thread):
    """
    ニコニコ生放送およびニコニコ動画の新着を監視するスレッド。
    """

    def __init__(self, user_id, poll_interval, on_new_live, on_new_video, shutdown_event=None):
        # 監視対象ユーザーID、ポーリング間隔、コールバック関数を初期化
        super().__init__(daemon=True)
        self.user_id = user_id
        self.poll_interval = poll_interval
        self.on_new_live = on_new_live
        self.on_new_video = on_new_video
        self.last_live_id = None
        self.last_video_id = None
        self.shutdown_event = shutdown_event if shutdown_event is not None else Event()
        _, _, _, _, _, niconico_logger = configure_logging()
        self.logger = niconico_logger

    def run(self):
        # スレッドのメインループ。shutdown_eventがセットされたら安全に終了
        while not self.shutdown_event.is_set():
            try:
                # 生放送RSSから最新エントリを取得し、前回と異なればコールバック実行
                live_entry = self.get_latest_live_entry()
                if live_entry and (not self.last_live_id or live_entry.id != self.last_live_id):
                    event_context = self._entry_to_context(live_entry, kind="live")
                    self.logger.info(f"[NiconicoMonitor] 新着生放送検出: {getattr(live_entry, 'title', '')} ({getattr(live_entry, 'link', '')})")
                    self.on_new_live(event_context)
                    self.last_live_id = live_entry.id

                # 動画RSSから最新エントリを取得し、前回と異なればコールバック実行
                video_entry = self.get_latest_video_entry()
                if video_entry and (not self.last_video_id or video_entry.id != self.last_video_id):
                    event_context = self._entry_to_context(video_entry, kind="video")
                    self.logger.info(f"[NiconicoMonitor] 新着動画検出: {getattr(video_entry, 'title', '')} ({getattr(video_entry, 'link', '')})")
                    self.on_new_video(event_context)
                    self.last_video_id = video_entry.id

            except Exception as e:
                self.logger.error(f"[NiconicoMonitor] エラー発生: {e}", exc_info=e)
            self.shutdown_event.wait(self.poll_interval)

    def get_latest_live_entry(self):
        """
        ユーザーの最新生放送エントリを取得。
        """
        url = f"https://live.nicovideo.jp/feeds/user/{self.user_id}"
        feed = feedparser.parse(url)
        if feed.entries:
            return feed.entries[0]
        return None

    def get_latest_video_entry(self):
        """
        ユーザーの最新動画エントリを取得。
        """
        url = f"https://www.nicovideo.jp/user/{self.user_id}/video?rss=2.0"
        feed = feedparser.parse(url)
        if feed.entries:
            return feed.entries[0]
        return None

    def _entry_to_context(self, entry, kind="video"):
        """
        feedparserのentryからevent_context(dict)を生成
        """
        context = {
            "title": getattr(entry, "title", ""),
            "author": getattr(entry, "author", ""),
            "published": getattr(entry, "published", ""),
        }
        if kind == "video":
            context["video_id"] = entry.id
            context["video_url"] = getattr(entry, "link", "")
        elif kind == "live":
            context["live_id"] = entry.id
            context["stream_url"] = getattr(entry, "link", "")
        return context

    def get_latest_live_id(self):
        """
        ユーザーの最新生放送IDを取得。
        """
        entry = self.get_latest_live_entry()
        if entry:
            return entry.id
        return None

    def get_latest_video_id(self):
        """
        ユーザーの最新動画IDを取得。
        """
        entry = self.get_latest_video_entry()
        if entry:
            return entry.id
        return None
