# Stream notify on Bluesky

- Twitch/YouTube/ニコニコ生放送の放送開始を自動検知し、\
Bluesky へリアルタイムにお知らせ投稿する Python 製 Bot です。
- Youtubeとニコニコについては、放送だけでなく動画投稿の通知にも対応します。    
- Cloudflare Tunnel または他のトンネル通信アプリケーション(ngrok,localtunnel)による、\
Webhook 受信、エラー通知、履歴記録など運用に便利な機能を多数備えています。
- **GUI（設定アプリ）**からもサーバー・トンネルの起動/停止・状態確認・安全な終了が可能
- **CUI（main.py）/GUI**どちらからでもCtrl+Cや停止ボタンで安全にクリーンアップ・ログ出力・ファイルロック解放

---

## 主な特徴
### 基本機能
- **Twitch EventSub Webhook**で放送開始/終了を自動検知
- 不要な**Twitch EventSub サブスクリプション**の自動クリーンアップ
- **YouTubeLive**の放送開始・終了の検知に対応
- **ニコニコ生放送**の放送開始の検知に対応(終了検知はニコニコの仕様上非対応)
- **Youtube動画/ニコニコ動画**のアップロード検知(App起動後の新着のみ)に対応
- **トンネル通信アプリケーション** でローカル環境でもWebhook 受信
- **トンネル通信アプリケーションの自動起動・URL自動反映・GUI連携**
- **TwitchEventsub設定/WebhookURLタブ分離・自動反映**
- **設定ファイル**で設定を細かくカスタマイズ可能
- **Discord へのエラー通知**・通知レベルの管理や機能オフも可能
- **ログファイル・コンソール出力**のログレベルは設定ファイルで調整可能
- **APIエラー時**の自動リトライ機能(回数や間隔も調整可能)

### 投稿関連
- **Bluesky**へ自動で放送開始/終了通知を投稿(各サービスごとに個別On/Off可能)
- **Bluesky**へ投稿する内容は各サービスごとにテンプレートで切り替え可能
- **Bluesky**へ投稿するとき特定の画像を添付することも可能
- **Bluesky**投稿した内容をCSVで投稿履歴として記録
- **投稿テンプレート**の作成と編集もGUIから可能

### 安全・保守機能
- **Webhook署名**のタイムスタンプ検証による**リプレイ攻撃対策**
- **監査ログ**の保存機能を実装しているので、操作履歴の確認に活用可能
- **自動テスト**機能による品質管理を実装（tests/ディレクトリ）

- 拡張性・保守性を考慮したモジュール分割設計

---

## 必要な環境
### パソコン環境
- Windows10以降（11を推奨）\
**※このアプリケーションはWindows専用です**\
**※LinuxやMacには対応していません。**
- Python 3.13 以上 推奨
- Git 2.49 以上 推奨
- Cloudflared(CloudflareTunnel)または\
他のトンネル通信アプリケーション(ngrok,localtunnel)のいずれかの事前インストール必須

### アカウント関連
- Twitch のユーザーID（EventSub 用）
- Twitch APIのクライアントIDとクライアントシークレット(デベロッパーコンソールから取得)
- Bluesky アカウント（投稿用）
- Cloudflareのアカウント（Cloudflare利用時のみ）
- ngrokのアカウント(ngrok利用時のみ)

### その他に必要なもの
- CloudflareでDNS管理されている独自ドメイン（推奨）\
または(ngrokやlocaltunnelなど)他のトンネル通信アプリケーション

---

## トンネル要件 / Tunnel Requirements

本アプリケーションはCloudflare Tunnel「のみ」対応ではありません。\
ngrok、localtunnel、カスタムトンネルもサポートされています。

- `TUNNEL_SERVICE`環境変数でサービスを切り替え、各種コマンド\
（`TUNNEL_CMD`/`NGROK_CMD`/`LOCALTUNNEL_CMD`/`CUSTOM_TUNNEL_CMD`）でトンネルを起動・管理します。
- コマンド未設定時は警告ログを出し、トンネルは起動しません。\
終了時はterminate/waitで正常終了、タイムアウトや例外時はkillで強制終了し、\
詳細なログを出力します。
- Cloudflare Tunnel利用時は**Cloudflare Zero Trust**でトンネル作成・`config.yml`準備が必要です。
  - Cloudflare Tunnelは「独自ドメイン用」と「一時アドレス(trycloudflare.com)用」で\
     設定・画面が分かれています。
  - 「Cloudflare(独自ドメイン)」はZero Trust管理画面でトンネル・ドメインを発行し、\
     config.ymlとトンネル名を指定して利用する従来のCloudflare設定です。
  - 「Cloudflare(一時アドレス)」は cloudflared.exe の --url オプションで一時的な https://xxxx.trycloudflare.com\
     アドレスを自動発行し、Webhook一時URLとして自動反映されます。
  - GUIの「トンネルサービス」選択で「cloudflare_domain」「cloudflare_tempurl」を切り替え可能です。
  - Cloudflare一時アドレス利用時、URLは自動取得され一時URLに設定・表示されます。
