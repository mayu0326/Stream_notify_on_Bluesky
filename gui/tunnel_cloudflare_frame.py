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

import os
import customtkinter as ctk
import tkinter.messagebox as messagebox
import subprocess
import threading
import time

DEFAULT_FONT = "Yu Gothic UI", 15, "normal"

try:
    import pyperclip
    _pyperclip_available = True
except ImportError:
    _pyperclip_available = False

class TunnelCloudflareFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.font =DEFAULT_FONT
        self.cloudflared_path = ctk.StringVar(value=self._get_default_cloudflared())
        self.config_path = ctk.StringVar(value=self._get_default_config())
        self.tunnel_name = ctk.StringVar(value="my-tunnel")
        self.generated_cmd = ctk.StringVar()
        self.url_var = ctk.StringVar(value=self._load_permanent_url())
        self._load_tunnel_name()
        self._cf_proc = None
        self.status_var = ctk.StringVar(value="停止中")
        # --- 中央寄せ用サブフレーム ---
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(fill="both", expand=True)
        self._create_widgets(center_frame)
        self._update_cmd()

    def _get_default_cloudflared(self):
        default = r"C:/Program Files (x86)/cloudflared/cloudflared.exe"
        return default if os.path.exists(default) else ""

    def _get_default_config(self):
        userprofile = os.environ.get('USERPROFILE', 'C:/Users')
        default = os.path.join(userprofile, '.cloudflared', 'config.yml')
        return default if os.path.exists(default) else ""

    def _load_tunnel_name(self):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        if not os.path.exists(env_path):
            return
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('TUNNEL_NAME='):
                    self.tunnel_name.set(line.strip().split('=', 1)[1])
                    break

    def _load_permanent_url(self):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        if not os.path.exists(env_path):
            return ''
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('WEBHOOK_CALLBACK_URL_PERMANENT='):
                    return line.strip().split('=', 1)[1]
        return ''

    def _create_widgets(self, parent):
        ctk.CTkLabel(parent, text="cloudflared.exeの場所:", font=self.font, anchor="w").grid(row=0, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.cloudflared_path, font=self.font, width=320).grid(row=0, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="参照", command=self._select_cloudflared, font=self.font).grid(row=0, column=2, padx=(0,10), pady=(10,0))
        ctk.CTkLabel(parent, text="config.ymlの場所:", font=self.font, anchor="w").grid(row=1, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.config_path, font=self.font, width=320).grid(row=1, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="参照", command=self._select_config, font=self.font).grid(row=1, column=2, padx=(0,10), pady=(10,0))
        ctk.CTkLabel(parent, text="トンネル名:", font=self.font, anchor="w").grid(row=2, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.tunnel_name, font=self.font, width=320).grid(row=2, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkLabel(parent, text="cloudflared起動コマンド:", font=self.font, anchor="w").grid(row=3, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.generated_cmd, font=self.font, width=320, state="readonly").grid(row=3, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="保存", command=self._save_cmd, font=self.font).grid(row=4, column=1, pady=(20,0))
        # ここからCloudflareトンネル操作UI
        ctk.CTkLabel(parent, text="トンネル状態:", font=self.font).grid(row=5, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkLabel(parent, textvariable=self.status_var, font=self.font).grid(row=5, column=1, sticky='w', pady=(10,0))
        ctk.CTkButton(parent, text="トンネル開始", command=self._start_cloudflare_tunnel, font=self.font).grid(row=6, column=0, pady=(20,0), padx=(10,0))
        ctk.CTkButton(parent, text="トンネル停止", command=self._stop_cloudflare_tunnel, font=self.font).grid(row=6, column=1, pady=(20,0), padx=(10,0))

    def _to_relative_path(self, abspath):
        # プロジェクトルート（settings.envのあるディレクトリ）からの相対パスに変換
        if not abspath:
            return ''
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        try:
            rel = os.path.relpath(abspath, root)
            return rel if not rel.startswith('..') else abspath
        except Exception:
            return abspath

    def _update_cmd(self):
        exe = self.cloudflared_path.get()
        conf = self.config_path.get()
        tunnel = self.tunnel_name.get()
        exe_rel = self._to_relative_path(exe)
        conf_rel = self._to_relative_path(conf)
        # パス区切りをスラッシュに変換
        conf_rel = conf_rel.replace("\\", "/")
        if exe_rel and conf_rel and tunnel:
            cmd = f'cloudflared.exe tunnel --config {conf_rel} run {tunnel}'
            self.generated_cmd.set(cmd)
        else:
            self.generated_cmd.set("")

    def _select_cloudflared(self):
        import tkinter.filedialog as fd
        # cloudflared.exeの現在値があればそのディレクトリ、なければProgram Files等
        current = self.cloudflared_path.get()
        if current and os.path.isfile(current):
            initial_dir = os.path.dirname(current)
        else:
            initial_dir = r"C:/Program Files (x86)/cloudflared"
        path = fd.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("実行ファイル", "*.exe"), ("すべてのファイル", "*.*")],
            title="cloudflared.exeを選択してください"
        )
        if path:
            rel_path = self._to_relative_path(path)
            self.cloudflared_path.set(rel_path)
            self._update_cmd()

    def _select_config(self):
        import tkinter.filedialog as fd
        # config.ymlの現在値があればそのディレクトリ、なければユーザープロファイル配下
        current = self.config_path.get()
        if current and os.path.isfile(current):
            initial_dir = os.path.dirname(current)
        else:
            userprofile = os.environ.get('USERPROFILE', 'C:/Users')
            initial_dir = os.path.join(userprofile, '.cloudflared')
        path = fd.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("YAMLファイル", "*.yml;*.yaml"), ("すべてのファイル", "*.*")],
            title="config.ymlを選択してください"
        )
        if path:
            rel_path = self._to_relative_path(path)
            self.config_path.set(rel_path)
            self._update_cmd()

    def _save_cmd(self):
        self._update_cmd()
        cmd = self.generated_cmd.get()
        tunnel = self.tunnel_name.get()
        url = self.url_var.get()
        if not cmd or not tunnel:
            # messagebox.showerror("エラー", "cloudflared.exe、config.yml、トンネル名を指定してください。")
            from gui.app_gui import show_ctk_error
            show_ctk_error(self, "エラー", "cloudflared.exe、config.yml、トンネル名を指定してください。")
            return
        env_path = 'settings.env'
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        new_lines = []
        found_cmd = found_name = found_url = False
        for line in lines:
            if line.startswith('TUNNEL_CMD='):
                new_lines.append(f'TUNNEL_CMD={cmd}\n')
                found_cmd = True
            elif line.startswith('TUNNEL_NAME='):
                new_lines.append(f'TUNNEL_NAME={tunnel}\n')
                found_name = True
            elif line.startswith('WEBHOOK_CALLBACK_URL_PERMANENT='):
                new_lines.append(f'WEBHOOK_CALLBACK_URL_PERMANENT={url}\n')
                found_url = True
            else:
                new_lines.append(line)
        if not found_cmd:
            new_lines.append(f'TUNNEL_CMD={cmd}\n')
        if not found_name:
            new_lines.append(f'TUNNEL_NAME={tunnel}\n')
        if not found_url:
            new_lines.append(f'WEBHOOK_CALLBACK_URL_PERMANENT={url}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        # messagebox.showinfo("保存完了", "TUNNEL_CMD, TUNNEL_NAME, 公開URLを保存しました。")
        from gui.app_gui import show_ctk_info
        show_ctk_info(self, "保存完了", "TUNNEL_CMD, TUNNEL_NAME, 公開URLを保存しました。")

    def _copy_url(self):
        url = self.url_var.get()
        if not url:
            # messagebox.showwarning("URL未入力", "公開URLが空です。")
            from gui.app_gui import show_ctk_warning
            show_ctk_warning(self, "URL未入力", "公開URLが空です。")
            return
        if _pyperclip_available:
            pyperclip.copy(url)
            # messagebox.showinfo("コピー完了", "公開URLをクリップボードにコピーしました。")
            from gui.app_gui import show_ctk_info
            show_ctk_info(self, "コピー完了", "公開URLをクリップボードにコピーしました。")
        else:
            # messagebox.showwarning("pyperclip未インストール", "pyperclipが未インストールのためコピーできません。\n\n'pip install pyperclip'でインストールしてください。")
            from gui.app_gui import show_ctk_warning
            show_ctk_warning(self, "pyperclip未インストール", "pyperclipが未インストールのためコピーできません。\n\n'pip install pyperclip'でインストールしてください。")

    def _start_cloudflare_tunnel(self):
        exe = self.cloudflared_path.get()
        conf = self.config_path.get()
        tunnel = self.tunnel_name.get()
        # --- 一時URL運用かどうかを判定（tunnel名が空、または"--url"運用時） ---
        use_temporary_url = False
        if tunnel.strip() == '' or tunnel.strip().lower() == 'temporary' or tunnel.strip().startswith('--url'):
            use_temporary_url = True
        # --- コマンド生成 ---
        exe_path = exe if os.path.isabs(exe) else os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', exe))
        conf_path = conf if os.path.isabs(conf) else os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', conf))
        if use_temporary_url:
            # 例: cloudflared tunnel --url http://localhost:5000
            # ポート番号はconfigやUIから取得するのが理想だが、ここでは5000を仮定
            port = 5000
            cmd = [exe_path, 'tunnel', '--url', f'http://localhost:{port}']
        else:
            cmd = [exe_path, 'tunnel', '--config', conf_path, 'run', tunnel]
        try:
            self.status_var.set("Cloudflare Tunnel起動中…")
            self._cf_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if use_temporary_url:
                # stdoutから一時URLを抽出
                url = ''
                for _ in range(30):  # 最大15秒待機
                    if self._cf_proc.stdout:
                        line = self._cf_proc.stdout.readline()
                        if not line:
                            time.sleep(0.5)
                            continue
                        if 'trycloudflare.com' in line:
                            import re
                            m = re.search(r'(https://[\w\-]+\.trycloudflare\.com)', line)
                            if m:
                                url = m.group(1)
                                break
                    time.sleep(0.5)
                if url:
                    self._save_temporary_url(url)
                    self.url_var.set(url)
                    self.status_var.set("Cloudflare Tunnel稼働中")
                else:
                    # 一時URL取得失敗時はPERMANENT欄の値を流用
                    url = self.url_var.get()
                    self._save_temporary_url(url)
                    self.status_var.set("一時URL取得失敗/PERMANENT反映")
            else:
                # 通常運用（恒久URL）
                url = self.url_var.get()
                self._save_temporary_url(url)
                self.status_var.set("Cloudflare Tunnel稼働中")
        except Exception as e:
            from gui.app_gui import show_ctk_error
            show_ctk_error(self, "エラー", f"Cloudflare Tunnelの起動に失敗しました: {e}")
            self.status_var.set("起動エラー")

    def _stop_cloudflare_tunnel(self):
        if self._cf_proc and self._cf_proc.poll() is None:
            self._cf_proc.terminate()
            try:
                self._cf_proc.wait(timeout=5)
                self.status_var.set("Cloudflare Tunnel停止済み")
            except Exception:
                self._cf_proc.kill()
                self.status_var.set("Cloudflare Tunnel強制終了")
        else:
            self.status_var.set("Cloudflare Tunnelは起動していません")
        # 一時URLの値だけ消す（行自体は残す）
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.startswith('WEBHOOK_CALLBACK_URL_TEMPORARY='):
                new_lines.append('WEBHOOK_CALLBACK_URL_TEMPORARY=\n')
            else:
                new_lines.append(line)
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        self.url_var.set("")

    def _save_temporary_url(self, url):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
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
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
