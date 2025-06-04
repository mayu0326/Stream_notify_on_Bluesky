## 現在発生している不具合
- Twitchサブスクリプションが作成できない。
>>現時点で外部からの疎通は確認ができている。
>>おそらくevent.pyのTwitchAPIに送るリクエストの内容のバージョン指定句がapp_versionになっていると思われる(正しくはversionである)

### エラーログ
```
2025-06-04 07:59:20,292 [INFO] TwitchAPIアクセストークン取得を確認しました。
2025-06-04 07:59:20,293 [INFO] stream.online のEventSubサブスクリプションを作成します...
2025-06-04 07:59:20,455 [ERROR] EventSubリクエスト: url=https://api.twitch.tv/helix/eventsub/subscriptions headers={'Client-ID': 'u7pf6eb12f9kff5xzln7vppfjwe08w', 'Authorization': 'Bearer ge8czy1dd6bx69sk5j941uxg1d5lgd', 'Content-Type': 'application/json'} payload={'type': 'stream.online', 'app_version': '1', 'condition': {'broadcaster_user_id': '478192219'}, 'transport': {'method': 'webhook', 'callback': 'https://endpoint.mayuneco.net/webhook', 'secret': '77178932db3011a6a6da084b909a380f46cf30f58ab6d6d36b0fa5bbfb8d87eb'}}
2025-06-04 07:59:20,618 [ERROR] EventSubサブスクリプション (stream.online) 作成失敗: HTTPError: Unknown status - N/A 詳細: {}
2025-06-04 07:59:20,618 [CRITICAL] stream.online EventSubサブスクリプションの作成に失敗しました。詳細: {'status': 'error', 'reason': 'HTTPError: Unknown status - N/A', 'details': {}, 'http_status': None}
2025-06-04 07:59:20,618 [CRITICAL] 必須EventSubサブスクリプションの作成に失敗したため、Twitch通知は無効化されます。
```
### GUIの不具合
- YouTube放送終了時にBlueskyへ通知するか(NOTIFY_ON_YOUTUBE_OFFLINE=True)が正しく実装されているか、
調査を行う、実装されていなければ実装が必要である。

-　settings.envがない場合ディレクトリ内に作られるが、
以後そのファイルは使われずdesktopやTempに新たに作られるsettings.envに記録される(ディレクトリ内のファイルが使われるべき)
- GUIからトンネルやサーバーの起動や終了ができない。

#### 修正完了・作業完了済みの不具合リスト

- サービス選択や投稿設定のスイッチが、設定後GUIを再起動するとオフに戻る問題。
>>settings.envのパス指定が相対だと発生する。絶対パス指定が必要。

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