- ngrokやlocaltunnel利用時は**各公式手順に従いインストール・設定**をしてください。
- Customトンネルもコマンド指定で利用可能ですが、**動作保証・サポート対象外**です。

詳細なセットアップ・運用方法は`ARCHITECTURE.ja.md`や`CONTRIBUTING.ja.md`も参照してください。

---

## ファイル構成
このプログラムは以下のファイル構成/フォルダで構成されています。

```
プロジェクトルート/
├── app_initializer.py
├── app_version.py
├── bluesky.py
├── cleanup.py
├── development-requirements.txt
├── eventsub.py
├── LICENSE
├── log_viewer.py
├── logging_config.py
├── main.py
├── niconico_monitor.py
├── pep8_check.txt
├── pyproject.toml
├── pytest.ini
├── README.md
├── requirements.txt
├── service_monitor.py
├── settings.env
├── settings.env.example
├── tunnel_manager.py
├── tunnel.py
├── utils.py
├── version_info.py
├── webhook_routes.py
├── youtube_monitor.py
├── Cloudflared/
│   └── config.yml.example
├── diff/
│   └── diff_tool.py
├── Docker/
│   ├── docker_readme_section.ja.md
│   ├── docker-compose.yml
│   └── Dockerfile
├── document/
│   ├── All-ModuleList.md
│   ├── ARCHITECTURE.ja.md
│   ├── comprehensive_summary_japanese.md
│   ├── consolidated_summary_japanese.md
│   └── CONTRIBUTING.ja.md
├── gui/
│   ├── account_settings_frame.py
│   ├── app_gui.py
│   ├── bluesky_acc_tab.py
│   ├── bluesky_post_settings_frame.py
│   ├── console_output_viewer.py
│   ├── discord_notification_frame.py
│   ├── log_viewer.py
│   ├── logging_console_frame.py
│   ├── logging_notification_frame.py
│   ├── main_control_frame.py
│   ├── niconico_acc_tab.py
│   ├── niconico_notice_frame.py
│   ├── notification_customization_frame.py
│   ├── setting_status.py
│   ├── settings_editor_dialog.py
│   ├── setup_wizard.py
│   ├── template_editor_dialog.py
│   ├── timezone_settings.py
│   ├── tunnel_cloudflare_frame.py
│   ├── tunnel_cloudflare_temp_frame.py
│   ├── tunnel_connection.py
│   ├── tunnel_custom_frame.py
│   ├── tunnel_localtunnel_frame.py
│   ├── tunnel_ngrok_frame.py
│   ├── twitch_acc_tab.py
│   ├── twitch_notice_frame.py
│   ├── webhook_acc_tab.py
│   ├── webhookurl_acc_tab.py
│   ├── youtube_acc_tab.py
│   ├── youtube_notice_frame.py
│   └── ユーザーマニュアル_StreamNotifyonBluesky_GUI設定エディタ.txt
├── images/
│   └── noimage.png
├── logs/
│   └── ...
├── templates/
│   ├── niconico/
│   │   ├── __init__.txt
│   │   ├── nico_new_video_template.txt
│   │   └── nico_online_template.txt
│   ├── twitch/
│   │   ├── __init__.txt
│   │   ├── twitch_offline_template.txt
│   │   └── twitch_online_template.txt
│   ├── youtube/
│   │   ├── __init__.txt
│   │   ├── yt_new_video_template.txt
│   │   ├── yt_offline_template.txt
│   │   └── yt_online_template.txt
│   ├── nico_new_video_template.txt
│   ├── nico_online_template.txt
│   ├── twitch_offline_template.txt
│   ├── twitch_online_template.txt
│   ├── yt_new_video_template.txt
│   └── yt_online_template.txt
└── tests/
    ├── __init__.py
    ├── test_bluesky.py
    ├── test_eventsub.py
    ├── test_integration.py
    ├── test_main.py
    ├── test_performance.py
    ├── test_utils.py
    ├── test_youtube_niconico_monitor.py
    ├── tunnel_tests.py
    └── ...
```
---
## セットアップ手順
- **※このアプリケーションはWindows専用です。LinuxやMacには対応していません。**
- もし仮にWindows以外の環境で動いたとしてもサポート対象外です。

### 1. **リポジトリをクローン**

   ```
   git clone https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky.git
   cd Twitch-Stream-notify-on-Bluesky
   ```

### 2. **Python パッケージをインストール**

   ```
   pip install -r requirements.txt
   ```
  - 開発者の方はdevelopment-requirements.txtのほうをお使いください。

