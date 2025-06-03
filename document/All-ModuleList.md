2025年6月時点「Stream notify on Bluesky」プロジェクトにおける全モジュールの種類と使われ方（用途・インポート関係・役割）をまとめます。

---

## 1. コアロジック・主要機能モジュール

| ファイル名                | 種類         | 主な用途・役割                                                                 | 主なインポート先・使われ方                |
|--------------------------|--------------|-------------------------------------------------------------------------------|-------------------------------------------|
| app_version.py           | ユーティリティ| アプリバージョン管理（version_info.py経由で全体からimport・利用）              | version_info.py、main.py、各コア・GUI     |
| bluesky.py               | コア         | Blueskyへの投稿処理・テンプレート管理。                                        | main.py、各監視モジュール                 |
| cleanup.py               | ユーティリティ| 終了時のクリーンアップ処理・リソース解放                                      | main.py                                   |
| eventsub.py              | コア         | Twitch EventSub Webhookの管理・通知検知。                                      | main.py                                   |
| logging_config.py        | ユーティリティ| ログ設定・出力レベル管理。                                                     | main.py、各コア・GUI                      |
| main.py                  | コア         | アプリ全体の起動・管理。トンネル管理や監視、GUI起動などのエントリーポイント。 | 単体実行・全体の起動点                    |
| niconico_monitor.py      | コア         | ニコニコ生放送・動画の監視・通知。                                             | main.py                                   |
| service_monitor.py       | コア         | サービス状態監視・ヘルスチェック                                               | main.py                                   |
| tunnel.py                | コア         | トンネル通信アプリ（Cloudflare/ngrok/localtunnel/custom）の起動・管理。        | main.py、GUI（tunnel_connection等）       |
| utils.py                 | ユーティリティ| 各種共通関数（パス変換・日付整形・ファイル操作など）。                         | 各コア・GUI・テスト                       |
| version_info.py          | ユーティリティ| __version__を一元的に提供                                                     | main.py、各コア・GUI、テスト             |
| webhook_routes.py        | コア         | Webhookエンドポイントのルーティング・受信処理                                   | main.py                                   |
| youtube_monitor.py       | コア         | YouTubeLive・動画の監視・通知。                                                | main.py                                   |

---

## 2. GUI関連モジュール

| ファイル名                              | 種類      | 主な用途・役割                                               | 主なインポート先・使われ方                |
|-----------------------------------------|-----------|-------------------------------------------------------------|-------------------------------------------|
| account_settings_frame.py               | GUI       | アカウント設定タブ                                           | app_gui.py                                |
| app_gui.py                              | GUI本体   | メインGUIウィンドウ・各フレームの統括・起動                   | main.py（GUI起動時のエントリーポイント）  |
| bluesky_acc_tab.py                      | GUI       | Blueskyアカウント設定タブ                                    | app_gui.py                                |
| bluesky_post_settings_frame.py          | GUI       | Bluesky投稿設定タブ                                          | app_gui.py                                |
| discord_notification_frame.py           | GUI       | Discord通知設定タブ                                          | app_gui.py                                |
| log_viewer.py                           | GUI       | ログ・投稿履歴ビューア                                       | app_gui.py                                |
| logging_console_frame.py                | GUI       | ログ出力・レベル設定                                         | app_gui.py                                |
| logging_notification_frame.py           | GUI補助   | ログ出力・レベル設定の補助                                   | logging_console_frame.py等                |
| main_control_frame.py                   | GUI       | メイン操作パネル                                             | app_gui.py                                |
| niconico_acc_tab.py                     | GUI       | ニコニコアカウント設定タブ                                   | app_gui.py                                |
| niconico_notice_frame.py                | GUI       | ニコニコ通知設定タブ                                         | app_gui.py                                |
| notification_customization_frame.py     | GUI補助   | 通知カスタマイズ設定タブ                                     | app_gui.py等                              |
| setting_status.py                       | GUI補助   | 設定状態管理・補助クラス                                     | app_gui.py等                              |
| setup_wizard.py                         | GUI       | 初期セットアップウィザード                                   | app_gui.py                                |
| template_editor_dialog.py               | GUI       | 投稿テンプレートの作成・編集ダイアログ                       | app_gui.py、bluesky_post_settings_frame.py |
| timezone_settings.py                    | GUI       | タイムゾーン設定                                             | app_gui.py                                |
| tunnel_cloudflare_frame.py              | GUI       | Cloudflare Tunnel（独自ドメイン用）専用設定フレーム           | tunnel_connection.py等                    |
| tunnel_cloudflare_temp_frame.py         | GUI       | Cloudflare Tunnel（一時アドレス用）専用設定フレーム           | tunnel_connection.py等                    |
| tunnel_connection.py                    | GUI       | トンネル接続管理・状態表示                                   | app_gui.py                                |
| tunnel_custom_frame.py                  | GUI       | Customトンネル設定フレーム                                   | tunnel_connection.py等                    |
| tunnel_localtunnel_frame.py             | GUI       | localtunnel専用設定フレーム                                  | tunnel_connection.py等                    |
| tunnel_ngrok_frame.py                   | GUI       | ngrok専用設定フレーム                                        | tunnel_connection.py等                    |
| twitch_acc_tab.py                       | GUI       | Twitchアカウント設定タブ                                     | app_gui.py                                |
| twitch_notice_frame.py                  | GUI       | Twitch通知設定タブ                                           | app_gui.py                                |
| webhook_acc_tab.py                      | GUI       | Webhookアカウント設定タブ                                    | app_gui.py                                |
| webhookurl_acc_tab.py                   | GUI       | Webhook URL設定タブ                                          | app_gui.py                                |
| youtube_acc_tab.py                      | GUI       | YouTubeアカウント設定タブ                                    | app_gui.py                                |
| youtube_notice_frame.py                 | GUI       | YouTube通知設定タブ                                          | app_gui.py                                |
| ユーザーマニュアル....txt                | ドキュメント| GUI設定エディタのユーザーマニュアル                          | ドキュメント用途                          |

