## 1. `pytest` および `autopep8` の問題点と推奨事項：

### GitHub Actions を利用した `pytest` の設定：
*   **CI環境：** アプリケーションはWindows専用（例：cloudflared.exeのパス規約、Tkinter GUI連携）であるため、GitHub Actionsでは`windows-latest`で`pytest`を実行するように設定します。
*   **CIでのcloudflaredのセットアップ：**
    *   CIワークフローにcloudflared.exeのダウンロード・インストール手順を含めます。
    *   settings.env（またはCI用の同等物）のTUNNEL_CMDは、CIランナー内のcloudflared.exeの場所を指す必要があります。
    *   実際のトンネル接続はCIで完全にテストするのは困難なため、ボットがトンネルコマンドを呼び出し、プロセスを管理できるかのテストに重点を置きます。
    *   現状はCloudflare Tunnel以外にもngrok/localtunnel/customコマンドに対応。
    *   TUNNEL_SERVICE環境変数でサービスを切り替え、各種コマンド（TUNNEL_CMD/NGROK_CMD/LOCALTUNNEL_CMD/CUSTOM_TUNNEL_CMD）でトンネルを起動・管理。
    *   コマンド未設定時は警告ログを出し、起動しない。終了時はterminate/waitで正常終了、タイムアウトや例外時はkillで強制終了し、詳細なログを出力。）
*   **シークレットを介したsettings.envの管理：**
    *   実際のsettings.envファイルはコミットしない。
    *   GitHub Actionsではリポジトリシークレットを使い、CIセットアップ時に一時的なsettings.envを生成するか、
    *   python-dotenvのos.environフォールバックを活用。
    *   ローカル開発では.gitignoreされたsettings.envを各自管理。
*   **pathlibの使用：**
    *   ファイルパス操作（BLUESKY_IMAGE_PATH、BLUESKY_TEMPLATE_PATH、ログファイル、config.yml等）はpathlib.Pathで統一し、
    *   クロスプラットフォーム互換性と可読性を向上。

### autopep8：
*   **pre-commitとの統合：** autopep8（またはBlack/Ruffなど）をpre-commitフックに統合し、コミット前に自動フォーマット。
*   **詳細なチェックと問題のあるコード：** autopep8がうまく機能しない場合は--diffや詳細オプションで問題箇所を特定し、必要に応じて手動修正。
*   **アップデート：** autopep8や関連ツールは常に最新に保つ。Ruff等の高速リンター/フォーマッターの導入も検討。

## 2. GUIの必要性・現状：

*   現状はTkinterベースのGUI（app_gui.py等）で、settings.envと双方向連携し、\
     各サービスごとのテンプレート・画像・Webhook・APIキー等を個別に管理可能。
*   コマンドライン（CUI）とGUIの両方に対応し、ユーザーの技術レベルに応じて選択可能。
*   GUIからサーバー・トンネルの起動/停止・状態確認・安全な終了・クリーンアップが可能。
*   CUI/GUIどちらでも、終了時に必ずクリーンアップ・ログ出力・ファイルロック解放が保証される。\
    異常終了時もログが残る。
*   今後の開発リソースは、堅牢性・エラー処理・自動テスト・CI/CD強化に優先配分。
*   GUIはユーザーベース拡大や要望に応じて今後も拡張可能。

## 3. CI/CD・自動テスト・保守運用の補助モジュール・注意事項

*   本リポジトリでは、CI/CDや自動テストの堅牢化・保守性向上のため、以下の補助モジュール・運用ルールを導入しています。
    *   **cleanup.py:** アプリケーション終了時のクリーンアップ処理・リソース解放を担い、CI/CDや異常終了時も安定運用を支援。
    *   **service_monitor.py:** サービス状態監視・ヘルスチェックを自動化し、CI/CDや運用時の異常検知・通知に活用。
    *   **webhook_routes.py:** Webhookエンドポイントのルーティング・受信処理を分離し、テスト容易性・保守性を向上。
    *   **logs/post_history.csv:** Bluesky投稿履歴をCSVで記録し、GUI・CLI・CI/CD共通で監査・検証可能。
    *   **gui/template_editor_dialog.py:** GUI上でテンプレート編集・保存・プレビューを実現し、ユーザビリティとテスト容易性を両立。
    *   **templates/サブディレクトリ・__init__.txt:** テンプレートサブディレクトリ（niconico, twitch, youtube等）には__init__.txt（システム管理用）が必須。\
    削除・リネーム・空ディレクトリ化はCI/CD・自動テスト・運用時の動作不良の原因となるため厳禁。
    *   **All-ModuleList.mdやREADME.md:** モジュール・ファイルリストはA-Z順で整理し、保守性・CI/CD自動チェックの観点からも重要。
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