### 3. **Cloudflare Tunnel または他のトンネル通信アプリケーションをインストール**  
- CloudflareTunnelをご利用の場合は \
[公式手順](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)に従いcloudflared（cloudflared.exe 等）をインストールしてください。
- ngrokやlocaltunnelを利用する場合は、各公式手順に従いインストールしてください。 
- その他、本アプリケーションおよびGUIに対応していないトンネル通信アプリケーションは、\
customコマンドでご利用いただけます。\
※場合によっては**Pathの設定**が必要な場合があります。

### 4. **Cloudflare Tunnel または他のトンネル通信アプリケーションをセットアップ**

- CloudflareTunnelをご利用の場合は、Cloudflare Zero Trust でトンネルを作成し、\
設定ファイル(config.yml)を準備してください。\
※詳細は[Cloudflare Tunnel 公式ドキュメント](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)を参照。
- **Cloudflaredの設定ファイル config.yml のサンプル**は本アプリケーションの\
「Cloudflared」フォルダ内にあります。
- 必要に応じてコピーを作成して以下の場所に置いてください。\
※すでにトンネルuuidのjsonとcert.pemがあるフォルダです。
  ```
  C:\Users\[お使いのパソコンのuser名]\.cloudflared\config.yml
  ``` 
#### ngrokやlocaltunnelを利用した運用について
- 本アプリケーション(GUIを含む)は、CloudflareTunnel以外にngrokとlocaltunnelに対応しています。\
それ以外のトンネル通信アプリケーションでもCustomで設定していただくことにより\
利用可能だと思われますが、動作確認およびサポートの対象外とさせていただいています。

### 5. **初期設定を行う**
- アプリケーションの起動時に設定ファイルがない場合、\
「設定ファイルが見つかりません。初期セットアップを実行します。」が表示され、\
セットアップウィザードが実行されます。

### セットアップウィザードで設定を行う場合
- 設定用GUI`gui\app_gui.py`を起動した時に設定ファイルが見つからなかった場合は、\
「初期設定ウィザード」`gui\setup_wizard.py`が自動的に起動します。
- ウィザードはGUIで本アプリケーションの利用で必須となるBlueskyアカウントの設定と\
設定ファイルの生成をサポートします(それ以外の機能・設定はメインGUIから行ってください)。
- 入力内容の確認・保存後、`settings.env` が自動生成されます。
- ウィザード完了後はメイン画面が自動で開きます。
- 途中でキャンセルやバツで閉じた場合はアプリケーションが終了します。

### 設定ファイルを直接編集する場合
- 設定ファイルの直接編集は推奨されません。\
設定用GUIやセットアップウィザードをご利用ください。

<details>