---

## 3. テスト関連

| ファイル名                        | 種類      | 主な用途・役割                                               | 主なインポート先・使われ方                |
|-----------------------------------|-----------|-------------------------------------------------------------|-------------------------------------------|
| __init__.py                       | テスト    | テストパッケージ初期化                                       | pytest                                   |
| __pycache__/                      | テスト    | テスト用バイトコードキャッシュ                               | pytest                                   |
| test_bluesky.py                   | テスト    | bluesky.pyのテスト                                           | pytest                                   |
| test_eventsub.py                  | テスト    | eventsub.pyのテスト                                          | pytest                                   |
| test_integration.py               | テスト    | 統合テスト                                                   | pytest                                   |
| test_main.py                      | テスト    | main.pyのテスト                                              | pytest                                   |
| test_performance.py               | テスト    | パフォーマンステスト                                         | pytest                                   |
| test_utils.py                     | テスト    | utils.pyのテスト                                             | pytest                                   |
| test_youtube_niconico_monitor.py  | テスト    | youtube_monitor.py/niconico_monitor.pyのテスト               | pytest                                   |
| tunnel_tests.py                   | テスト    | tunnel.pyのテスト                                            | pytest                                   |

---

## 4. その他・設定・ドキュメント

| ファイル名                        | 種類      | 主な用途・役割                                               | 主なインポート先・使われ方                |
|-----------------------------------|-----------|-------------------------------------------------------------|-------------------------------------------|
| ARCHITECTURE.ja.md                | ドキュメント| アーキテクチャ詳細（日本語）                                 | -                                        |
| CONTRIBUTING.ja.md                | ドキュメント| コントリビュートガイド（日本語）                             | -                                        |
| LICENSE                           | ライセンス| ライセンス文書                                               | -                                        |
| README.md                         | ドキュメント| 全体説明・セットアップ・FAQ等                                | -                                        |
| comprehensive_summary_japanese.md | ドキュメント| 機能・構成の詳細まとめ（日本語）                             | -                                        |
| config.yml.example                | 設定      | Cloudflared用サンプル設定                                    | Cloudflare利用時                         |
| consolidated_summary_japanese.md  | ドキュメント| 機能・構成の簡易まとめ（日本語）                             | -                                        |
| development-requirements.txt      | 設定      | 開発用依存パッケージリスト                                   | pip                                      |
| docker-compose.yml                | 設定      | Docker用構成ファイル                                         | Docker利用時                             |
| docker_readme_section.ja.md       | ドキュメント| Docker用構成・説明書（日本語）                               | Docker利用時                             |
| Dockerfile                        | 設定      | Docker用ビルドファイル                                       | Docker利用時                             |
| pytest.ini                        | 設定      | pytest設定                                                   | pytest                                   |
| requirements.txt                  | 設定      | 本番用依存パッケージリスト                                   | pip                                      |
| settings.env / settings.env.example| 設定     | 環境変数・設定ファイル                                       | main.py、各コア・GUI                      |

