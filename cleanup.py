import sys

def cleanup_application():
    import logging
    logger = logging.getLogger("AppLogger")
    # トンネル・監視スレッド・ロガーのクリーンアップ処理をここに記述
    logger.info("アプリケーションのクリーンアップ処理を開始します。")
    # ...（main.py cleanup_applicationの内容をここに移植）...
    logger.info("アプリケーションのクリーンアップ処理が完了しました。")

def cleanup_from_gui():
    cleanup_application()

def signal_handler(sig, frame):
    import logging
    logger = logging.getLogger("AppLogger")
    logger.info(f"シグナル {sig} を受信しました。アプリケーションを終了します。")
    cleanup_application()
    sys.exit(0)