```
# このファイルを settings.env にコピーして、各値を設定してください。
# コメント行 (#で始まる行) や空行は無視されます。
#
# --- Bluesky関連設定 ---
# Blueskyのユーザー名 (例: your-handle.bsky.social or 独自ドメイン等ご利用中のID)
BLUESKY_USERNAME=
# Blueskyのアプリパスワード (Blueskyの設定画面で発行してください)
BLUESKY_APP_PASSWORD=
# Bluesky投稿時に使用する画像ファイルのパス(Twitch/YouTube/ニコニコ共通)
BLUESKY_IMAGE_PATH=images/noimage.png
# 放送開始投稿用テンプレートファイル(Twitch)
BLUESKY_TEMPLATE_PATH=templates/twitch_online_template.txt
# 放送終了投稿用テンプレートファイル(Twitch)
BLUESKY_OFFLINE_TEMPLATE_PATH=templates/twitch_offline_template.txt
# 放送開始通知投稿用テンプレートファイル(YouTubeLive)
BLUESKY_YT_ONLINE_TEMPLATE_PATH=templates/yt_online_template.txt
# 放送終了通知投稿用テンプレートファイル(YouTubeLive)
BLUESKY_YT_OFFLINE_TEMPLATE_PATH=templates/yt_offline_template.txt
# 動画投稿通知用テンプレートファイル(YouTube動画)
BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH=templates/yt_new_video_template.txt
# 放送開始通知投稿用テンプレートファイル(ニコニコ生放送)
BLUESKY_NICO_ONLINE_TEMPLATE_PATH=templates/nico_online_template.txt
# 動画投稿通知用テンプレートファイル(ニコニコ動画)
BLUESKY_NICO_NEW_VIDEO_TEMPLATE_PATH=templates/nico_new_video_template.txt
#
# --- Twitch関連設定 ---
# TwitchアプリケーションのクライアントID (Twitch Developer Consoleで取得)
TWITCH_CLIENT_ID=
# Twitchアプリケーションのクライアントシークレット (Twitch Developer Consoleで取得)
TWITCH_CLIENT_SECRET=
# 通知対象のTwitch放送者のユーザー名
TWITCH_BROADCASTER_ID=
# APIアクセス用TwitchBroadcasterID(自動変換・入力されます)
TWITCH_BROADCASTER_ID_CONVERTED=
# Twitch EventSub WebhookのコールバックURL
# Cloudflare Tunnelなどで公開したこのアプリの /webhook エンドポイントのURL
# 例: https://your-tunnel-domain.com/webhook
WEBHOOK_CALLBACK_URL=
# WebhookコールバックURL（恒久用: Cloudflare/custom、または手動設定用）
WEBHOOK_CALLBACK_URL_PERMANENT=
# WebhookコールバックURL（一時用: ngrok/localtunnel自動取得用）
WEBHOOK_CALLBACK_URL_TEMPORARY=
# Webhook署名検証用のシークレットキー
# アプリケーション起動時に自動生成されますので空欄にしてください。
WEBHOOK_SECRET=
# シークレットが最後に更新された日時（自動入力されます）
SECRET_LAST_ROTATED=
# Twitch EventSubの各APIリクエストが失敗した場合のリトライ回数
RETRY_MAX=3
# リトライ時の待機秒数
RETRY_WAIT=2
#
# --- YouTube関連設定 ---
# YouTube Data API v3のAPIキー
YOUTUBE_API_KEY=
# 監視対象のYouTubeチャンネルID
YOUTUBE_CHANNEL_ID=
# YouTubeのポーリング間隔（秒、デフォルト: 60）
YOUTUBE_POLL_INTERVAL=60
# YouTube放送中のポーリング間隔（秒、デフォルト: 30）
YOUTUBE_POLL_INTERVAL_ONLINE=30
# YouTube放送外のポーリング間隔（秒、デフォルト: 180）
YOUTUBE_POLL_INTERVAL_OFFLINE=180
#
# --- ニコニコ関連設定 ---
# 監視対象のニコニコユーザーID（数字のみ）
NICONICO_USER_ID=
# ニコニコのポーリング間隔（秒、デフォルト: 60）
NICONICO_LIVE_POLL_INTERVAL=60
#
# --- 通知設定 ---
# Twitch放送開始時にBlueskyへ通知するか (True/False)
NOTIFY_ON_TWITCH_ONLINE=False
# Twitch放送終了時にBlueskyへ通知するか (True/False)
NOTIFY_ON_TWITCH_OFFLINE=False
# YouTube放送開始時にBlueskyへ通知するか(True/False)
NOTIFY_ON_YT_ONLINE=False
# YouTube放送終了時にBlueskyへ通知するか(True/False)
NOTIFY_ON_YOUTUBE_OFFLINE=False
# YouTube新着動画投稿時にBlueskyへ通知するか(True/False)
NOTIFY_ON_YT_NEWVIDEO=False
# ニコニコ生放送放送開始時にBlueskyへ通知するか(True/False)
NOTIFY_ON_NICO_ONLINE=False
# ニコニコ動画新着投稿時にBlueskyへ通知するか(True/False)
NOTIFY_ON_NICO_NEWVIDEO=False
# Discord通知を有効にするか (True/False)
DISCORD_NOTIFY_ENABLED=False
#
# --- ロギング関連設定 ---
# Discordへ通知するログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
discord_notify_level=CRITICAL
# コンソール・ログに出力するログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=DEBUG
# Discord通知用のWebhook URL
discord_error_notifier_url=
# ログファイルのローテーション保持日数 (日単位の整数)
LOG_RETENTION_DAYS=14
#
# --- トンネル関連設定 ---
# Cloudflare Tunnelなどのトンネルを起動するコマンド 
# 設定しない場合はトンネルを起動しません。
TUNNEL_SERVICE=none
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
#
# --- 一般設定 ---
# タイムゾーン設定 (例: Asia/Tokyo, UTC, America/New_York, Europe/London)
# "system" を指定すると、実行環境のシステムタイムゾーンを自動的に使用します。
# 無効な値や空の場合はシステムタイムゾーンまたはUTCにフォールバックします。
TIMEZONE=system
# ナイトモード設定
APPEARANCE_MODE=system

```
</details>

## Dockerでの実行 (Windowsコンテナ)
<details>
このアプリケーションは、Windowsコンテナを使用してDockerコンテナ内で実行できます。これは、アプリケーションとその依存関係を分離するのに特に便利です。

### 前提条件

*   **Docker Desktop for Windows:** Docker Desktopをインストールし、\
**Windowsコンテナ**を使用するように設定していることを確認してください。

### セットアップ

1.  **`settings.env`の設定:**
    *   Dockerコンテナをビルドまたは実行する前に、プロジェクトのルートディレクトリにある\
    `settings.env.example`ファイルを`settings.env`にコピーしてください。
    *   `settings.env`を編集し、必要なすべての認証情報と設定詳細（Twitch APIキー、Bluesky認証情報など）を記入してください。\
    このファイルはコンテナにマウントされます。

