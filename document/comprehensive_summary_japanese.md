## アプリケーション概要
このアプリケーションは、Twitch/YouTube/ニコニコの配信開始・新着動画投稿を自動検知し、リアルタイムでBlueskyに通知を投稿するPythonボットです。\
Twitch EventSubウェブフックやYouTube/Niconicoの監視機能を利用し、Cloudflare Tunnelやngrok/localtunnel/customトンネルを使ってローカル環境でもWebhookを受信できます。\
GUI（Tkinter）による設定・管理にも対応し、各種設定の自動反映や保存完了メッセージ表示など、ユーザビリティも強化されています。

【主なファイル構成のポイント】
- settings.env.example（テンプレート）…配布ファイルに含まれる。\
- settings.env（本番用設定ファイル）…配布ファイルには含まれず、初回セットアップまたはウィザードで自動生成。\
  - 起動時にutils/env_migrator.pyによる自動マイグレーション（不足項目追加・不要項目コメントアウト等）が行われる。
- latest_videos.json … 新着動画・配信の管理用キャッシュファイル。
- static/ … favicon.ico等の静的ファイル格納ディレクトリ。

## 主な機能
*   **Twitch/YouTube/ニコニコ連携:** 各サービスの配信開始・新着動画投稿を自動検知し、Blueskyへ通知（配信終了通知はニコニコ生放送のみ非対応）。
*   **Bluesky通知:** サービスごとにカスタマイズ可能なテンプレート・画像でBlueskyに投稿。テンプレート・画像・Webhook・APIキー等は各サービスごとに個別管理可能。
    * テンプレート・画像パスは `templates/`・`images/` 以降の相対パスで保存・管理。
*   **トンネル機能:** Cloudflare Tunnel/ngrok/localtunnel/customコマンドに対応し、TUNNEL_SERVICE環境変数でサービスを切り替え、\
各種コマンドでトンネルの自動起動・監視・URL自動反映・再接続を実装。WebhookコールバックURLは恒久用/一時用を自動切替。コマンド未設定時は警告ログを出し、起動しない。\
終了時はterminate/waitで正常終了、タイムアウトや例外時はkillで強制終了し、詳細なログを出力。
*   **GUI管理:** TkinterベースのGUIで、settings.envと双方向連携し、各種設定・テンプレート・画像・Webhook・APIキー等を統合管理。タブ構成・レイアウト・UI/UX改善済み。\
保存時は完了メッセージを表示し、タブ切替時に最新設定を自動反映。メイン機能やトンネル等もGUIから起動可能。
    * **GUIからサーバー・トンネルの起動/停止・状態確認・安全な終了・クリーンアップが可能です。**
    * **CUI/GUIどちらでも、終了時に必ずクリーンアップ・ログ出力・ファイルロック解放が保証されます。異常終了時もログが残ります。**
*   **設定:** settings.envファイルでAPIキー、通知ON/OFF、テンプレート・画像パス、Discord Webhook、ログレベル等を柔軟にカスタマイズ。
*   **エラー処理とロギング:**
    * 重大なエラー時のDiscord通知
    * APIエラーの自動リトライ（回数・待機時間は設定可能）
    * アプリケーションアクティビティの包括的なロギング
    * Bluesky投稿履歴（logs/post_history.csv）
    * 監査ログ（logs/audit.log）
    * テンプレート・画像パス未設定・ファイル未存在時はエラーハンドリング（エラーログ＋Discord通知＋投稿中止）
*   **サブスクリプション管理:** 不要なTwitch EventSubサブスクリプションの自動クリーンアップ。
*   **セキュリティ:** Webhook署名検証によるリプレイ攻撃対策、WEBHOOK_SECRETの自動ローテーション。

*   **YouTubeチャンネルID仕様:**
    * **YouTube APIキー未設定時**は、UCから始まるチャンネルID（例: UCxxxx...）のみ**通知対象として許可**されます。
    * APIキーを設定した場合は、**カスタムIDや@ハンドル形式**も利用可能です。
    * GUI・CLIともに、**APIキー未入力時はUC形式ID以外**は保存・起動できません。

