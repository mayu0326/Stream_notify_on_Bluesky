## プロジェクトレビュー: Stream notify on Bluesky

### 1. コアアプリケーションロジック

#### main.py
- **役割:** アプリケーションのメインエントリーポイント。全体の機能を調整。
- **機能:**
    - Flaskウェブサーバーを初期化・実行（本番はwaitress）。
    - 設定の読み込み、ロギング設定、設定検証。
    - **settings.envの自動マイグレーション（utils/env_migrator.py）を起動時に必ず実行（ファイルが存在する場合のみ）**。
    - tunnel.py経由でCloudflareやその他のトンネルサービスの開始/停止を管理。
    - Twitch EventSubウェブフックのインタラクション（/webhookエンドポイント: GET=ヘルスチェック, POST=通知）。
    - eventsub.verify_signatureで署名検証。
    - Twitch webhook_callback_verificationチャレンジ処理。
    - stream.online/stream.offlineイベントの処理（詳細抽出→BlueskyPosterでBluesky投稿）。
    - settings.envで各サービスごとの通知ON/OFF・テンプレート・画像パス等を個別管理（Twitch/YouTube/ニコニコ/Bluesky/Discord等）。
    - Twitchからの失効メッセージのロギング。
    - EventSubサブスクリプションの管理（クリーンアップ/作成）。
    - WEBHOOK_SECRETのローテーション。
    - TWITCH_BROADCASTER_IDをユーザーIDから変換して使用。
    - GUI（Tkinter）との連携（settings.env同期・プロセス制御）。
        - GUIからサーバー・トンネルの起動/停止・状態確認・疎通確認（トンネル稼働時のみ有効）が可能。
        - CUI/GUIどちらでも、終了時に必ずクリーンアップ・ログ出力・ファイルロック解放が保証される。
        異常終了時もログが残る。
        - 進捗・ステータス表示やボタン配置は中央・拡張性重視で整理。
- **主要技術:** Flask, Waitress, Tkinter（GUI連携）

#### utils/env_migrator.py
- **役割:** settings.envの自動マイグレーション（不足項目追加・不要項目コメントアウト・バックアップ作成）。
- **機能:**
    - settings.env.example（テンプレート）と現行settings.envを比較し、不足項目を自動追加、不要項目をコメントアウト。
    - バックアップファイル（settings.env.bak）を自動作成。
    - main.py・gui/app_gui.pyの起動時に自動的に呼び出される。
- **主要技術:** Pythonファイル操作、差分検出

#### eventsub.py
- **役割:** Twitch EventSub・API認証管理。
- **機能:**
    - OAuthクライアント認証フローでアクセストークン取得。
    - ユーザー名→ブロードキャスターID変換。
    - HMAC SHA256署名検証（タイムスタンプ検証含む）。
    - EventSubサブスクリプション管理（取得/作成/削除/クリーンアップ）。
    - API呼び出しのリトライ。
    - タイムゾーン管理。
- **主要技術:** Twitch API, HMAC, SHA256

#### bluesky.py
- **役割:** Bluesky連携。
- **機能:**
    - BlueskyPosterクラス: ログイン、画像アップロード、Jinja2テンプレートで通知投稿（オンライン/オフライン/新着動画）。
    - 各サービスごとのテンプレート・画像パス対応（Twitch/YouTube/ニコニコ等）。
    - テンプレートパス未設定・ファイル未存在時はエラーハンドリング（エラーログ＋Discord通知＋投稿中止）。
    - 投稿履歴をlogs/post_history.csvに記録。
    - APIリトライ。
- **主要技術:** atproto, Jinja2