### 推奨: Docker Composeの使用

Docker Composeは、コンテナのライフサイクルを簡単に管理する方法を提供します。\
プロジェクトルートに`docker-compose.yml`ファイルが提供されています。

*   **アプリケーションの起動 (デタッチモード):**
    ```bash
    docker-compose up -d
    ```
*   **ログの表示:**
    ```bash
    docker-compose logs -f twitch-bluesky-bot
    ```
    （実行中のサービスがこれだけの場合は`docker-compose logs -f`も使用できます）
*   **アプリケーションの停止:**
    ```bash
    docker-compose down
    ```
*   **アプリケーションの再ビルドと更新 (例: コード変更やDockerfile更新後):**
    ```bash
    docker-compose build && docker-compose up -d --force-recreate
    ```

### 代替案: `docker run`の使用

Dockerコマンドを使用して手動でコンテナをビルドおよび実行することもできます。

1.  **Dockerイメージのビルド:**
    イメージにカスタム名をタグ付けしたり、最初からビルドすることを確認したい場合:
    ```bash
    docker build -t your-custom-name/twitch-bluesky-bot .
    ```
    （カスタム名を指定しない場合は、`docker-compose.yml`で使用されているタグに依存するか、\
    特定のタグなしでビルドし、その後イメージIDを使用する可能性があります）。

2.  **Dockerコンテナの実行:**
    このコマンドは、ローカルの`settings.env`と`logs`ディレクトリをコンテナにマウントします。
    ```bash
    docker run --name twitch-bluesky-bot-manual -v "%CD%\settings.env:C:\app\settings.env" -v "%CD%\logs:C:\app\logs" your-custom-name/twitch-bluesky-bot
    ```
    *   **注意:** `your-custom-name/twitch-bluesky-bot`を`docker build`コマンド中に使用したタグ\
    （またはタグ付けしなかった場合はイメージID）に置き換えてください。
    *   `%CD%`はWindowsコマンドプロンプトの現在のディレクトリを指します。PowerShellを使用している場合は、\
    `$(pwd)`を使用するか、絶対パスを指定する必要がある場合があります。
    *   デタッチモード（バックグラウンド）で実行するには、`-d`フラグを追加します:
        ```bash
        docker run -d --name twitch-bluesky-bot-manual -v "%CD%\settings.env:C:\app\settings.env" -v "%CD%\logs:C:\app\logs" your-custom-name/twitch-bluesky-bot
        ```

### ログへのアクセス

*   Docker Composeまたは指定されたボリュームマウントで`docker run`を使用する場合、\
アプリケーションログはローカルマシンのプロジェクトルートにある`./logs`ディレクトリに永続化されます。\
これにより、コンテナが停止した後でもログファイルにアクセスできます。

</datails>

### 6.サーバー・トンネルの起動/停止

- 本アプリケーションは「CUI（`main.py`）」だけでなく「GUI（`gui/app_gui.py`）」からも、 \
サーバー・トンネルの起動/停止・状態確認が可能です。
- GUIからアプリおよびトンネルを「開始」「停止」する場合は「アプリ管理」タブから操作できます。
- アプリおよびトンネルをCUIから開始する場合は`main.py`で開始し、Ctrl+C（SIGINT）で安全に終了できます。
- どちらの方法で実行しても、終了時に必ず「**アプリケーションのクリーンアップ処理**」が動作し、\
コンソール表示とログファイルに**ログが記録されます**。
- GUI/CUIどちらからの操作に関わらず、異常終了や強制終了時であっても、\
**ログファイル保存**,**ファイルロック解放**,**プロセス終了**が保証されます。

---

## カスタマイズ

### **通知レベルの変更**
**settings.env**または**設定GUI** で\
`discord_notify_level`（例：DEBUG, INFO, WARNING, ERROR, CRITICAL）を変更できます。
### **ログレベルの一括変更**
**settings.env**または**設定GUI** で\
`LOG_LEVEL`（例：DEBUG, INFO, WARNING, ERROR, CRITICAL）を変更できます。\
  ※コンソール表示とログ保存の２つをまとめて変更します。
### **Bluesky 投稿履歴**
すべての投稿履歴は`logs/post_history.csv`に自動記録されます。\
※GUIのログビューアからも投稿履歴をご確認いただけます。
### **トンネル通信設定のカスタマイズ**
  CloudflareTunnel,ngrok,localtonnelの設定をサポートしています。\
  他のトンネル通信アプリケーションにもCustom設定を利用することで対応可能です。\
  (ただしサポート対象外)
### **投稿テンプレートの切り替え**
- テンプレートを切り替える場合、\
  **settings.env**または**設定GUI**の各サービス用の設定項目から、\
使用するテンプレートのファイル名を指定（書き替える）とテンプレートの切り替えができます。

