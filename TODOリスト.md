## 現在発生している不具合

### GUIの不具合

- 設定ファイルがない場合、空ファイルを作って起動してしまう(本来は設定ウィザードが開くはずである)。

### CUIの不具合

- 現在のところ不具合は確認されていません。

### TODO

- pytest実行確認。
- 設定ファイルがない場合の挙動確認。

### 完了済みのTODO

### tunnel_manager.py: 
- グローバルなtunnel_procを管理し、ここで停止処理を行う実装が必要。現状は未実装。
- stop_tunnel関数の適切な場所へのimport

### webhook_routes.py:
- グローバルなtunnel_procを参照し、トンネルの稼働状態を返す実装が必要。現状は仮実装。

### maincontrol_frame.py
- 実際の疎通確認APIを呼ぶ機能が未実装
- サーバー・トンネル・URLの状態を再取得して反映する機能も未実装

#### 修正完了・作業完了済みの不具合リスト

- 設定ファイルがない場合に「設定ファイルがありません」として起動抑止することが実装されていない。
>>[ERROR] 設定ファイルが見つかりません。'settings.env' を作成してください。
と表示し起動抑止を実装。

- GUIで起動時、誤ってCUI側で終了操作(Ctrl+C等)を行った際に出力される以下のログの出力抑制が必要。

- コンソールに出力されるログが２重になっているため、処理が２度呼ばれている
>>configure_logging内で「すでに同種のハンドラが追加されている場合は新たに追加しない」処理を追加する。

- コンソールに本来はログ/コンソール設定が[DEBUG]でないと表示されないはずのログが出ている。

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