#### tunnel.py
- **役割:** Cloudflare/ngrok/localtunnel/custom 各種トンネルサービスの起動・管理。
- **機能:**
    - start_tunnel(): settings.envのTUNNEL_SERVICEで選択されたサービス\
    （cloudflare/ngrok/localtunnel/custom）に応じて、各種コマンド\
    （TUNNEL_CMD/NGROK_CMD/LOCALTUNNEL_CMD/CUSTOM_TUNNEL_CMD）でトンネルプロセスを起動。
    - stop_tunnel(): プロセスをterminate()→wait()で正常終了、タイムアウト時はkill()で強制終了。\
    例外時もkill()を試みる。
    - ログ出力はlogger引数で指定可能（未指定時は"tunnel.logger"）。
    - コマンド未設定時は警告ログを出し、起動しない。
    - コマンド実行時はshlex.splitで安全に分割し、FileNotFoundErrorや一般例外も個別にログ。
    - TUNNEL_SERVICEが未設定・未知の場合はTUNNEL_CMDを利用。
    - GUIからトンネルの状態確認・疎通確認ボタン（稼働時のみ有効）を実装。
    - 状態表示は色分け（緑=稼働/赤=停止）で統一。
- **主要技術:** subprocess, shlex, logging, 環境変数によるサービス切替

#### utils.py
- **役割:** 共通ユーティリティ。
- **機能:**
    - Jinja2日付フィルタ、.envファイル更新（コメント保持）、リトライデコレータ、シークレット生成、\
    .env読込、シークレットローテーション、URL検証。
    - **utils/ディレクトリ配下に配置され、env_migrator.py等の補助スクリプトも含む。**
- **主要技術:** secrets, datetime, pytz, tzlocal

#### cleanup.py
- **役割:** アプリケーション終了時のクリーンアップ処理・リソース解放。
- **機能:**
    - 一時ファイルやプロセスの後始末。
    - ファイルロックやリソースの安全な解放。
    - 異常終了時も確実にクリーンアップを実施。
- **主要技術:** os, logging

#### service_monitor.py
- **役割:** サービス状態監視・ヘルスチェック。
- **機能:**
    - 各種外部サービスや内部プロセスの稼働状況を定期監視。
    - 異常検知時のログ出力や通知。
- **主要技術:** threading, logging

#### webhook_routes.py
- **役割:** Webhookエンドポイントのルーティング・受信処理。
- **機能:**
    - Flaskアプリのルート定義。
    - Webhookリクエストの受信・検証・分岐処理。
- **主要技術:** Flask

### 2. 設定とセッティング

#### gui/app_gui.py
#### 最新GUI仕様のポイント
- メインコントロールパネルは、サーバー・トンネルの状態表示（色分け）、進捗インジケータ、\
中央配置の操作ボタン（起動/停止/疎通確認/終了）で構成。
- 「疎通確認」ボタンはトンネル稼働時のみ有効。
- ダークモード切替は「オプション」タブ最上部に移動し、その下に拡張用スペースを確保。
- レイアウト・配色・拡張性を重視した設計。
- すべての設定・状態はsettings.envと双方向同期。
- **settings.envの自動マイグレーション（utils/env_migrator.py）を起動時に必ず実行（ファイルが存在する場合のみ）**。
- CUI/GUIどちらでも安全な終了・クリーンアップ・ログ出力が保証される。

#### settings.env / settings.env.example
- **役割:** settings.envは本番用設定ファイル（※配布ファイルには含まれません。初回セットアップまたはウィザードで自動生成）。settings.env.exampleはテンプレート。
- **主要設定:**
    - Twitch: TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_BROADCASTER_ID
    - Bluesky: BLUESKY_USERNAME, BLUESKY_APP_PASSWORD, BLUESKY_IMAGE_PATH, BLUESKY_TEMPLATE_PATH, BLUESKY_OFFLINE_TEMPLATE_PATH, BLUESKY_YT_ONLINE_TEMPLATE_PATH, BLUESKY_YT_OFFLINE_TEMPLATE_PATH, BLUESKY_NICO_ONLINE_TEMPLATE_PATH, BLUESKY_NICO_NEW_VIDEO_TEMPLATE_PATH など
    - YouTube: YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID, YOUTUBE_POLL_INTERVAL, YOUTUBE_POLL_INTERVAL_ONLINE
    - ニコニコ: NICONICO_USER_ID, NICONICO_LIVE_POLL_INTERVAL
    - Webhook: WEBHOOK_SECRET, SECRET_LAST_ROTATED, WEBHOOK_CALLBACK_URL
    - Discord: discord_error_notifier_url, discord_notify_level
    - 一般: TIMEZONE, LOG_LEVEL, LOG_RETENTION_DAYS, APPEARANCE_MODE
    - トンネル: TUNNEL_CMD, TUNNEL_SERVICE など
    - APIリトライ: RETRY_MAX, RETRY_WAIT