- **テンプレートファイルが見つからない場合**は、エラーログが記録され、\
  下記のデフォルトテンプレートが利用されます。
- **.template**フォルダ、および**__init__.txtファイル**はシステム用フォルダ/ファイルです！\
機能不良や不具合の原因となりますので、削除・ファイル名の変更をしないでください。
```
 【放送開始または動画投稿告知】
以下の放送が開始されたか動画が投稿されました。
※放送プラットフォームが特定できなかったため、
最小限の内容で投稿しております。
タイトル: {{ title }}
放送者: {{ broadcaster_user_name }} ({{ broadcaster_user_login }})
カテゴリ: {{ category_name }}
開始日時: {{ start_time | datetimeformat }}
視聴URL: {{ stream_url }}
  ```
  ```
  【放送終了】
以下の放送は終了しました。
※放送プラットフォームが特定できなかったため、
最小限の内容で投稿しております。
放送者: {{ broadcaster_user_name }} ({{ broadcaster_user_login }})
チャンネルURL: {{ channel_url }}
  ```
- テンプレートを編集しない場合は以下の内容が投稿されます。
## Twitchの場合
  ```
Twitch 放送開始 🎉

放送者: {{ broadcaster_user_name }} ({{ broadcaster_user_login }})
タイトル: {{ title }}
カテゴリ: {{ category_name }}
開始日時: {{ start_time | datetimeformat }}
視聴URL: {{ stream_url }}

ぜひ遊びに来てください！
#Twitch放送通知📺
  ```
  ```
🛑 Twitch 放送終了

{{ broadcaster_user_name | default('放送者名不明') }} さんのTwitch放送が終わりました。
チャンネル: {{ channel_url | default('チャンネルURL不明') }}

またの放送をお楽しみに！
#Twitch #放送終了 
  ```
## YouTubeLiveの場合 
  ```
▶️ YouTube Live 放送開始 🚀

チャンネル: {{ broadcaster_user_name }}
タイトル: {{ title }}
開始日時: {{ start_time | datetimeformat }}
視聴URL: {{ stream_url }}

みなさんの視聴をお待ちしています！
  ```
  ```
  🛑 YouTube Live 放送終了

チャンネル: {{ channel_name }}
タイトル: {{ title }}
開始日時: {{ start_time | datetimeformat }}
放送URL: {{ stream_url }}

またの放送をお楽しみに！
  ```
## ニコニコ生放送の場合 
  ```
📡 ニコニコ生放送 開始 🎉

放送者: {{ broadcaster_user_name }}
タイトル: {{ title }}
開始日時: {{ start_time | datetimeformat }}
視聴URL: {{ stream_url }}

コメントお待ちしています！
  ```
## YouTube動画の場合
  ```
🎬 YouTube に新着動画投稿！

タイトル: {{ title }}
動画ID: {{ video_id }}
視聴URL: {{ video_url }}

チェックお願いします！👍
  ```
## ニコニコ動画の場合
  ```
📽 ニコニコ動画 新着投稿！

タイトル: {{ title }}
動画URL: {{ video_url }}

ぜひご覧ください！
  ```
---

## よくある質問（FAQ）

### ドメイン・トンネル通信アプリケーション関連
<details>

### Q. ドメインをもっていなくても利用できますか？

A.  はい。**ドメインを持っていなくともご利用いただけます**。\
ただし、ドメインなしで利用するためには**app_version1.0.4-beta以降**のアプリケーションが必要です。

### Q. CloudflareTunnelを使うための条件はなんですか？

A.  Cloudflare Tunnelは**独自ドメインの所有**かつ、**CloudflareによるDNS管理**が前提となるため、\
  **ドメインを持っていない場合**や**CloudflareでDNSを管理していない場合**には利用できません。
  - ただし「Cloudflare(一時アドレス)」モードを使えば、独自ドメインなしでも一時的なtrycloudflare.comアドレスでWebhook受信が可能です（GUIで選択可）。

### Q. Cloudflare以外でDNS管理をしている場合でもこのアプリケーションを利用できますか？

A. はい。**ドメインの管理がCloudflareでない場合**でも、\
**ngrokやlocaltunnelなどに対応**しているため、それらを用いればご利用いただけます。
- 公式でのサポート対象は、\
Cloudflare DNSにより管理されたドメインを用いたCloudflare Tunnelでのご利用\
または、**設定GUIで設定可能な他のトンネル通信アプリケーション**をご利用いただくこととなっております。\
そのため、**Custom設定でご利用の場合は公式サポートの対象外**とさせていただいています。

### Q. トンネル通信アプリケーションはどのように管理されていますか？

