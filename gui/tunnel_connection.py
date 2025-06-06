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

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__

import customtkinter as ctk
from .tunnel_cloudflare_frame import TunnelCloudflareFrame
from .tunnel_cloudflare_temp_frame import TunnelCloudflareTempFrame
from .tunnel_ngrok_frame import TunnelNgrokFrame
from .tunnel_localtunnel_frame import TunnelLocalTunnelFrame
from .tunnel_custom_frame import TunnelCustomFrame
import os

DEFAULT_FONT = "Yu Gothic UI", 17, "normal"

def remove_tunnel_settings(env_path):
    tunnel_keys = [
        "TUNNEL_SERVICE", "TUNNEL_CMD", "TUNNEL_NAME",
        "NGROK_AUTH_TOKEN", "NGROK_PORT", "NGROK_PROTOCOL",
        "LOCALTUNNEL_PORT", "LOCALTUNNEL_CMD", "CUSTOM_TUNNEL_CMD"
    ]
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            key = line.split("=", 1)[0].strip()
            if key not in tunnel_keys:
                new_lines.append(line)
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

class TunnelConnection(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(expand=True, fill="both")
        # settings.envからTUNNEL_SERVICEを取得し、なければ"none"に
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        service = "none"
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('TUNNEL_SERVICE='):
                        val = line.strip().split('=', 1)[1]
                        if val:
                            service = val
                        break
        self.var_service = ctk.StringVar(value=service)
        # ラベルとプルダウンは常に上部に固定
        label_service = ctk.CTkLabel(self.center_frame, text="トンネルサービス:", font=DEFAULT_FONT)
        label_service.pack(pady=(30, 5), anchor="center")
        self.combo = ctk.CTkComboBox(
            self.center_frame,
            values=["none","cloudflare_domain", "cloudflare_tempurl", "ngrok", "localtunnel", "custom"],
            variable=self.var_service,
            font=DEFAULT_FONT,
            width=400,
            command=self.on_service_change,
            state="readonly",
            justify="center"
        )
        self.combo.pack(pady=5, anchor="center")
        # --- 自動起動オプション ---
        self.var_autostart = ctk.BooleanVar()
        self._load_autostart_option(env_path)
        self.chk_autostart = ctk.CTkCheckBox(
            self.center_frame,
            text="トンネル自動起動を有効にする",
            font=("Yu Gothic UI", 15),
            variable=self.var_autostart,
            command=lambda: self._save_autostart_option(env_path)
        )
        self.chk_autostart.pack(pady=(10, 5), anchor="center")
        # サービスごとの内容を表示するエリア
        self.dynamic_area = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.dynamic_area.pack(expand=True, fill="both")
        self.current_frame = None
        self.on_service_change()

    def _load_autostart_option(self, env_path):
        # DISABLE_TUNNEL_AUTOSTARTがtrueならチェックを外す
        val = None
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('DISABLE_TUNNEL_AUTOSTART='):
                        val = line.strip().split('=', 1)[1].lower()
                        break
        # チェックON: 自動起動有効（=false or 未設定）、OFF: 無効（=true）
        self.var_autostart.set(val != 'true')

    def _save_autostart_option(self, env_path):
        # チェックON: DISABLE_TUNNEL_AUTOSTART=false、OFF: true
        lines = []
        found = False
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if line.strip().startswith('DISABLE_TUNNEL_AUTOSTART='):
                    lines[i] = f"DISABLE_TUNNEL_AUTOSTART={'false' if self.var_autostart.get() else 'true'}\n"
                    found = True
                    break
        if not found:
            lines.append(f"DISABLE_TUNNEL_AUTOSTART={'false' if self.var_autostart.get() else 'true'}\n")
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    def on_service_change(self, *args):
        for child in self.dynamic_area.winfo_children():
            child.destroy()
        service = self.var_service.get().lower()
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        # サービス名をenv用に正規化
        if service.startswith("cloudflare"):
            if "temp" in service:
                env_service = "cloudflare_tempurl"
            else:
                env_service = "cloudflare_domain"
        elif service == "custom":
            env_service = "custom"
        else:
            env_service = service
        self.save_tunnel_service_to_env(env_path, env_service)
        frame = None
        if service == "cloudflare_domain":
            frame = TunnelCloudflareFrame(self.dynamic_area)
            frame.pack(expand=True)
        elif service == "cloudflare_tempurl":
            frame = TunnelCloudflareTempFrame(self.dynamic_area)
            frame.pack(expand=True)
        elif service == "ngrok":
            frame = TunnelNgrokFrame(self.dynamic_area)
            frame.pack(expand=True)
        elif service == "localtunnel":
            frame = TunnelLocalTunnelFrame(self.dynamic_area)
            frame.pack(expand=True)
        elif service == "custom":
            frame = TunnelCustomFrame(self.dynamic_area)
            frame.pack(expand=True)
        elif service == "none":
            frame = ctk.CTkFrame(self.dynamic_area)
            frame.pack(expand=True, fill="both")
            label_explain = ctk.CTkLabel(frame, text="トンネル関連設定を初期化するには下記のボタンを押してください\n（ラベルは消えません）", font=DEFAULT_FONT)
            label_explain.pack(pady=(30, 20), anchor="center")
            def on_reset_tunnel_settings():
                from tkinter import messagebox
                result = messagebox.askyesno("確認", "トンネル関連設定を本来の初期値で再生成しますか？\nこの操作は元に戻せません。", icon='warning')
                if result:
                    # トンネル関連設定を初期値で再生成
                    tunnel_init = [
                        "# --- トンネル関連設定 ---\n",
                        "# Cloudflare Tunnelなどのトンネルを起動するコマンド \n",
                        "# 設定しない場合はトンネルを起動しません。\n",
                        "TUNNEL_SERVICE=none\n",
                        "DISABLE_TUNNEL_AUTOSTART=false\n",
                        "TUNNEL_CMD=\n",
                        "TUNNEL_NAME=\n",
                        "CLOUDFLARE_TEMP_CMD=\n",
                        "CLOUDFLARE_TEMP_PORT=\n",
                        "NGROK_CMD=\n",
                        "NGROK_PORT=\n",
                        "NGROK_PROTOCOL=\n",
                        "LOCALTUNNEL_PORT=\n",
                        "LOCALTUNNEL_CMD=\n",
                        "CUSTOM_TUNNEL_CMD=\n"
                    ]
                    # settings.envの既存内容を読み込み、トンネル関連以外を残す
                    lines = []
                    if os.path.exists(env_path):
                        with open(env_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                    # トンネル関連以外を残す
                    tunnel_keys = [
                        "TUNNEL_SERVICE", "TUNNEL_CMD", "TUNNEL_NAME",
                        "CLOUDFLARE_TEMP_CMD", "CLOUDFLARE_TEMP_PORT",
                        "NGROK_CMD", "NGROK_PORT", "NGROK_PROTOCOL",
                        "LOCALTUNNEL_PORT", "LOCALTUNNEL_CMD", "CUSTOM_TUNNEL_CMD",
                        "DISABLE_TUNNEL_AUTOSTART"
                    ]
                    new_lines = []
                    for line in lines:
                        key = line.split("=", 1)[0].strip()
                        if key not in tunnel_keys and not line.strip().startswith("# --- トンネル関連設定 ---"):
                            new_lines.append(line)
                    # 末尾に初期化内容を追加
                    new_lines.append("\n")
                    new_lines.extend(tunnel_init)
                    with open(env_path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    messagebox.showinfo("初期化完了", "トンネル関連設定を初期値で再生成しました。\n\nsettings.envを確認してください。")
            btn = ctk.CTkButton(frame, text="トンネル設定を初期化", font=DEFAULT_FONT, width=200,
                                command=on_reset_tunnel_settings)
            btn.pack(anchor="center")
        else:
            # 想定外の値の場合は空フレーム
            frame = ctk.CTkFrame(self.dynamic_area)
            frame.pack(expand=True, fill="both")
        self.current_frame = frame

    def save_tunnel_service_to_env(self, env_path, service):
        # TUNNEL_SERVICEをsettings.envに保存
        lines = []
        found = False
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if line.strip().startswith("TUNNEL_SERVICE="):
                    lines[i] = f"TUNNEL_SERVICE={service}\n"
                    found = True
                    break
        if not found:
            lines.append(f"TUNNEL_SERVICE={service}\n")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def load_last_service(self):
        # settings.envからTUNNEL_SERVICEを読み込む
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("TUNNEL_SERVICE="):
                        value = line.strip().split("=", 1)[1]
                        # env値→ComboBox値へ変換
                        if value == "cloudflare":
                            self.var_service.set("cloudflare_domain")
                        elif value == "cloudflare_temp":
                            self.var_service.set("cloudflare_tempurl")
                        elif value == "ngrok":
                            self.var_service.set("ngrok")
                        elif value == "localtunnel":
                            self.var_service.set("localtunnel")
                        elif value == "custom":
                            self.var_service.set("custom")
                        elif value == "none":
                            self.var_service.set("none")
                        break

    def after(self, ms, func):
        # afterメソッドのラッパー（CustomTkinterのFrameにafterがない場合用）
        self.master.after(ms, func)

    def pack(self, *args, **kwargs):
        # pack時に前回のサービスを復元し、動的エリアも更新
        self.load_last_service()
        self.on_service_change()
        super().pack(*args, **kwargs)
