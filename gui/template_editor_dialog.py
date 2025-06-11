# -*- coding: utf-8 -*-
"""
テンプレート編集用ダイアログ（プレビュー付き・利用可能変数制限）
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
from tkinter import filedialog

DEFAULT_FONT = ("Yu Gothic UI", 12, "normal")

# サンプル event_context（サービス・通知種別ごとに適宜拡張）
SAMPLE_CONTEXT = {
    "twitch_online": {
        "language": "日本語(japanese)",
        "user_name": "hogehoge",
        "title": "テスト配信",
        "game_name": "ゲームタイトル",
        "url": "https://twitch.tv/sample",
    },
    "yt_online": {
        "channel_name": "YouTubeチャンネル名",
        "channel_url": "https://youtube.com/channel/xxxx",
        "title": "YouTube配信タイトル",
        "url": "https://youtube.com/live/xxxx",
    },
    "yt_new_video": {
        "title": "新作動画タイトル",
        "video_id": "abcd1234",
        "video_url": "https://youtube.com/watch?v=abcd1234",
        "channel_name": "YouTubeチャンネル名",
    },
    "niconico_online": {
        "broadcaster_user_name": "ニコニコ配信者",
        "title": "ニコ生テスト配信",
        "start_time": "2025-06-02 20:00",
        "stream_url": "https://live.nicovideo.jp/watch/lv123456789",
        "author": "投稿者名サンプル",
        "published": "2025-06-02 20:00:00",
    },
    "niconico_new_video": {
        "title": "新作ニコニコ動画",
        "video_url": "https://www.nicovideo.jp/watch/sm12345678",
        "author": "動画投稿者サンプル",
        "published": "2025-06-01 19:00:00",
    },
}
# 除外リスト
TEMPLATE_VAR_BLACKLIST = {
    "twitch_online": {"broadcaster_user_id", "game_id", "started_at", "type", "is_mature", "tags"},
    "yt_online": {"channel_id", "channel_name", "thumbnail_url", "description", "start_time"},
}
# --- テンプレート引数（日本語ラベル付きボタン群）定義 ---
TEMPLATE_ARGS = {
    "twitch_online": [
        ("配信者名", "broadcaster_user_name"),
        ("タイトル", "title"),
        ("カテゴリ", "category_name"),
        ("ゲーム名", "game_name"),
        ("言語", "language"),
        ("URL", "stream_url"),
    ],
    "twitch_offline": [
        ("配信者名", "broadcaster_user_name"),
        ("URL", "stream_url"),
    ],
    # --- YouTube用を追加 ---
    "yt_online": [
        ("チャンネル名", "broadcaster_user_name"),
        ("配信タイトル", "title"),
        ("配信URL", "stream_url"),
        ("チャンネルURL", "channel_url"),
    ],
    "yt_offline": [
        ("チャンネル名", "channel_name"),
        ("配信タイトル", "title"),
        ("配信URL", "stream_url"),
        ("チャンネルURL", "channel_url"),
    ],
    "yt_new_video": [
        ("動画タイトル", "title"),
        ("動画ID", "video_id"),
        ("動画URL", "video_url"),
        ("チャンネル名", "channel_name"),
    ],
    # --- ニコニコ用を追加 ---
    "niconico_online": [
        ("放送者", "broadcaster_user_name"),
        ("タイトル", "title"),
        ("開始日時", "start_time"),
        ("視聴URL", "stream_url"),
        ("投稿者名", "author"),
        ("投稿日時", "published"),
    ],
    "niconico_new_video": [
        ("動画タイトル", "title"),
        ("動画URL", "video_url"),
        ("投稿者名", "author"),
        ("投稿日時", "published"),
    ],
}
# --- サービスごとのテンプレートサブフォルダ定義 ---
TEMPLATE_SUBFOLDER = {
    "twitch_online": "twitch",
    "yt_online": "youtube",
    "niconico_online": "niconico",
}

class TemplateEditorDialog(ctk.CTkToplevel):
    def __init__(self, master, template_type="twitch_online", initial_text="", on_save=None, initial_path=None):
        super().__init__(master)
        self.title("テンプレート編集")
        self.geometry("600x540")
        self.resizable(False, False)
        self.template_type = template_type
        self.on_save = on_save
        self.file_path = initial_path
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        # --- 追加: 前面に出す ---
        self.lift()
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
        # --- 追加: 縦幅拡大 ---
        self.geometry("600x700")

        # ファイル名表示
        self.file_label = ctk.CTkLabel(self, text=self._get_file_label(), font=("Yu Gothic UI", 12, "italic"))
        self.file_label.pack(anchor="w", padx=16, pady=(8, 0))

        # テンプレート編集欄（スクロールバー付き）
        text_frame = ctk.CTkFrame(self)
        text_frame.pack(fill="x", padx=16, pady=(8, 4))
        self.text_area = tk.Text(text_frame, font=("Consolas", 13), height=8, wrap="word")
        yscroll = tk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=yscroll.set)
        self.text_area.pack(side="left", fill="x", expand=True)
        yscroll.pack(side="right", fill="y")

        # テンプレート引数（日本語ラベルのみのボタン群）
        args_frame = ctk.CTkFrame(self)
        args_frame.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(args_frame, text="テンプレート引数:", font=DEFAULT_FONT).pack(anchor="w")
        btns_frame = ctk.CTkFrame(args_frame)
        btns_frame.pack(fill="x", pady=(2, 2))
        # 重複を除外して順番通りにボタンを表示
        seen = set()
        for label, key in TEMPLATE_ARGS.get(self.template_type, []):
            if key in seen:
                continue
            seen.add(key)
            btn = ctk.CTkButton(btns_frame, text=label, font=("Yu Gothic UI", 13), width=90,
                                command=lambda k=key: self.insert_arg(k))
            btn.pack(side="left", padx=4, pady=2)

        # プレビュー欄（スクロールバー付き）
        ctk.CTkLabel(self, text="プレビュー:", font=DEFAULT_FONT).pack(anchor="w", padx=16)
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="both", padx=16, pady=(0, 8), expand=True)
        preview_canvas = tk.Canvas(preview_frame, bg="#f0f0f0", highlightthickness=0)
        preview_yscroll = tk.Scrollbar(preview_frame, orient="vertical", command=preview_canvas.yview)
        preview_canvas.configure(yscrollcommand=preview_yscroll.set)
        preview_canvas.pack(side="left", fill="both", expand=True)
        preview_yscroll.pack(side="right", fill="y")
        self.preview_label = tk.Label(preview_canvas, text="", font=("Yu Gothic UI", 13), bg="#f0f0f0", anchor="w", justify="left", wraplength=560)
        self.preview_label_id = preview_canvas.create_window((0, 0), window=self.preview_label, anchor="nw")
        def _on_preview_configure(event):
            preview_canvas.configure(scrollregion=preview_canvas.bbox("all"))
        self.preview_label.bind("<Configure>", _on_preview_configure)
        self.update_preview()

        # ボタン
        frame_btn = ctk.CTkFrame(self)
        frame_btn.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkButton(frame_btn, text="開く", command=self.on_open, font=DEFAULT_FONT, width=90).pack(side="left", padx=(0, 8))
        ctk.CTkButton(frame_btn, text="保存", command=self.on_save_click, font=DEFAULT_FONT, width=90).pack(side="left", padx=(0, 8))
        ctk.CTkButton(frame_btn, text="名前を付けて保存", command=self.on_saveas, font=DEFAULT_FONT, width=140).pack(side="left", padx=(0, 8))
        ctk.CTkButton(frame_btn, text="キャンセル", command=self.on_cancel, font=DEFAULT_FONT, width=90).pack(side="left")

    def _get_file_label(self):
        # ファイル名以外（特にテンプレート本文）は絶対にセットしないこと
        return f"ファイル: {os.path.basename(self.file_path) if self.file_path else '(未保存)'}"

    def get_template_dir(self):
        sub = TEMPLATE_SUBFOLDER.get(self.template_type, "")
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
        if sub:
            path = os.path.join(base, sub)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            return path
        return base

    def on_open(self):
        path = filedialog.askopenfilename(
            title="テンプレートファイルを開く",
            filetypes=[("Text files", "*.txt")],
            initialdir=self.get_template_dir()
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", text)
                self.file_path = path
                self.file_label.configure(text=self._get_file_label())  # ファイル名のみ表示
                self.update_preview()
                # --- 追加: ファイルを開いた後も前面に出す ---
                self.lift()
                self.attributes('-topmost', True)
                self.after(100, lambda: self.attributes('-topmost', False))
            except Exception as e:
                messagebox.showerror("ファイル読み込みエラー", str(e))

    def get_available_vars(self):
        ctx = SAMPLE_CONTEXT.get(self.template_type, {})
        blacklist = TEMPLATE_VAR_BLACKLIST.get(self.template_type, set())
        return [k for k in ctx.keys() if k not in blacklist]

    def insert_var(self, event):
        sel = self.var_listbox.curselection()
        if sel:
            var = self.var_listbox.get(sel[0])
            self.text_area.insert(tk.INSERT, var)
            self.update_preview()

    def insert_arg(self, key):
        self.text_area.insert(tk.INSERT, f"{{{key}}}")
        self.update_preview()

    def update_preview(self, event=None):
        tpl = self.text_area.get("1.0", tk.END).strip()
        ctx = SAMPLE_CONTEXT.get(self.template_type, {})
        try:
            preview = tpl.format(**ctx)
            self.preview_label.config(text=preview, fg="#222")
        except KeyError as e:
            self.preview_label.config(text=f"[エラー] 未定義の変数: {e}", fg="#d32f2f")
        except Exception as e:
            self.preview_label.config(text=f"[エラー] {e}", fg="#d32f2f")

    def on_save_click(self):
        tpl = self.text_area.get("1.0", tk.END).strip()
        blacklist = TEMPLATE_VAR_BLACKLIST.get(self.template_type, set())
        for b in blacklist:
            if "{" + b + "}" in tpl:
                messagebox.showerror("禁止変数", f"禁止された変数 '{{{b}}}' が含まれています。テンプレートから削除してください。")
                return
        if self.file_path:
            try:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(tpl)
                messagebox.showinfo("保存完了", f"{os.path.basename(self.file_path)} に保存しました。")
            except Exception as e:
                messagebox.showerror("保存エラー", str(e))
                return
        if self.on_save:
            self.on_save(self.file_path)  # ファイルパスを渡す
        self.destroy()

    def on_saveas(self):
        path = filedialog.asksaveasfilename(
            title="名前を付けて保存",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialdir=self.get_template_dir()
        )
        if path:
            tpl = self.text_area.get("1.0", tk.END).strip()
            blacklist = TEMPLATE_VAR_BLACKLIST.get(self.template_type, set())
            for b in blacklist:
                if "{" + b + "}" in tpl:
                    messagebox.showerror("禁止変数", f"禁止された変数 '{{{b}}}' が含まれています。テンプレートから削除してください。")
                    return
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(tpl)
                self.file_path = path
                self.file_label.configure(text=self._get_file_label())  # ファイル名のみ表示
                messagebox.showinfo("保存完了", f"{os.path.basename(path)} に保存しました。")
                if self.on_save:
                    self.on_save(self.file_path)  # ファイルパスを渡す
                self.destroy()
            except Exception as e:
                messagebox.showerror("保存エラー", str(e))

    def on_cancel(self):
        self.destroy()