A. アプリケーションの基本機能を担当するmain.pyがトンネル通信機能の起動
停止・URL取得を自動で管理します。
トンネル通信アプリケーションを起動後WebhookURLは自動で取得され、
GUIのURL欄に即時反映されます。
- Cloudflare Tunnelは「独自ドメイン用」と「一時アドレス用」で設定画面が分かれており、
  一時アドレス利用時はtrycloudflare.comのURLが自動反映されます。
</details>

### エラー関連
<details>

### Q. トンネル通信アプリケーションがインストールされていませんと出ます

A. 当アプリケーションはCloudflare/ngrok/localtonnelでご利用いただけますが、\
**トンネル通信アプリケーションの自動インストール機能はついておりません**ので、\
事前にインストールをお願いします。
- CloudflareTunnelをご利用の方は、[公式ページ](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)から cloudflared をダウンロードし、\
`settings.env`または`設定用GUI`からトンネルサービスを正しく設定してください。\
※運用環境によってはPathをダブルクォーテーションで囲って記載する必要がある場合があります。
- (例：)wingetコマンドでインストールした場合の記載例。※[ ]内がコマンドです。
  ```
  TUNNEL_CMD=[cloudflared.exe tunnel --config C:\Users\[パソコンのユーザーID]\.cloudflared\config.yml run <トンネル名>]"
  ```
※例えば上の記載例のように、**ファイルパス内に空白がある場合**は、\
**ダブルクォーテーションで囲って記載する**必要がありますので注意してください。

### Q. テンプレートや画像ファイルのパスはどのように指定すればよいですか？

A. templates/ や images/ フォルダ内のファイルは、\
**相対パス（例: templates/xxx.txt, images/xxx.png）で指定してください。**
- GUIでファイル選択した場合も自動で相対パスに変換されます。
- プロジェクト外や絶対パスの場合はそのまま絶対パスで保存されます。

### Q. テンプレートファイルが見つからないというエラーがでます。

A. **ファイル名の指定**が間違っている可能性があるので確認してください。\
指定した**ファイルが存在するかどうか**も確認してください。

**正しいファイル名の指定形式**は以下のとおりです。
  ```
  BLUESKY_TEMPLATE_PATH=templates/default_template.txt
  ```

ファイル名指定の際、**/から書いてしまうと認識できない**ことがあります。\
また、**拡張子を記載しない場合も認識できない**ことがあるので注意してください。
</details>

### アプリケーションの通信関連
<details>

### Q. アプリケーションの疎通確認方法がわかりません。

A. アプリケーションを起動後、設定したWebhookエンドポイントのURLにブラウザでアクセスしてください。\
下記の状態であれば、外部との通信ができる状態になっています。
- ブラウザの表示が **Webhook endpoint is working! POST requests only.** である。
- コンソールやログファイルの出力に **Webhookエンドポイントは正常に稼働しています**\
というinfoログがある。

### Q. アプリケーションにはエラーが出力されていないのに疎通確認が取れません。

A. 次のどれかが原因の可能性があります。
- Cloudflare側でドメインとトンネルの紐付けができていない\
→ **DNSのCNAMEレコードが正しい値であるか**、Cloudflareダッシュボードで確認してください。

- CNAMEレコードがトンネルのUUID.cfargotunnel.comに向いていない、またはAレコードになっている\
→ **必ずCNAMEでUUID.cfargotunnel.comに向けてください**。

- Cloudflare DNSでドメインを管理していない（外部DNSや未設定）\
→ Cloudflare DNSで管理していない場合、**Cloudflareでのトンネル公開はできません**。

- トンネル名やUUIDの設定ミス\
→ cloudflared tunnel listで表示されるUUIDと、DNS設定のCNAME先が**一致しているか確認してください**。\
一致していない場合は、DNS設定を一致するように書き換えてください。
</details>

### 認証情報関連
<details>

### Q. Twitch/Bluesky/Discord の認証情報はどこで取得しますか？

A. 各サービスの公式サイトから必要な API キーやパスワードを取得してください。\
Bluesky：アプリパスワード(Blueskyの設定→プライバシーとセキュリティー→アプリパスワード)\
Twitch：ユーザーID(アカウント)、クライアントID(Devポータル)、クライアントシークレット(Devポータル)\
Discord：WebhookURL(Discordサーバーの設定→連携サービス→Webhook)
</details>

### Bluesky投稿関連
<details>

### Q. 投稿文のテンプレートを変更したい／多言語対応したい

A. templates/ ディレクトリにテンプレートを追加し、\
**settings.env**または**設定GUI**からテンプレートファイルを切り替えてください。

### Q. 放送終了時にも Bluesky に投稿したい

A. 現時点では放送終了投稿機能はTwitchのみに対応していますが、\
YouTube/ニコニコの放送終了通知についても今後のアップデートで対応すべく\
現在実装方法の検討を行っております。

### Q. Blueskyに投稿する時に画像を添付したい

