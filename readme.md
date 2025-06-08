# Stream notify on Bluesky

- Twitch/YouTube/ニコニコ生放送の放送開始を自動検知し、\
Bluesky へリアルタイムにお知らせ投稿する Python 製 Bot です。
- Youtubeとニコニコについては、放送だけでなく動画投稿の通知にも対応します。    
- Cloudflare Tunnel または他のトンネル通信アプリケーション(ngrok,localtunnel)による、\
Webhook 受信、エラー通知、履歴記録など運用に便利な機能を多数備えています。
- **GUI**からもサーバー・トンネルの起動/停止・状態確認・安全な終了が可能です。
- **CUI/GUI**どちらからでもCtrl+Cや停止ボタンで安全にクリーンアップ・ログ出力\
ファイルロック解放がされます。

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
- **トンネル通信**が不要な場合やデバックなどで個別起動したいときは連携起動OFF可能
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
#### 以下のいずれかのアカウント
- Twitch のユーザーIDとTwitch APIのキー（EventSub 用）
- YouTube のユーザーIDとYouTubeDataAPIのキー(YouTube用)
- ニコニコアカウントの数字ID(パスワードは不要/ニコニコ用)

##### 必須のアカウント
- Bluesky アカウント（投稿用）
- Cloudflareのアカウント（Cloudflare利用時のみ）または、\
ngrokのアカウント(ngrok利用時のみ)

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

---

## カスタマイズ

カスタマイズ・運用Tipsは [User-Manual-GUI の「10. カスタマイズ・運用Tips」](https://github.com/mayu0326/Stream_notify_on_Bluesky/wiki/User-Manual-GUI#10) に移動しました。詳しくはWikiをご覧ください。
---

## よくある質問（FAQ）

[FAQ・トラブルシューティング](FAQ) に移動しました。詳しくはWikiをご覧ください。

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

自動テストの実行方法は [Testing](Testing) に移動しました。詳しくはWikiをご覧ください。

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
