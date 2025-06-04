# syntax=docker/dockerfile:1

# ベースイメージ
FROM python:3.13-slim

# 作業ディレクトリ作成
WORKDIR /app

# 依存ファイルをコピー
COPY requirements.txt ./

# 依存パッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体をコピー
COPY . .

# ポート開放（CherryPyのデフォルト3000番）
EXPOSE 3000

# 環境変数（必要に応じて）
ENV TZ=Asia/Tokyo

# Node.jsインストール
RUN apt-get update \
    && apt-get install -y curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# localtunnel, ngrok, cloudflared インストール
RUN npm install -g localtunnel \
    && curl -fsSL https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.tgz | tar xz -C /usr/local/bin \
    && mv /usr/local/bin/ngrok /usr/local/bin/ngrok \
    && curl -L -o /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    && chmod +x /usr/local/bin/cloudflared

# 起動コマンド
CMD ["python", "main.py"]
