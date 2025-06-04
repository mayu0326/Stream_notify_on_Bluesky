# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import customtkinter as ctk
from gui.account_settings_frame import AccountSettingsFrame
from gui.tunnel_connection import TunnelConnection
from gui.bluesky_post_settings_frame import BlueskyPostSettingsFrame
from gui.log_viewer import LogViewer  # 正しいクラス名に修正
from gui.logging_notification_frame import LoggingNotificationFrame
from gui.setup_wizard import SetupWizard
from gui.setting_status import SettingStatusFrame
from gui.main_control_frame import MainControlFrame
from gui.notification_customization_frame import NotificationCustomizationFrame
from gui.niconico_notice_frame import NiconicoNoticeFrame
from gui.twitch_notice_frame import TwitchNoticeFrame
from gui.youtube_notice_frame import YouTubeNoticeFrame
import configparser

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

"""
エントリポイント: 初回起動時はSetupWizard、設定済みならMainWindowを表示
"""

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")
SETTINGS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))

def load_user_settings():
    settings = {}
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#'):
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        settings[k.strip()] = v.strip()
    return settings

def save_user_settings(settings):
    # 既存envを読み込み、該当キーだけ上書き
    lines = []
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, encoding='utf-8') as f:
            lines = f.readlines()
    keys = set(settings.keys())
    new_lines = []
    for line in lines:
        if '=' in line and not line.strip().startswith('#'):
            k = line.split('=', 1)[0].strip()
            if k in keys:
                new_lines.append(f"{k}={settings[k]}\n")
                keys.remove(k)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    for k in keys:
        new_lines.append(f"{k}={settings[k]}\n")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

class MainWindow(ctk.CTk):
    def __init__(self):
        user_settings = load_user_settings()
        appearance = user_settings.get('APPEARANCE_MODE', 'light')  # デフォルトをライトモードに変更
        language = user_settings.get('LANGUAGE', '日本語')
        ctk.set_appearance_mode(appearance)
        self._user_settings = user_settings
        self._appearance = appearance
        self._language = language
        super().__init__()
        self.title("StreamNotifyonBluesky - メインウィンドウ")
        self.geometry("740x730")
        self.resizable(False, False)
        self.tabview = ctk.CTkTabview(self)
        self._create_tabs()
        self.tabview.pack(fill="both", expand=True, pady=(0, 0))
        self._set_tabview_button_color()  # 初期化時に文字色を設定

    def _set_tabview_button_color(self):
        # appearanceに応じてタブメニューの文字色を切り替え
        mode = ctk.get_appearance_mode().lower()
        if mode == "light":
            fg = "#222"
        elif mode == "dark":
            fg = "#fff"
        elif mode == "system":
            # システム設定に基づいて色を決定
            fg = "#fff" if self._appearance == "dark" else "#222"
        else:
            fg = "#222"  # デフォルトは黒
        try:
            self.tabview._segmented_button.configure(text_color=fg)
        except Exception:
            pass

    def on_appearance_change(self, value):
        ctk.set_appearance_mode(value)
        self._appearance = value
        self._user_settings['APPEARANCE_MODE'] = value
        save_user_settings(self._user_settings)
        self._set_tabview_button_color()
        if hasattr(self, 'main_control_frame'):
            self.main_control_frame.update_appearance()
        if hasattr(self, 'account_settings_frame'):
            self.account_settings_frame.update_appearance()

    def on_language_change(self, value):
        self._language = value
        self._user_settings['LANGUAGE'] = value
        save_user_settings(self._user_settings)
        print(f"Language changed to: {value}")

    def _create_tabs(self):
        self.tabview.add("アプリ管理")
        self.tabview.add("状況")
        self.tabview.add("アカウント")
        self.tabview.add("Bluesky投稿")
        self.tabview.add("トンネル通信")
        self.tabview.add("ログ・通知")
        self.tabview.add("オプション")
        # アプリ管理
        self.tabview.tab("アプリ管理").grid_rowconfigure(0, weight=1)
        self.tabview.tab("アプリ管理").grid_columnconfigure(0, weight=1)
        self.main_control_frame = MainControlFrame(self.tabview.tab("アプリ管理"))
        self.main_control_frame.grid(row=0, column=0, sticky="nsew")
        # 状況
        self.tabview.tab("状況").grid_rowconfigure(0, weight=1)
        self.tabview.tab("状況").grid_columnconfigure(0, weight=1)
        self.setting_status_frame = SettingStatusFrame(self.tabview.tab("状況"))
        self.setting_status_frame.grid(row=0, column=0, sticky="nsew")
        # アカウント
        self.account_settings_frame = AccountSettingsFrame(self.tabview.tab("アカウント"))
        self.account_settings_frame.pack(fill="both", expand=True)
        # Bluesky投稿
        self.bluesky_post_settings_frame = BlueskyPostSettingsFrame(self.tabview.tab("Bluesky投稿"))
        self.bluesky_post_settings_frame.pack(fill="both", expand=True)
        # トンネル通信
        self.tabview.tab("トンネル通信").grid_rowconfigure(0, weight=1)
        self.tabview.tab("トンネル通信").grid_columnconfigure(0, weight=1)
        self.tunnel_connection = TunnelConnection(self.tabview.tab("トンネル通信"))
        self.tunnel_connection.grid(row=0, column=0, sticky="nsew")
        # ログ・通知
        self.logging_notification_frame = LoggingNotificationFrame(self.tabview.tab("ログ・通知"))
        self.logging_notification_frame.grid(row=0, column=0, sticky="nsew")
        # メインタブのフォント・サイズ・間隔を調整（被り防止）
        self.tabview._segmented_button.configure(
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            height=24,
            corner_radius=4
        )

        # タブ切り替え時に設定状況タブをリロード
        original_command = self.tabview._segmented_button.cget("command")
        def on_tab_changed(value=None):
            self.tabview.set(value)  # まずタブを切り替える
            if self.tabview.get() == "状況":
                self.setting_status_frame.create_widgets()
        self.tabview._segmented_button.configure(command=on_tab_changed)
        # オプションタブの内容
        option_tab = self.tabview.tab("オプション")
        option_tab.grid_rowconfigure(0, weight=1)
        option_tab.grid_columnconfigure(0, weight=1)
        # option_frameの行数を増やし、上部に外観モード、下部に空欄
        option_frame = ctk.CTkFrame(option_tab)
        option_frame.grid(row=0, column=0, sticky="nsew")
        for i in range(7):
            option_frame.grid_rowconfigure(i, weight=1)
        for j in range(7):
            option_frame.grid_columnconfigure(j, weight=1)
        # ダークモード切替（最上部に移動）
        ctk.CTkLabel(option_frame, text="外観モード:", font=("Yu Gothic UI", 18)).grid(row=0, column=2, sticky="e", pady=(30,10), padx=(10,10))
        appearance_combo = ctk.CTkComboBox(
            option_frame,
            values=["system", "light", "dark"],
            width=180,
            font=("Yu Gothic UI", 18),
            command=self.on_appearance_change
        )
        appearance_combo.set(self._appearance)
        appearance_combo.grid(row=0, column=3, sticky="w", pady=(30,10), padx=(10,10))
        # 下部に空白スペース（将来の機能やリンク用）
        blank_area = ctk.CTkFrame(option_frame, fg_color="transparent", height=120)
        blank_area.grid(row=1, column=0, columnspan=7, sticky="nsew", pady=(10, 10))

    def open_log_viewer(self):
        LogViewer(self)

    def on_close(self):
        self.destroy()