A. imagesフォルダに画像を置いて、\
**settings.env**または**設定GUI**からファイルを設定してください。
- Blueskyに投稿できる画像形式はJPEG（.jpg/.jpeg）、PNG（.png）、静止画GIFです。\
アニメーションGIF投稿できません。
- Blueskyへの動画投稿には対応していません。
- 画像サイズは1MB以下を推奨します
- 初期設定ではimages/noimage.pngが設定されています。\
また、現状では画像は１枚だけ添付できます。

- **ファイル名の指定**が間違っている場合、デフォルト画像が使用されます。

- **正しいファイル名の指定形式**は以下のとおりです。
  ```
  BLUESKY_IMAGE_PATH=images/noimage.png
  ```
ファイル名指定の際、**/から書いてしまうと認識できない**ことがあります。\
また、**拡張子を記載しない場合も認識できない**ことがあるので注意してください。

</details>

### セキュリティ・保守関連
<details>

### Q. セキュリティ対策はどうなっていますか？

A. このBotはWebhook署名のタイムスタンプ検証によるリプレイ攻撃防止や、\
APIエラー時の自動リトライ機能を備えています。\
また、リトライの回数や間隔は設定ファイルから変更が可能です。

### Q. 監査ログはどこに記録されますか？

A. logs/audit.log に主要な操作履歴が記録されます。

### Q. WEBHOOK_SECRETを変更したいときはどうしたらいいですか？

A. もし運用中に手動でシークレットを変更したい場合は、\
settings.envの**WEBHOOK_SECRETとSECRET_LAST_ROTATEDを空欄にして**再起動してください。\
そうすれば、次回起動時に再生成されます。
</details>

---
## 運用上の注意

- この Bot は個人運用・検証を想定しています。\
商用利用や大規模運用時は自己責任でお願いします。
- セキュリティのため、**APIキーやパスワード**は**絶対に公開リポジトリに含めない**でください。
- 依存パッケージの脆弱性は `pip-audit` や `safety` で定期的にチェックしてください。
- **APIエラー発生時**は自動でリトライ処理を行います。\
また、Webhook署名のタイムスタンプを検証するようになっているため、\
リプレイ攻撃の防止にも効果があります。
- TwitchAPI の利用規約により**API キーの使い回し**や**複数人利用は禁止**されております。\
  利用者側で[Twitch デベロッパーポータル](https://dev.twitch.tv/)にアクセスし、\
  **アプリケーションの登録**と**API キーを生成**してお使いください。
- WEBHOOK_SECRETは30日ごとに自動でローテーションされるため**通常は編集不要**です。
- 監査ログ（logs/audit.log）には重要な操作履歴が記録されます。\
運用時はアクセス権限や保管期間に注意してください。
- 不要なEventSubサブスクリプションはBot起動時に自動削除されます。

---

## このアプリケーションを開発・改変されたい方へ
- mainブランチは「直push禁止＆PR必須」になっています。\
そのため、mainブランチにMerge希望の場合はブランチ作成→PRでお願いします。
- 安全のためGitGuardianを導入しています。\
導入されていない方は以下の方法で導入してください。
 ```
 pip install ggshield pre-commit
 ```

---
## 貢献
このアプリケーションを改善し、拡張するための貢献を歓迎します！\
バグの報告、機能強化の提案、プルリクエストの提出方法の詳細については、\
[貢献ガイドライン](CONTRIBUTING.ja.md)をご覧ください。

---
## 自動テストの実行方法

本アプリケーションは主要な機能やバリデーションの自動テストを備えています。  
テストは [pytest](https://docs.pytest.org/) で簡単に実行できます。

### テストの実行手順

<details>

必要なパッケージをインストール（未インストールの場合）

 ```
 pip install pytest
 ```
プロジェクトルートで以下のコマンドを実行
 ```
python -m pytest
 ```
- 特定のテストファイルだけを実行したい場合は
 ```
 pytest test/test_utils.py
 ```

テスト結果が表示され、すべてのテストがパスすればOKです。

</details>

### テストの補足

- テストコードは `test/` ディレクトリにあります。
- テストの追加や修正はこのディレクトリ内の各ファイルに記述してください。
- 詳細な使い方は [pytest公式ドキュメント](https://docs.pytest.org/) を参照してください。
---
### 今後の開発予定
- ここに書かれてある内容は将来的に実装を計画している、または検討している項目であり、\
具体的な実装時期等は未定です。決まり次第作者のSNSなどでお知らせします。


- **現時点で追加予定の機能はございません。**
---

## ライセンス

GPL License v2

---

## 開発・メンテナンス

- 作者: まゆにゃ（@mayu0326）
- 連絡先：下記のいずれかへ。\
BlueSky:neco.mayunyan.tokyo\
Web:https://mayunyan.tokyo/contact/personal/
- 本アプリケーションはオープンソースです。Issue・PR 歓迎！

---