---

## 5. テンプレート・画像・ログ

| ディレクトリ/ファイル                 | 種類      | 主な用途・役割                                   | 主なインポート先・使われ方                |
|-------------------------------------|-----------|-------------------------------------------------|-------------------------------------------|
| images/                             | 画像      | 投稿用画像（noimage.png等）                      | bluesky.py、GUI                          |
| logs/                               | ログ      | 投稿履歴・監査ログ・エラーログ等                 | main.py、GUI、各コア                     |
| logs/app.log                        | ログ      | アプリケーションログ                             | main.py、logging_config.py               |
| logs/audit.log                      | ログ      | 監査ログ                                         | main.py等                                |
| logs/error.log                      | ログ      | エラーログ                                       | main.py等                                |
| logs/post_history.csv               | ログ      | 投稿履歴CSV                                      | main.py、GUI                             |
| logs/tunnel.log                     | ログ      | トンネル関連ログ                                 | tunnel.py等                              |
| templates/niconico/                 | テンプレート| ニコニコ用テンプレート格納ディレクトリ（__init__.txtは削除・改名禁止） | bluesky.py、GUI |
| templates/niconico/__init__.txt     | テンプレート| ニコニコ用システムファイル                        | bluesky.py、GUI                          |
| templates/niconico/nico_new_video_template.txt | テンプレート| ニコニコ新規動画投稿通知テンプレート             | bluesky.py                                |
| templates/niconico/nico_online_template.txt    | テンプレート| ニコニコ放送開始通知テンプレート                 | bluesky.py                                |
| templates/twitch/                   | テンプレート| Twitch用テンプレート格納ディレクトリ（__init__.txtは削除・改名禁止）   | bluesky.py、GUI |
| templates/twitch/__init__.txt       | テンプレート| Twitch用システムファイル                          | bluesky.py、GUI                          |
| templates/twitch/twitch_offline_template.txt   | テンプレート| Twitch放送終了通知テンプレート                  | bluesky.py                                |
| templates/twitch/twitch_online_template.txt    | テンプレート| Twitch放送開始通知テンプレート                  | bluesky.py                                |
| templates/youtube/                  | テンプレート| YouTube用テンプレート格納ディレクトリ（__init__.txtは削除・改名禁止）  | bluesky.py、GUI |
| templates/youtube/__init__.txt      | テンプレート| YouTube用システムファイル                         | bluesky.py、GUI                          |
| templates/youtube/yt_new_video_template.txt    | テンプレート| YouTube新規動画投稿通知テンプレート             | bluesky.py                                |
| templates/youtube/yt_offline_template.txt      | テンプレート| YouTube放送終了通知テンプレート                 | bluesky.py                                |
| templates/youtube/yt_online_template.txt       | テンプレート| YouTube放送開始通知テンプレート                 | bluesky.py                                |

---

## 6. インポート・利用関係のポイント

- `main.py`が全体の起動点で、**コアロジック・監視・トンネル・GUIを統括**。
- `bluesky.py`, `eventsub.py`, `niconico_monitor.py`, `youtube_monitor.py`, `tunnel.py`は`main.py`から直接呼ばれる。
- `utils.py`, `logging_config.py`, `app_version.py`などは**各所で共通利用**。
- `app_gui.py`がGUIのエントリーポイントで、各フレーム（`account_settings_frame.py`等）をimportして統合。
- `tunnel_connection.py`はトンネル種別ごとのフレーム（`tunnel_cloudflare_frame.py`等）をimportして利用。
- `tests/`配下は**pytestによる自動テスト用**。

---

## 7. 特記事項

- **Cloudflare Tunnel**は「独自ドメイン用」と「一時アドレス用（trycloudflare.com）」でフレーム分離・管理。
- **トンネル管理**は`main.py`と`tunnel.py`が中心、GUIからも状態反映・コマンド実行可能。
- GUIの各設定・状態は`app_gui.py`が統括し、各フレームで分担管理。
- **テンプレートファイルのデフォルトパス**は`bluesky.py`で`templates/`配下に指定。
- テンプレートディレクトリ（templates/）配下にはniconico/twitch/youtube各サブディレクトリと__init__.txtファイルがあり、\
これらはシステム用です。削除・ファイル名変更は不具合の原因となるため禁止します。

---

この一覧が現時点の全モジュールの種類・役割・使われ方のまとめです。\
さらに詳細な依存関係や設計意図は`ARCHITECTURE.ja.md`や`comprehensive_summary_japanese.md`も参照してください。