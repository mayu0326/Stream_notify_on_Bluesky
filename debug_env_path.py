# debug_env_path.py
import inspect
import os

def debug_env_access(env_path, mode='read'):
    """
    settings.envのアクセスパスをデバッグ出力。
    mode: 'read' or 'write'
    env_path: 実際に参照・書き込みしようとしている絶対パス
    """
    frame = inspect.currentframe().f_back
    filename = os.path.basename(frame.f_code.co_filename)
    funcname = frame.f_code.co_name
    print(f"[DEBUG][settings.env {mode}] {filename}:{funcname} -> {env_path}")