# --- 共通カスタムダイアログ ---
import customtkinter as ctk

class CTkMessageBox(ctk.CTkToplevel):
    def __init__(self, master=None, title="", message="", icon="info", button_text="OK"):
        super().__init__(master)
        self.title(title)
        self.geometry("340x160")
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        self.result = None
        icon_map = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}
        ctk.CTkLabel(self, text=icon_map.get(icon, "ℹ️"), font=("Yu Gothic UI", 32)).pack(pady=(18, 0))
        ctk.CTkLabel(self, text=message, font=("Yu Gothic UI", 13), wraplength=300, justify="center").pack(pady=(8, 0))
        ctk.CTkButton(self, text=button_text, command=self._on_ok, width=80).pack(pady=18)
        self.bind("<Return>", lambda e: self._on_ok())
    def _on_ok(self):
        self.result = True
        self.destroy()

def show_ctk_info(master, title, message):
    CTkMessageBox(master, title=title, message=message, icon="info").wait_window()

def show_ctk_error(master, title, message):
    CTkMessageBox(master, title=title, message=message, icon="error").wait_window()

def show_ctk_warning(master, title, message):
    CTkMessageBox(master, title=title, message=message, icon="warning").wait_window()

# python-dotenvの警告回避: settings.envの先頭に空行や不正な行がないかチェック
settings_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../settings.env'))
if os.path.exists(settings_env_path):
    with open(settings_env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 先頭に空行や#以外の不正な行、または「//」で始まる行があれば削除
    cleaned = []
    for line in lines:
        if (line.strip() == '' or line.strip().startswith('//')) and not cleaned:
            continue  # 先頭の空行や//コメントはスキップ
        if line.strip().startswith('#') and not cleaned:
            continue  # 先頭の#コメントもスキップ
        cleaned.append(line)
    # さらに先頭が#で始まるコメント行だけの場合もスキップ
    while cleaned and cleaned[0].strip().startswith('#'):
        cleaned.pop(0)
    if cleaned != lines:
        with open(settings_env_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned)

def is_first_setup():
    return not os.path.exists("settings.env")


if __name__ == "__main__":
    try:
        MainWindow().mainloop()
    except KeyboardInterrupt:
        print("アプリケーションを終了します (Ctrl+C)")
        # トレースバックを抑制し、静かに終了
        sys.exit(0)
