# Stream notify on Bluesky - Docker利用手順

このプロジェクトをDockerで動かすための手順・注意点をまとめます。

## 必要なもの
- Docker Desktop（Windows/Mac）またはDocker Engine（Linux）
- このリポジトリのクローン
- `settings.env`（`settings.env.example`をコピーして必要な値を設定）
- 必要に応じてCloudflared/ngrok/localtunnel等の外部トンネルサービス

## ビルド手順
1. プロジェクトルートに移動
2. 下記コマンドでDockerイメージをビルド

```powershell
# PowerShell例（カレントディレクトリがプロジェクトルートの場合）
docker build -t streamnotify-bluesky .
```

## 起動手順
1. `settings.env`を編集し、必要なAPIキーやトンネル設定を記入
2. 下記コマンドでコンテナを起動

```powershell
docker run --rm -it -p 3000:3000 --env-file settings.env streamnotify-bluesky
```
- `-p 3000:3000` でホストの3000番ポートをコンテナに割り当て
- `--env-file settings.env` で環境変数を渡す

## 注意事項
- `settings.env`は必須です。`settings.env.example`をコピーして編集してください。
- トンネルサービス（Cloudflare/ngrok/localtunnel等）はホスト側で起動・設定が必要な場合があります。
- Windows環境での日本語ファイル名やパスに注意してください。
- GUI機能はDocker上では利用できません（CUIサーバーのみ）。

## よくあるトラブル
- ポート競合: 既に3000番ポートが使われている場合は`-p`の値を変更してください。
- トンネルが動かない: トンネルコマンドやAPIキーの設定を再確認してください。
- Pythonバージョン: Dockerfileは`python:3.13-slim`を使用しています。

---

詳細な設定や運用方法は`README.md`や`document/`配下のドキュメントも参照してください。
