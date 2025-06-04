## 現在発生している不具合

### GUIの不具合

- 現在のところ不具合は確認されていません。

### CUIの不具合

- GUIからトンネルやサーバーの起動や終了ができない。
>>起動はできるようになったが、以下の不具合がある
- コンソールに本来はログ/コンソール設定が[DEBUG]でないと表示されないはずのログが出ているので,、
適切なレベルのときだけ表示されるように修正が必要。

当該ログ
```
2025-06-04 10:07:36,621 [ERROR] EventSubリクエスト: url=https://api.twitch.tv/helix/eventsub/subscriptions headers={'Client-ID': 'u7pf6eb12f9kff5xzln7vppfjwe08w', 'Authorization': 'Bearer 4on2v6jofjlxha2vfb455dmrfhr01t', 'Content-Type': 'application/json'} payload={'type': 'stream.offline', 'version': '1', 'condition': {'broadcaster_user_id': '478192219'}, 'transport': {'method': 'webhook', 'callback': 'https://endpoint.mayuneco.net/webhook', 'secret': '77178932db3011a6a6da084b909a380f46cf30f58ab6d6d36b0fa5bbfb8d87eb'}}
```

- コンソールに出力されるログが２重になっているため、処理が２度呼ばれているかどこかに不具合がある可能性がある、
調査と修正が必要

- GUIで起動時、誤ってコマンドプロンプトで終了操作(Ctrl+C等)を行った際の、
以下のログの出力抑制が必要。
```
Traceback (most recent call last):
  File "D:\Documents\StreamNotify_on_Bluesky_dev\gui\app_gui.py", line 285, in <module>
    MainWindow().mainloop()
    ~~~~~~~~~~~~~~~~~~~~~^^
  File "D:\Documents\StreamNotify_on_Bluesky_dev\.venv\Lib\site-packages\customtkinter\windows\ctk_tk.py", line 165, in mainloop
    super().mainloop(*args, **kwargs)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.1008.0_x64__qbz5n2kfra8p0\Lib\tkinter\__init__.py", line 1599, in mainloop
    self.tk.mainloop(n)
    ~~~~~~~~~~~~~~~~^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.1008.0_x64__qbz5n2kfra8p0\Lib\tkinter\__init__.py", line 2063, in __call__
    def __call__(self, *args):

KeyboardInterrupt
```

### TODO
### tunnel_manager.py: 
- グローバルなtunnel_procを管理し、ここで停止処理を行う実装が必要。現状は未実装。
- stop_tunnel関数の適切な場所へのimport

### webhook_routes.py:
- グローバルなtunnel_procを参照し、トンネルの稼働状態を返す実装が必要。現状は仮実装。

### maincontrol_frame.py
- 実際の疎通確認APIを呼ぶ機能が未実装
- サーバー・トンネル・URLの状態を再取得して反映する機能も未実装

### 記載外だが全体のTODO
## BLUESKY_TEMPLATE_PATH,BLUESKY_OFFLINE_TEMPLATE_PATH
- これは現仕様に即していないので、定義名を更新する必要がある。
そのためこの名前を使ってるもの(大文字・小文字どちらも)を調査し以下に変更する必要がある。
- BLUESKY_TEMPLATE_PATH　→　BLUESKY_TW_ONLINE_TEMPLATE_PATH
- BLUESKY_OFFLINE_TEMPLATE_PATH → BLUESKY_TW_OFFLINE_TEMPLATE_PATH

- 従来のBLUESKY_TEMPLATE_PATH,BLUESKY_OFFLINE_TEMPLATE_PATHは、
pytestやデフォルトフォールバック時のテンプレート
(内部仕様のため設定ファイルに使うのは適切でない)用の関数として使うことが望ましい。


#### 修正完了・作業完了済みの不具合リスト

- アカウントタブ＞YouTubeにおいて、ポーリング間隔の設定が１種類しかない。

- ログビューアがログを読み込めない。

- GUIからトンネルやサーバーの起動や終了ができない。
>>トンネル状態表示は停止のままであったがこれは設定ファイルの項目重複による不具合であったため修正済み

-- サーバー停止は以下のエラーにより失敗しているため調査と修正が必要
[ERROR] サーバー停止失敗: module 'main' has no attribute 'stop_cherrypy_server'
>>main.pyに適切な処理を追加し修正完了。

- Twitchサブスクリプションが作成できない。
>>event.pyのTwitchAPIに送るリクエストの内容のバージョン指定句をapp_versionからversionに変更
>>上記修正後main.py直接起動でEventサブスクリプションが正常に作成できている事を確認済み。

- YouTube放送終了時にBlueskyへ通知するか(NOTIFY_ON_YOUTUBE_OFFLINE=True)が正しく実装されているか、
調査を行う、実装されていなければ実装が必要である。

- YouTube放送終了時にBlueskyへ通知する(Bluesky投稿設定＞YouTubeタブ)が、
設定ファイルがTrueでもスイッチがオフになる(オンにして再起動してもオフに戻る)

- サービス選択や投稿設定のスイッチが、設定後GUIを再起動するとオフに戻る問題。
>>settings.envのパス指定が相対だと発生する。絶対パス指定が必要。

- settings.envがない場合ディレクトリ内に作られるが、
以後そのファイルは使われずdesktopやTempに新たに作られるsettings.envに記録される(ディレクトリ内のファイルが使われるべき)

- トンネル設定タブ＞トンネルサービスをnoneにして設定を初期化すると設定項目ごと消える（本来はラベルは消えず項目だけ消す）
- 本来の初期化後のsettings.envのトンネル関連設定が目指すべき内容は以下である

当該項目(抜粋)

```
# --- トンネル関連設定 ---
# Cloudflare Tunnelなどのトンネルを起動するコマンド 
# 設定しない場合はトンネルを起動しません。
TUNNEL_SERVICE=none
DISABLE_TUNNEL_AUTOSTART=false
TUNNEL_CMD=
TUNNEL_NAME=
CLOUDFLARE_TEMP_CMD=
CLOUDFLARE_TEMP_PORT=
NGROK_CMD=
NGROK_PORT=
NGROK_PROTOCOL=
LOCALTUNNEL_PORT=
LOCALTUNNEL_CMD=
CUSTOM_TUNNEL_CMD=

```