# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

from version_info import __version__

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


import customtkinter as ctk

DEFAULT_FONT = ("Yu Gothic UI", 18, "normal")

TEMPLATE_KEYS = {
    "Twitch": [
        ("配信開始テンプレート", "BLUESKY_TW_ONLINE_TEMPLATE_PATH"),
        ("配信終了テンプレート", "BLUESKY_TW_OFFLINE_TEMPLATE_PATH"),
        ("画像ファイル", "BLUESKY_IMAGE_PATH"),
    ],
    "YouTube": [
        ("配信開始テンプレート", "BLUESKY_YT_ONLINE_TEMPLATE_PATH"),
        ("新着動画テンプレート", "BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH"),
        ("画像ファイル", "BLUESKY_IMAGE_PATH"),
    ],
    "ニコニコ": [
        ("配信開始テンプレート", "BLUESKY_NICO_ONLINE_TEMPLATE_PATH"),
        ("新着動画テンプレート", "BLUESKY_NICO_NEW_VIDEO_TEMPLATE_PATH"),
        ("画像ファイル", "BLUESKY_IMAGE_PATH"),
    ],
}

class BlueskyPostSettingsFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True)
        # --- Twitchタブ ---
        tabview.add("Twitch")
        from .twitch_notice_frame import TwitchNoticeFrame
        self.twitch_frame = TwitchNoticeFrame(tabview)
        self.twitch_frame.pack(fill="both", expand=True, padx=10, pady=10, in_=tabview.tab("Twitch"))
        # --- YouTubeタブ ---
        tabview.add("YouTube")
        from .youtube_notice_frame import YouTubeNoticeFrame
        self.youtube_frame = YouTubeNoticeFrame(tabview)
        self.youtube_frame.pack(fill="both", expand=True, padx=10, pady=10, in_=tabview.tab("YouTube"))
        # --- ニコニコタブ ---
        tabview.add("ニコニコ")
        from .niconico_notice_frame import NiconicoNoticeFrame
        self.nico_frame = NiconicoNoticeFrame(tabview)
        self.nico_frame.pack(fill="both", expand=True, padx=10, pady=10, in_=tabview.tab("ニコニコ"))

        # サービス欄にテンプレート編集ボタン（有効化）を追加
        from .template_editor_dialog import TemplateEditorDialog
        def open_template_editor(template_type, initial_text_var):
            def on_save(new_text):
                initial_text_var.set(new_text)
            TemplateEditorDialog(self, template_type=template_type, initial_text=initial_text_var.get(), on_save=on_save)
        for tab_name, template_type, var_attr in [
            ("Twitch", "twitch_online", getattr(self.twitch_frame, "tpl_online", None)),
            ("YouTube", "yt_online", getattr(self.youtube_frame, "tpl_online", None)),
            ("ニコニコ", "niconico_online", getattr(self.nico_frame, "tpl_online", None)),
        ]:
            tab = tabview.tab(tab_name)
            if var_attr is not None:
                edit_btn = ctk.CTkButton(tab, text="テンプレート編集", state="normal", font=DEFAULT_FONT, width=180,
                                         command=lambda t=template_type, v=var_attr: open_template_editor(t, v))
                edit_btn.pack(anchor="ne", padx=10, pady=(5, 0))

        # タブボタンのサイズとフォントを変更
        for button in tabview._segmented_button._buttons_dict.values():
            button.configure(font=DEFAULT_FONT)