*   **機密ファイル管理:**
    * `settings.env`や`settings.env.bak`等の**機密ファイル**は、`.gitignore`で必ず除外し、**Git履歴にも残さない運用**としてください。
    * `settings.env.bak`等を誤ってコミットした場合は、`git filter-repo`等で**履歴から完全削除してください**。
    * `settings.env.example`のみ**配布・共有可能**です。

*   **テンプレート・画像パス命名規則:**
    * パスは必ず`templates/`・`images/`以降の相対パスで指定してください。**絶対パスやプロジェクトルートから**のパスは非推奨です。
    * Bluesky通知テンプレートのパス（例: `BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH`）は、サービスごとに個別に設定できます。

*   **settings.env自動マイグレーション:**
    * 起動時に`utils/env_migrator.py`が自動で**不足項目の追加・不要項目のコメントアウト**等を行い、常に最新仕様に保ちます。
    * 手動編集時も、次回起動時に自動で整合性が取られます。

*   **.gitignore運用:**
    * 機密ファイル（`settings.env`,`settings.env.bak`,`logs/`等）は必ず`.gitignore`で除外してください。
    * 配布・共有時は`settings.env.example`のみ含めてください。

## 使用されている主要なテクノロジー
*   Python（コア言語）
*   Flask（Webhook用Webフレームワーク）
*   Tkinter（GUI）
*   Twitch/YouTube/Niconico API
*   Bluesky API
*   Cloudflare Tunnel/ngrok/localtunnel/custom
*   Discord API（Webhook）
*   Git（バージョン管理）
*   pytest（自動テスト）
*   CSV（投稿履歴ロギング用）
*   YAML（Cloudflare Tunnel設定用）
*   .envファイル（設定管理用）

## セットアップ方法
1. リポジトリをクローンし、`pip install -r requirements.txt`で必要なPythonパッケージをインストール。
2. Cloudflare Tunnel（cloudflared）やngrok/localtunnel等をインストールし、必要に応じてconfig.ymlやコマンドを設定。
3. `settings.env.example`をコピーして`settings.env`を作成し、以下を記入：
    * 各サービスのAPIキー・ユーザーID
    * Blueskyの画像/テンプレートパス（各サービスごとに個別指定可能。`templates/`・`images/`以降の相対パスで記載）
    * Discord Webhook URL
    * ログレベル等
    * トンネルコマンド・WebhookコールバックURL（恒久用/一時用）
    - ※settings.envは配布ファイルに含まれません。初回セットアップ時やGUIウィザードで自動生成されます。
    - ※起動時に自動マイグレーション（utils/env_migrator.py）が実行され、常に最新仕様に保たれます。
4. 必要に応じてGUI（`python gui/app_gui.py`）で設定・管理。
    * GUIではテンプレート・画像・Webhook・APIキー等を直感的に編集可能。
    * 設定保存時は完了メッセージが表示され、タブ切替時に最新設定が自動反映されます。
5. ボットは`python main.py`で起動。通知レベルやテンプレート切り替え等はsettings.envまたはGUIから管理。

### 注意事項
- `templates/`配下の各サブディレクトリ（niconico, twitch, youtube等）には `__init__.txt`（システム管理用）が必須です。\
削除・リネーム・空ディレクトリ化は動作不良の原因となるため厳禁です。
- テンプレート・画像パスは `templates/`,`images/`以降の相対パスで管理・指定してください。
- 投稿履歴（`logs/post_history.csv`）はGUI・CLI共通で参照・管理されます。
- YouTubeチャンネルIDは、APIキー未設定時はUC形式ID（UCxxxx...）のみ許可されます。APIキー設定時はカスタムIDや@ハンドルも利用可能です。
- `settings.env`や`settings.env.bak`等の**機密ファイル**は、`.gitignore`で除外し、**Git履歴にも残さないよう厳重に管理**してください。
- `settings.env`は**配布・共有禁止**、`settings.env.example`のみ配布可です。
- テンプレート・画像パスは必ず`templates/`,`images/`以降の相対パスで指定してください。
- `settings.env`は起動時に自動マイグレーションされ、常に最新仕様に保たれます。
