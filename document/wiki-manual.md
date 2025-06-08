# Stream notify on Bluesky Wiki Construction Manual

## Purpose
このマニュアルは「Stream notify on Bluesky」プロジェクトのためのエンドユーザー向けGitHub Wikiを構築する標準手順です。  
実際の実装・運用・画面・FAQ・トラブル対応に即し、一般利用者が迷わず使える内容を重視します。

## 推奨Wiki構成（2025年6月時点の実態に即した例）

### 1. Home Page (`Home.md`)
- プロジェクトの概要・主な特徴
- クイックナビゲーション（セットアップ・使い方・FAQ・テンプレート変数）
- GitHubリポジトリ等の主要リソースへのリンク
- 技術者向け情報はGitHubリポジトリのドキュメント等に誘導

### 2. Getting Started
- `Getting-Started-Setup.md` … Windows専用のインストール・セットアップ手順（Python/Git/Cloudflared等の導入、初期設定、トンネル運用の注意点も含む）

### 3. User Manual
- `User-Manual-GUI.md` … GUI画面の使い方・各タブの説明・初回セットアップ・テンプレート/画像管理・トンネル設定・エラー時の挙動・Tips・よくある質問・トラブル対応まで一貫して記載

### 4. FAQ・トラブルシューティング
- `FAQ.md` … よくある質問・トラブル事例・対処法を一元化

### 5. テンプレート変数リスト
- `Template-Arguments.md` … 投稿テンプレートで使える変数一覧（Twitch/YouTube/ニコニコ等サービス別）

### 6. 参考・補助ページ（必要に応じて）
- `Explanation-of-configuration-files.md` … 設定ファイル（settings.env等）の詳細解説
- `File-folder-structure.md` … フォルダ・ファイル構成の説明
- `Glossary.md` … 用語集
- `Testing.md` … テスト方法（一般ユーザーが手動で動作確認する場合のみ）

---

## 命名規則・ルール
- ページ名・リンクは必ず現存するファイル名・内容に合わせること
- 技術者向け・開発/テスト/アーキテクチャ系ページはエンドユーザー向けWikiからは除外
- 内容は必ず実装・画面・運用実態に即し、推測や未検証の記述は禁止
- Markdown形式、見出し・リスト・リンク等はGitHub Flavored Markdownに準拠
- 画面例・操作例・注意点・FAQ・Tipsはできるだけ具体的・実用的に
- 詳細な技術情報や開発者向け情報はGitHubリポジトリのドキュメント（ARCHITECTURE.ja.md, CONTRIBUTING.ja.md等）に誘導

---

## 参考：エンドユーザー向け主要ページ例
- Home.md
- Getting-Started-Setup.md
- User-Manual-GUI.md
- FAQ.md
- Template-Arguments.md
- Explanation-of-configuration-files.md
- File-folder-structure.md
- Glossary.md

---

このマニュアルに従い、エンドユーザーが迷わず使える高品質なWikiを構築してください。
