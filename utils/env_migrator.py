# -*- coding: utf-8 -*-
"""
settings.env自動マイグレーションスクリプト
- settings.env.example（最新テンプレート）とsettings.env（ユーザー設定）を比較し、
  不足項目を自動追加・説明コメントも補完
- 既存値は維持し、古い不要項目はコメントアウト
- バックアップを自動作成
"""
import os
import shutil

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '../settings.env.example')
USER_PATH = os.path.join(os.path.dirname(__file__), '../settings.env')
BACKUP_PATH = USER_PATH + '.bak'

def parse_env_lines(lines):
    result = {}
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue
        if '=' in line:
            k, v = line.strip().split('=', 1)
            result[k.strip()] = v.strip()
    return result

def migrate_env():
    if not os.path.exists(TEMPLATE_PATH) or not os.path.exists(USER_PATH):
        print('テンプレートまたはユーザーenvファイルが見つかりません')
        return
    with open(TEMPLATE_PATH, encoding='utf-8') as f:
        template_lines = f.readlines()
    with open(USER_PATH, encoding='utf-8') as f:
        user_lines = f.readlines()
    template_kv = parse_env_lines(template_lines)
    user_kv = parse_env_lines(user_lines)
    # バックアップ
    shutil.copy2(USER_PATH, BACKUP_PATH)
    print(f'バックアップ作成: {BACKUP_PATH}')
    # 新しいenvを構築
    new_lines = []
    for line in template_lines:
        if not line.strip() or line.strip().startswith('#'):
            new_lines.append(line)
            continue
        if '=' in line:
            k = line.split('=', 1)[0].strip()
            v = user_kv.get(k, template_kv[k])
            new_lines.append(f'{k}={v}\n')
    # ユーザーenvにしかない古い項目はコメントアウトして追記
    for k in user_kv:
        if k not in template_kv:
            new_lines.append(f'# (旧項目) {k}={user_kv[k]}\n')
    with open(USER_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print('settings.envを最新仕様に自動マイグレーションしました')

if __name__ == '__main__':
    migrate_env()
