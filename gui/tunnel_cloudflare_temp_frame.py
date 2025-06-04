# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

Cloudflare Tunnel（trycloudflare.com一時アドレス）専用フレーム
"""

from version_info import __version__
import os
import subprocess
import threading
import customtkinter as ctk
import tkinter.messagebox as messagebox

try:
    import pyperclip
    _pyperclip_available = True
except ImportError:
    _pyperclip_available = False

SETTINGS_ENV_FILE = os.path.join(os.path.dirname(__file__), '../settings.env')

class TunnelCloudflareTempFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.font = ("Yu Gothic UI", 15, "normal")
        self.port = ctk.StringVar(value="5000")
        self.generated_cmd = ctk.StringVar()
        self.url_var = ctk.StringVar(value=self._load_temporary_url())
        self.status_var = ctk.StringVar(value="準備中…")
        self._cf_proc = None
        # --- 中央寄せ用サブフレーム ---
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True, fill="both")
        self._create_widgets(center_frame)
        self._update_cmd()
        self.port.trace_add('write', lambda *a: self._update_cmd())

    def _load_temporary_url(self):
        if not os.path.exists(SETTINGS_ENV_FILE):
            return ""
        with open(SETTINGS_ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('WEBHOOK_CALLBACK_URL_TEMPORARY='):
                    return line.strip().split('=', 1)[1]
        return ""

    def _validate_port(self, value):
        if value == "":
            return True
        return value.isdigit() and len(value) <= 5

    def _create_widgets(self, parent):
        ctk.CTkLabel(parent, text="ポート番号:", font=self.font, anchor="w").grid(row=0, column=0, sticky='w', pady=(10,0), padx=(10,0))
        port_entry = ctk.CTkEntry(parent, textvariable=self.port, font=self.font, width=120)
        port_entry.grid(row=0, column=1, padx=(0,10), pady=(10,0))
        port_entry.configure(validate="key", validatecommand=(self.register(self._validate_port), "%P"))
        ctk.CTkLabel(parent, text="cloudflared起動コマンド:", font=self.font, anchor="w").grid(row=1, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.generated_cmd, font=self.font, width=320, state="readonly").grid(row=1, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkLabel(parent, text="一時公開URL:", font=self.font, anchor="w").grid(row=2, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.url_var, font=self.font, width=320, state="readonly").grid(row=2, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="URLコピー", command=self._copy_url, font=self.font).grid(row=2, column=2, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="保存", command=self._save_cmd, font=self.font).grid(row=3, column=0, pady=(20,0), padx=(10,0), sticky='ew')
        btn_frame = ctk.CTkFrame(parent)
        btn_frame.grid(row=3, column=1, columnspan=2, pady=(20,0), sticky='ew')
        btn_frame.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(btn_frame, text="トンネル開始", command=self._start_cloudflare_temp, font=self.font, width=120).grid(row=0, column=0, padx=10, sticky='ew')
        ctk.CTkButton(btn_frame, text="トンネル停止", command=self._stop_cloudflare_temp, font=self.font, width=120).grid(row=0, column=1, padx=10, sticky='ew')
        ctk.CTkLabel(parent, textvariable=self.status_var, font=self.font, anchor="w").grid(row=4, column=0, columnspan=3, sticky='w', padx=(10,0), pady=(10,0))

    def _update_cmd(self, *args):
        port = self.port.get()
        cmd = f"cloudflared tunnel --url http://localhost:{port}" if port else ""
        self.generated_cmd.set(cmd)

    def _save_cmd(self):
        port_value = self.port.get()
        cmd = self.generated_cmd.get()
        lines = []
        if os.path.exists(SETTINGS_ENV_FILE):
            with open(SETTINGS_ENV_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
        new_lines = []
        found_cmd = found_port = False
        for line in lines:
            if line.startswith('CLOUDFLARE_TEMP_CMD='):
                new_lines.append(f'CLOUDFLARE_TEMP_CMD={cmd}\n')
                found_cmd = True
            elif line.startswith('CLOUDFLARE_TEMP_PORT='):
                new_lines.append(f'CLOUDFLARE_TEMP_PORT={port_value}\n')
                found_port = True
            else:
                new_lines.append(line)
        if not found_cmd:
            new_lines.append(f'CLOUDFLARE_TEMP_CMD={cmd}\n')
        if not found_port:
            new_lines.append(f'CLOUDFLARE_TEMP_PORT={port_value}\n')
        with open(SETTINGS_ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        from gui.app_gui import show_ctk_info
        show_ctk_info(self, "保存完了", "Cloudflare一時トンネルの設定とコマンドが保存されました。")

    def _start_cloudflare_temp(self):
        port = self.port.get()
        if not port:
            from gui.app_gui import show_ctk_error
            show_ctk_error(self, "エラー", "ポート番号を入力してください。")
            return
        self.status_var.set("Cloudflare一時トンネル起動中…")
        self.url_var.set("")
        threading.Thread(target=self._run_cloudflare_temp, args=(port,), daemon=True).start()

    def _run_cloudflare_temp(self, port):
        exe_path = 'cloudflared'  # Pathは環境変数またはフルパス指定で調整可
        cmd = [exe_path, 'tunnel', '--url', f'http://localhost:{port}']
        try:
            self._cf_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if self._cf_proc.stdout is not None:
                for _ in range(30):  # 最大15秒待機
                    line = self._cf_proc.stdout.readline()
                    if not line:
                        continue
                    if 'trycloudflare.com' in line:
                        import re
                        m = re.search(r'(https://[\w\-]+\.trycloudflare\.com)', line)
                        if m:
                            url = m.group(1)
                            self.url_var.set(url)
                            self.status_var.set("Cloudflare一時トンネル稼働中")
                            self._save_temporary_url(url)
                            break
        except Exception as e:
            from gui.app_gui import show_ctk_error
            show_ctk_error(self, "エラー", f"Cloudflare一時トンネルの起動に失敗しました: {e}")

    def _stop_cloudflare_temp(self):
        if self._cf_proc and self._cf_proc.poll() is None:
            self._cf_proc.terminate()
            try:
                self._cf_proc.wait(timeout=5)
                self.status_var.set("Cloudflare一時トンネル停止済み")
            except Exception:
                self._cf_proc.kill()
                self.status_var.set("Cloudflare一時トンネル強制終了")
        else:
            self.status_var.set("Cloudflare一時トンネルは起動していません")
        # 一時URLの値だけ消す（行自体は残す）
        lines = []
        if os.path.exists(SETTINGS_ENV_FILE):
            with open(SETTINGS_ENV_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.startswith('WEBHOOK_CALLBACK_URL_TEMPORARY='):
                new_lines.append('WEBHOOK_CALLBACK_URL_TEMPORARY=\n')
            else:
                new_lines.append(line)
        with open(SETTINGS_ENV_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        self.url_var.set("")

    def _save_temporary_url(self, url):
        lines = []
        if os.path.exists(SETTINGS_ENV_FILE):
            with open(SETTINGS_ENV_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        new_lines = []
        found = False
        for line in lines:
            if line.startswith('WEBHOOK_CALLBACK_URL_TEMPORARY='):
                new_lines.append(f'WEBHOOK_CALLBACK_URL_TEMPORARY={url}\n')
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f'WEBHOOK_CALLBACK_URL_TEMPORARY={url}\n')
        with open(SETTINGS_ENV_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    def _copy_url(self):
        url = self.url_var.get()
        if not url:
            from gui.app_gui import show_ctk_warning
            show_ctk_warning(self, "URL未入力", "公開URLが空です。")
            return
        if _pyperclip_available:
            pyperclip.copy(url)
            from gui.app_gui import show_ctk_info
            show_ctk_info(self, "コピー完了", "公開URLをクリップボードにコピーしました。")
        else:
            from gui.app_gui import show_ctk_warning
            show_ctk_warning(self, "pyperclip未インストール", "pyperclipが未インストールのためコピーできません。\n\n'pip install pyperclip'でインストールしてください。")
