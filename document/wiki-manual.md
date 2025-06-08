# Stream notify on Bluesky Wiki Construction Manual

## Purpose
このマニュアルは「Stream notify on Bluesky」プロジェクトのための包括的なGitHub Wikiを構築する標準手順を示します。プロジェクトの実装・運用・拡張・保守に必要な情報を、コードベースに即して正確に記述することを目的とします。

## Wiki Structure Template

### 1. Home Page (`Home.md`)
- プロジェクトの概要・目的・主な特徴
- 各セクションへのクイックナビゲーション
- 技術ドキュメント・主要リソース（リポジトリ、CI/CD、PyPI等）へのリンク

### 2. Getting Started
- `Getting-Started-Development-Setup.md` - 開発環境セットアップ手順（Python, 仮想環境, 依存パッケージ, settings.env, Cloudflared等）
  - **Windows専用**: 本アプリケーションはWindows環境のみ対応しています。MacやLinuxには対応していません。
  - **Python未導入環境向け**: Python公式サイトからのインストール手順（Windowsのみ）を明記
  - **Git未導入環境向け**: Git公式サイトからのインストール手順（Windowsのみ）を明記
- `Getting-Started-Quick-Start.md` - 5分で動かす手順（最小構成例、GUI/CLI起動例）
- `Getting-Started-Architecture-Overview.md` - システム全体像（Mermaid図推奨）
- `Getting-Started-Core-Concepts.md` - 主要な技術用語・概念（Webhook, Tunnel, Template, Bluesky API等）

### 3. Architecture
- `Architecture-Technology-Stack.md` - 使用技術・主要ライブラリ（Python, Flask, Tkinter, atproto, Jinja2, pytest, Cloudflared等）
- `Architecture-System-Design.md` - 全体設計・設計思想・設計パターン
- `Architecture-Module-Structure.md` - コア/GUI/ユーティリティ/テスト等のモジュール構成（All-ModuleList.md, ARCHITECTURE.ja.md参照、Mermaid図可）
- `Architecture-Data-Flow.md` - データ・通知・イベントの流れ（Mermaid図推奨）

### 4. Testing
- `Testing-Testing-Strategy.md` - テスト全体方針（pytest, テスト自動化, CI/CD, テストカバレッジ）
- `Testing-Unit-Testing.md` - ユニットテストの書き方・実行方法（tests/配下、pytest.ini、mock活用例）
- `Testing-Integration-Testing.md` - 統合テストの指針（Webhook, Tunnel, Bluesky連携のテスト）
- `Testing-E2E-Testing.md` - E2Eテスト（GUI操作や外部サービス連携の自動化例）
- `Testing-Performance-Testing.md` - パフォーマンステスト（test_performance.py等）

### 5. Development Guides
- `Development-Guides-Local-Development.md` - ローカル開発・デバッグ手順（仮想環境、settings.env、GUI/CLI切替、ログ確認）
- `Development-Guides-Debugging.md` - デバッグ手法・ツール（logging_config.py, ログ出力, GUIデバッグ, VSCode等）
- `Development-Guides-Profiling.md` - パフォーマンスプロファイリング（time/perf, ログ活用）
- `Development-Guides-Logging.md` - ロギング標準（logs/配下, Discord通知, ログレベル, ローテーション）
- `Development-Guides-Monitoring.md` - 監視・運用（service_monitor.py, logs/audit.log, post_history.csv）
- `Development-Guides-Code-Styles.md` - コーディング規約・スタイルガイド（autopep8, pre-commit, Black, CONTRIBUTING.ja.md参照）

### 6. Deployment
- `Deployment-Build-Process.md` - ビルド・配布手順（requirements.txt, pyproject.toml）
- `Deployment-Configuration.md` - 環境設定（settings.env, config.yml, secrets管理）
- `Deployment-Deployment-Guide.md` - デプロイ手順（本番/開発環境、トンネル起動、CI/CD）
- `Deployment-Infrastructure.md` - インフラ要件（Cloudflared, ngrok, localtunnel, Discord, Bluesky, GitHub Actions等）
- `Deployment-CI-CD.md` - CI/CD構成（GitHub Actions, pre-commit, テスト自動化）

### 7. Security
- `Security-Security-Overview.md` - セキュリティ設計（Webhook署名検証、APIキー管理、監査ログ）
- `Security-Authentication.md` - 認証実装（Twitch/YouTube/Bluesky/DiscordのAPIキー・パスワード管理）
- `Security-Authorization.md` - アクセス制御（Webhook, Discord通知等）
- `Security-Security-Best-Practices.md` - セキュアコーディング・運用ガイド

## File Naming Convention

GitHub Wikiはフラット構造のため、以下の命名規則を厳守してください。

### ドキュメント命名規則
`Category-SubCategory-PageName.md`
例: `Getting-Started-Development-Setup.md`, `Architecture-Technology-Stack.md`

## Rules

- **正確性・検証性**:
  - 必ず実際のコード・設定ファイル・ドキュメントに基づき記述すること。
  - 技術詳細・仕様・プロセスは必ずリポジトリ内で確認し、推測や未検証の記述は禁止。
  - 不明点は該当ソースを調査し、根拠を明記。
- **フォーマット**: GitHub Flavored Markdownを使用。
  - **Mermaid**: アーキテクチャ・データフロー図はMermaid記法を推奨。
  - **リンク**: セクション内・関連資料へのリンクはMarkdown形式で記載。
    - 例: `[All-ModuleList.md](https://github.com/owner/repo/wiki/All-ModuleList)`
