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
from utils import get_settings_env_abspath

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__

"""
初期設定ウィザード
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

DEFAULT_FONT = ("Yu Gothic UI", 12, "normal")

class SetupWizard(ctk.CTkToplevel):
    def __init__(self, master=None, on_finish=None):
        self._after_ids = []  # after用リストを初期化
        super().__init__(master)
        self.title("StreamNotify on Bluesky 初期設定ウィザード")
        self.geometry("500x340")
        self.resizable(False, False)
        self.on_finish = on_finish
        self.current_step = 0
        self.vars = {}
        # 外観モード初期化
        self.appearance_var = tk.StringVar(value="system")
        ctk.set_appearance_mode("system")
        self.steps = [
            self.step_intro,
            self.step_bluesky_account,
            self.step_optional_info,
            self.step_summary
        ]
        self.create_widgets()
        self.show_step(0)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def after(self, ms, func=None, *args):
        # afterをラップしてIDを記録
        after_id = super().after(ms, func, *args)
        self._after_ids.append(after_id)
        return after_id

    def cancel_all_after(self):
        # すべてのafterイベントをキャンセル
        for after_id in getattr(self, '_after_ids', []):
            try:
                super().after_cancel(after_id)
            except Exception:
                pass
        self._after_ids.clear()

    def _on_cancel(self):
        self.cancel_all_after()
        self.destroy()
        import sys
        sys.exit(0)

    def create_widgets(self):
        # 外観モード切替UI（上部に追加）
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=16, pady=(10, 0))
        ctk.CTkLabel(top_frame, text="外観モード:", font=("Yu Gothic UI", 11)).pack(side="left")
        appearance_combo = ctk.CTkComboBox(
            top_frame,
            values=["system", "light", "dark"],
            variable=self.appearance_var,
            width=100,
            font=("Yu Gothic UI", 11),
            command=self.on_appearance_change
        )
        appearance_combo.pack(side="left", padx=(8, 0))
        # メインフレーム
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(side="bottom", pady=16, fill="x")
        self.btn_prev = ctk.CTkButton(self.button_frame, text="前へ", command=self.prev_step, font=DEFAULT_FONT, width=90)
        self.btn_next = ctk.CTkButton(self.button_frame, text="次へ", command=self.next_step, font=DEFAULT_FONT, width=90)
        self.btn_cancel = ctk.CTkButton(self.button_frame, text="キャンセル", command=self._on_cancel, font=DEFAULT_FONT, width=90)
        self.btn_prev.pack(side="left", padx=10)
        self.btn_cancel.pack(side="left", padx=10)
        self.btn_next.pack(side="right", padx=10)

    def on_appearance_change(self, mode):
        ctk.set_appearance_mode(mode)

    def show_step(self, idx):
        # step切り替え前にBlueskyアカウント用StringVarを新しく作り直し、古いバインドを切る
        if hasattr(self, 'entry_bsky_user'):
            try:
                self.entry_bsky_user.destroy()
            except Exception:
                pass
            del self.entry_bsky_user
        if hasattr(self, 'entry_bsky_pass'):
            try:
                self.entry_bsky_pass.destroy()
            except Exception:
                pass
            del self.entry_bsky_pass
        # StringVarも新しく作り直す（trace解除の代用）
        if idx == 1:
            self.vars['bsky_user'] = tk.StringVar()
            self.vars['bsky_pass'] = tk.StringVar()
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.current_step = idx
        self.steps[idx]()
        self.btn_prev.configure(state="normal" if idx > 0 else "disabled")
        if idx == len(self.steps) - 1:
            self.btn_next.configure(text="ファイルを作成")
        else:
            self.btn_next.configure(text="次へ")

    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def next_step(self):
        if not self.validate_step():
            return
        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
        else:
            self.save_settings()

    def step_intro(self):
        ctk.CTkLabel(self.frame, text="StreamNotify on Bluesky 初期設定ウィザード", font=("Yu Gothic UI", 15, "bold")).pack(anchor="w", pady=10)
        ctk.CTkLabel(
            self.frame,
            text="このウィザードでは、最低限必要なBlueskyアカウント情報のみ設定します。\nTwitch/YouTube/ニコニコ/トンネル等は後から設定できます。",
            font=("Yu Gothic UI", 12),
            justify="left",
            wraplength=440
        ).pack(anchor="w", pady=10)
        ctk.CTkLabel(
            self.frame,
            text="※設定内容は後からGUIでいつでも変更可能です。",
            font=("Yu Gothic UI", 11),
            text_color="#888"
        ).pack(anchor="w", pady=4)

    def step_bluesky_account(self):
        ctk.CTkLabel(self.frame, text="Blueskyアカウント設定 (必須)", font=("Yu Gothic UI", 13, "bold")).pack(anchor="w", pady=8)
        self.vars['bsky_user'] = self.vars.get('bsky_user', tk.StringVar())
        self.vars['bsky_pass'] = self.vars.get('bsky_pass', tk.StringVar())
        ctk.CTkLabel(self.frame, text="Blueskyユーザー名", font=DEFAULT_FONT).pack(anchor="w")
        self.entry_bsky_user = ctk.CTkEntry(self.frame, textvariable=self.vars['bsky_user'])
        self.entry_bsky_user.pack(fill="x")
        ctk.CTkLabel(self.frame, text="Blueskyアプリパスワード", font=DEFAULT_FONT).pack(anchor="w", pady=(8,0))
        self.entry_bsky_pass = ctk.CTkEntry(self.frame, textvariable=self.vars['bsky_pass'], show='*')
        self.entry_bsky_pass.pack(fill="x")

    def step_optional_info(self):
        ctk.CTkLabel(self.frame, text="その他の設定について", font=("Yu Gothic UI", 13, "bold")).pack(anchor="w", pady=8)
        ctk.CTkLabel(
            self.frame,
            text="Twitch/YouTube/ニコニコ/トンネル等の設定は、\nメイン画面の[設定]タブからいつでも追加・編集できます。\n\n今はBlueskyアカウントのみで進めます。",
            font=("Yu Gothic UI", 12),
            justify="left",
            wraplength=440
        ).pack(anchor="w", pady=10)

    def step_summary(self):
        ctk.CTkLabel(self.frame, text="セットアップ最終確認", font=("Yu Gothic UI", 13, "bold")).pack(anchor="w", pady=8)
        summary = f"Blueskyユーザー名: {self.vars['bsky_user'].get()}\nBlueskyアプリパスワード: {'*' * len(self.vars['bsky_pass'].get())}"
        ctk.CTkLabel(self.frame, text=summary, font=("Yu Gothic UI", 12), justify="left").pack(anchor="w", pady=10)
        ctk.CTkLabel(self.frame, text="この内容で settings.env を作成します。\n他のサービス設定は後から追加できます。", font=("Yu Gothic UI", 11), text_color="#888").pack(anchor="w", pady=6)

    def validate_step(self):
        if self.current_step == 1:
            # Entryウィジェットが存在しなければバリデーションをスキップ
            if not (hasattr(self, 'entry_bsky_user') and hasattr(self, 'entry_bsky_pass')):
                return False
            try:
                if not (self.entry_bsky_user.winfo_exists() and self.entry_bsky_pass.winfo_exists()):
                    return False
            except Exception:
                return False
            # StringVar.get()も安全に
            try:
                user = self.vars['bsky_user'].get().strip()
            except Exception:
                user = ''
            try:
                pw = self.vars['bsky_pass'].get().strip()
            except Exception:
                pw = ''
            # Blueskyユーザー名: 3文字以上、ドットまたはコロンを含む
            if not user or len(user) < 3 or ('.' not in user and ':' not in user):
                from gui.app_gui import show_ctk_error
                show_ctk_error(self, "入力エラー", "Blueskyユーザー名を正しく入力してください\n(例: your-handle.bsky.social または 独自ドメインID)")
                return False
            # アプリパスワード: xxxx-xxxx-xxxx-xxxx形式
            import re
            if not pw or not re.match(r"^[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$", pw, re.IGNORECASE):
                from gui.app_gui import show_ctk_error
                show_ctk_error(self, "入力エラー", "Blueskyアプリパスワードを正しく入力してください\n(例: xxxx-xxxx-xxxx-xxxx)")
                return False
            # --- APIで有効性チェック ---
            import requests
            try:
                resp = requests.post(
                    "https://bsky.social/xrpc/com.atproto.server.createSession",
                    json={"identifier": user, "password": pw}, timeout=10)
                if resp.status_code == 200 and resp.json().get("accessJwt"):
                    return True
                else:
                    from gui.app_gui import show_ctk_error
                    show_ctk_error(self, "認証エラー", "Blueskyアカウントまたはアプリパスワードが正しくありません。\n公式サイトでご確認ください。")
                    return False
            except Exception as e:
                from gui.app_gui import show_ctk_error
                show_ctk_error(self, "接続エラー", f"Bluesky APIへの接続に失敗しました:\n{e}")
                return False
        return True

    def save_settings(self):
        import re
        v = self.vars
        def getval(key):
            return v[key].get() if key in v else ''
        keymap = {
            'BLUESKY_USERNAME': 'bsky_user',
            'BLUESKY_APP_PASSWORD': 'bsky_pass',
        }
        with open('settings.env.example', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            m = re.match(r'^([A-Z_]+)=', line)
            if m:
                key = m.group(1)
                if key in keymap:
                    val = getval(keymap[key])
                    new_lines.append(f"{key}={val}\n")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        with open(get_settings_env_abspath(), 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        from gui.app_gui import show_ctk_info
        show_ctk_info(self, "完了", "設定ファイルを作成しました。\nメイン画面を開きます")
        self.cancel_all_after()
        self.destroy()
        if self.on_finish:
            self.on_finish()

# ...existing code...