- **自動マイグレーション:** settings.envは起動時に自動的に最新仕様へアップデートされる（不足項目追加・不要項目コメントアウト等）。

#### latest_videos.json
- **役割:** YouTube・ニコニコの新着動画・配信の管理用JSONファイル。
- **機能:**
    - 各監視モジュール（youtube_monitor.py, niconico_monitor.py）が新着情報のキャッシュ・差分検出に利用。

#### static/
- **役割:** favicon.ico等の静的ファイル格納ディレクトリ。
- **機能:**
    - Webサーバー（Flask等）で利用される静的リソースを管理。

#### logging_config.py
- **役割:** ロギング設定。
- **機能:**
    - AuditLogger（logs/audit.log）、AppLogger（logs/app.log, logs/error.log, コンソール）。
    - TimedRotatingFileHandlerでローテーション・保持。
    - Discordエラー通知（任意）。
    - Flaskロガー統合。
- **主要ライブラリ:** logging, discord_logging.handler

#### Cloudflared/config.yml.example
- **役割:** cloudflaredの設定例。
- **機能:**
    - トンネルUUID、認証情報、イングレスルール、noTLSVerify。

### 3. サポートファイル・ディレクトリ

- templates/niconico/, templates/twitch/, templates/youtube/: サービスごとのテンプレートサブディレクトリ（__init__.txtはシステム管理用。削除・リネーム厳禁）
- requirements.txt: 依存パッケージ（Flask, requests, atproto, python-dotenv, Jinja2, waitress, pytz, tzlocal, python-logging-discord-handler等）
- development-requirements.txt: 開発用依存（pytest, black, autopep8, pre-commit, ggshield）
- templates/: Bluesky投稿用Jinja2テンプレート（Twitch/YouTube/ニコニコ等サービスごと）
- images/: 投稿用画像（noimage.png等）
- logs/: ログファイル（app.log, error.log, audit.log, post_history.csv）
- **utils/: 共通ユーティリティ・設定マイグレーションスクリプト等を格納するディレクトリ。**
- **static/: favicon.ico等の静的ファイルを格納するディレクトリ。**
- **latest_videos.json: 新着動画・配信の管理用JSONファイル。**
- **settings.env: 本番用設定ファイル（自動マイグレーション対応、※配布ファイルには含まれません。初回セットアップまたはウィザードで自動生成されます）。**

### 4. 開発・CI/CDセットアップ

- .github/: GitHubテンプレート・ワークフロー（バグ報告、GitGuardianシークレットスキャン等）
- .pre-commit-config.yaml: pre-commitフック（ggshield）
- pytest.ini: pytest設定
- tests/: 自動テスト（pytest）

### 5. ドキュメントファイル

- README.md: メインドキュメント（機能・セットアップ・使い方・FAQ・貢献）
- document/CONTRIBUTING.ja.md: 貢献ガイド
- document/comprehensive_summary_japanese.md: 日本語要約
- document/consolidated_summary_japanese.md: 内部メモ・推奨事項
- document/All-ModuleList.md: 全モジュールの一覧リスト
- LICENSE: GPLv2

### 注意事項
- templates/配下の各サブディレクトリ（niconico, twitch, youtube等）には __init__.txt（システム管理用）が必須です。\
削除・リネーム・空ディレクトリ化は動作不良の原因となるため厳禁です。
- テンプレート・画像パスは templates/・images/ 以降の相対パスで管理・指定してください。
- 投稿履歴（logs/post_history.csv）はGUI・CLI共通で参照・管理されます。

### 全体概要

本プロジェクトは、Twitch/YouTube/ニコニコのイベントをBlueskyへ通知するPythonボットで、\
各サービスごとのテンプレート・画像・Webhook・APIキー個別管理、GUI（Tkinter）連携、\
強力なエラーハンドリング、包括的なドキュメント・テストを備え、拡張性・安全性に優れた設計です。