- **一貫性**: 各セクション・ページでフォーマット・スタイルを統一。
- **出典明記**: 情報の根拠となるファイル・行番号はGitHub Permalinkで明記。
  - mainブランチのパーマリンクを使用。
  - 例: `Source: [main.py#L123](https://github.com/owner/repo/blob/main/main.py#L123)`
- **テンプレート・画像・ログ管理**:
  - templates/配下の各サブディレクトリ（niconico, twitch, youtube等）には__init__.txtが必須。削除・リネーム禁止。
  - 画像・テンプレートパスはimages/・templates/以降の相対パスで指定。
  - 投稿履歴（logs/post_history.csv）はGUI・CLI共通で参照・管理。
- **CI/CD・自動テスト**:
  - tests/配下はpytestで自動テスト。pytest.ini, pre-commit, GitHub Actions等のCI/CD構成も明記。
- **コントリビューション**:
  - CONTRIBUTING.ja.mdの内容を参照し、貢献・バグ報告・PR手順・コーディング規約を明記。

---

## アプリケーション概要・主な特徴

- Twitch/YouTube/ニコニコ生放送の放送開始・動画投稿を自動検知し、Blueskyへリアルタイム通知するPython製Botです。
- Cloudflare Tunnelやngrok/localtunnel等のトンネル通信アプリケーションによるWebhook受信・エラー通知・履歴記録など運用に便利な機能を多数搭載。
- GUIからもサーバー・トンネルの起動/停止・状態確認・安全な終了が可能。
- CUI/GUIどちらからでもCtrl+Cや停止ボタンで安全にクリーンアップ・ログ出力・ファイルロック解放がされます。

### 主な機能
- Twitch EventSub Webhookで放送開始/終了を自動検知
- 不要なTwitch EventSubサブスクリプションの自動クリーンアップ
- YouTubeLive/ニコニコ生放送/動画投稿の検知・通知
- トンネル通信アプリケーションの自動起動・URL自動反映・GUI連携
- 設定ファイルやGUIで細かくカスタマイズ可能
- Discordへのエラー通知・通知レベル管理
- ログファイル・コンソール出力のログレベル調整
- APIエラー時の自動リトライ機能
- Bluesky投稿内容のテンプレート切り替え・画像添付・投稿履歴CSV記録
- Webhook署名のタイムスタンプ検証によるリプレイ攻撃対策
- 監査ログの保存機能
- 自動テスト機能（tests/ディレクトリ）
- 拡張性・保守性を考慮したモジュール分割設計

---

## インストール・セットアップ手順

1. **リポジトリをクローン**
   ```
   git clone https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky.git
   cd Twitch-Stream-notify-on-Bluesky
   ```
2. **Pythonパッケージをインストール**
   ```
   pip install -r requirements.txt
   ```
   - 開発者はdevelopment-requirements.txtも利用可能
3. **Cloudflare Tunnel等のトンネル通信アプリケーションをインストール**
   - Cloudflared（Cloudflare Tunnel）は[公式手順](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)参照
   - ngrok/localtunnelは各公式手順参照
4. **トンネル通信アプリケーションをセットアップ**
   - Cloudflare TunnelはZero Trustでトンネル作成・config.yml準備
   - サンプルconfig.ymlはCloudflaredフォルダ内
   - ngrok/localtunnelは各公式手順参照
5. **初期設定**
   - 設定ファイルがない場合は起動時にセットアップウィザードが自動起動
   - GUIのsetup_wizard.pyでBlueskyアカウント等を設定
   - 設定ファイル(settings.env)はGUI/ウィザードで自動生成

---

## カスタマイズ・運用Tips

- 通知レベルやログレベルはsettings.envまたは設定GUIで変更可能
- 投稿履歴はlogs/post_history.csvに自動記録（GUIログビューアからも確認可）
- トンネル通信設定はCloudflare/ngrok/localtunnel/Customに対応
- 投稿テンプレートはtemplates/配下のファイルを切り替え・編集可能
- テンプレートや画像ファイルのパスは相対パス指定（例: templates/xxx.txt, images/xxx.png）
- 監査ログはlogs/audit.logに記録
- APIキーやパスワードは絶対に公開リポジトリに含めないこと

---

## FAQ・トラブルシューティング

- トンネル通信アプリケーションのインストール・設定方法
- テンプレートや画像ファイルのパス指定方法
- Webhook疎通確認方法
- 認証情報の取得方法（Bluesky/Twitch/Discord）
- Bluesky投稿時の画像添付方法
- セキュリティ対策・監査ログの場所
- テストの実行方法（pytest）
- その他詳細はREADME.mdおよびCONTRIBUTING.ja.md参照

---

## 開発・貢献・ライセンス

- mainブランチは直push禁止＆PR必須
- GitGuardianによるシークレットスキャン推奨
- バグ報告・機能提案・PR歓迎（詳細はCONTRIBUTING.ja.md参照）
- 自動テストはpytestで実行可能
- ライセンス: GPL v2
- 作者: まゆにゃ（@mayu0326）
- 連絡先: https://mayunyan.tokyo/contact/personal/

---

このマニュアルに従い、プロジェクトの実装・運用・保守に役立つ高品質なWikiを構築してください。
