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
## セットアップ手順
- **※このアプリケーションはWindows専用です。LinuxやMacには対応していません。**
- もし仮にWindows以外の環境で動いたとしてもサポート対象外です。

1. 必要なソフトをインストール（Python, Git, Cloudflared等）
2. リポジトリをクローンし、依存パッケージをインストール
3. GUI（`python gui/app_gui.py`）を起動
4. 初回起動時はウィザードでBlueskyアカウント等を設定
5. 通知したいサービスやテンプレートをGUIで選択・保存
6. [FAQ](https://github.com/mayu0326/Stream_notify_on_Bluesky/wiki/FAQ) や [GUIマニュアル](https://github.com/mayu0326/Stream_notify_on_Bluesky/wiki/User-Manual-GUI) も参照してください。

詳しいセットアップ方法は [インストール・セットアップ手順](https://github.com/mayu0326/Stream_notify_on_Bluesky/wiki/Getting-Started-Setup) をご確認ください。

---

## カスタマイズ

- カスタマイズ・運用Tipsは [User-Manual-GUI](https://github.com/mayu0326/Stream_notify_on_Bluesky/wiki/User-Manual-GUI#10) に移動しました。詳しくはWikiをご覧ください。
---

## よくある質問（FAQ）

[FAQ・トラブルシューティング](https://github.com/mayu0326/Stream_notify_on_Bluesky/wiki/FAQ) に移動しました。詳しくはWikiをご覧ください。

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
[貢献ガイドライン](https://github.com/mayu0326/Stream_notify_on_Bluesky/blob/main/document/CONTRIBUTING.ja.md)をご覧ください。

---
## 自動テストの実行方法

自動テストの実行方法は [Testing](https://github.com/mayu0326/Stream_notify_on_Bluesky/wiki/Testing) に移動しました。詳しくはWikiをご覧ください。

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
