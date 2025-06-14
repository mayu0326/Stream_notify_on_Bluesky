# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

from datetime import datetime
from utils import retry_on_exception, is_valid_url, notify_discord_error
# is_valid_url: URLがhttp/httpsで始まるか判定するユーティリティ関数。他モジュールからも利用されるため削除不可。
import os
import csv
import logging
from atproto import Client, exceptions
from jinja2 import Environment, Template
from utils import format_datetime_filter
from version_info import __version__

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__

# Stream notify on Bluesky
# Copyright (C) 2025 mayuneco(mayunya)
#
# このプログラムはフリーソフトウェアです。フリーソフトウェア財団によって発行された
# GNU 一般公衆利用許諾契約書（バージョン2またはそれ以降）に基づき、再配布または
# 改変することができます。
#
# このプログラムは有用であることを願って配布されていますが、
# 商品性や特定目的への適合性についての保証はありません。
# 詳細はGNU一般公衆利用許諾契約書をご覧ください。
#
# このプログラムとともにGNU一般公衆利用許諾契約書が配布されているはずです。
# もし同梱されていない場合は、フリーソフトウェア財団までご請求ください。
# 住所: 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

# リトライ回数のデフォルト値を環境変数から取得
RETRY_MAX = int(os.getenv("RETRY_MAX", 3))
RETRY_WAIT = int(os.getenv("RETRY_WAIT", 2))

# アプリケーション用ロガー
logger = logging.getLogger("AppLogger")

# デフォルトテンプレートパス（ユーザーが直接触れない内部用・不可視ファイル）
DEFAULT_ONLINE_TEMPLATE_PATH = ".templates/default_online_template.txt"
DEFAULT_OFFLINE_TEMPLATE_PATH = ".templates/default_offline_template.txt"


def load_template(path=None):
    """
    テンプレートファイルを読み込み、Jinja2 Templateオブジェクトを返す
    """
    template_string = ""
    if path is None:
        path = DEFAULT_ONLINE_TEMPLATE_PATH
        logger.warning(
            f"load_templateにパスが指定されませんでした。デフォルトのオンラインテンプレートパス '{path}' を使用します。")

    try:
        with open(path, encoding="utf-8") as f:
            template_string = f.read()
    except FileNotFoundError:
        logger.error(
            f"テンプレートファイルが見つかりません: {path}. フォールバックエラーテンプレートを使用します。"
        )
        template_string = "Error: Template '{{ template_path }}' not found. Please check settings."
    except Exception as e:
        logger.error(f"テンプレート '{path}' の読み込み中に予期せぬエラー: {e}", exc_info=True)
        template_string = "Error: Failed to load template '{{ template_path }}' due to an unexpected error."

    # Jinja2 Environmentを使い、グローバルにフィルターを登録
    env = Environment()
    env.filters['datetimeformat'] = format_datetime_filter
    template_obj = env.from_string(template_string)
    return template_obj


# 監査用ロガー
audit_logger = logging.getLogger("AuditLogger")


class BlueskyPoster:
    def __init__(self, username, password):
        # Blueskyクライアントの初期化
        self.client = Client()
        self.username = username
        self.password = password

    def upload_image(self, image_path):
        """
        画像ファイルをBlueskyにアップロードし、blob情報を返す
        """
        try:
            with open(image_path, "rb") as img_file:
                img_bytes = img_file.read()
            blob = self.client.upload_blob(img_bytes)
            return blob
        except FileNotFoundError:
            logger.error(f"Bluesky画像アップロードエラー: ファイルが見つかりません - {image_path}")
            return None
        except Exception as e:
            logger.error(
                f"Bluesky画像アップロード中に予期せぬエラーが発生しました: {image_path}, エラー: {e}", exc_info=e)
            return None

    @retry_on_exception(
        max_retries=RETRY_MAX,
        wait_seconds=RETRY_WAIT,
        exceptions=(exceptions.AtProtocolError,)
    )
    def post_stream_online(self, event_context: dict, image_path=None, platform="twitch"):
        """
        配信開始通知をBlueskyに投稿する（Twitch/YouTube/ニコニコ対応）
        """
        # テンプレートパスの決定
        if platform == "twitch":
            template_path = os.getenv(
                "BLUESKY_TW_ONLINE_TEMPLATE_PATH", "templates/twitch_online_template.txt")
            required_keys = ["title", "category_name", "stream_url",
                             "broadcaster_user_login", "broadcaster_user_name"]
        elif platform == "youtube" or platform == "yt_nico":
            template_path = os.getenv(
                "BLUESKY_YT_ONLINE_TEMPLATE_PATH", "templates/yt_online_template.txt")
            required_keys = ["title", "stream_url", "channel_id", "channel_name"]
        elif platform == "niconico":
            template_path = os.getenv(
                "BLUESKY_NICO_ONLINE_TEMPLATE_PATH", "templates/nico_online_template.txt")
            required_keys = ["title", "stream_url", "channel_id", "channel_name"]
        else:
            # 内部デフォルト用途
            template_path = os.getenv(
                "BLUESKY_TW_ONLINE_TEMPLATE_PATH", ".templates/default_offline_template.txt")
            required_keys = ["title", "stream_url"]

        # テンプレートファイルがなければデフォルトテンプレートにフォールバック
        if not template_path or not os.path.isfile(template_path):
            logger.warning(f"配信開始テンプレートファイルが見つかりません: {template_path}. デフォルトテンプレートにフォールバックします。")
            template_path = DEFAULT_ONLINE_TEMPLATE_PATH

        template_obj = load_template(path=template_path)

        # 必須キーのチェック
        missing_keys = [
            key for key in required_keys if key not in event_context or event_context[key] is None]
        if missing_keys:
            logger.warning(
                f"Blueskyオンライン投稿の入力event_contextが不正です。不足キー: {', '.join(missing_keys)}")
            return False

        success = False

        try:
            # Blueskyへログイン
            self.client.login(self.username, self.password)

            # テンプレートをレンダリングして投稿本文を生成
            post_text = template_obj.render(
                **event_context, template_path=template_path)

            embed = None
            # 画像パスが指定されている場合は画像をアップロード
            if image_path and os.path.isfile(image_path):
                blob = self.upload_image(image_path)
                if blob:
                    embed = {
                        "$type": "app.bsky.embed.images",
                        "images": [
                            {
                                "alt": f"{
                                    event_context.get(
                                        'title',
                                        event_context.get(
                                            'broadcaster_user_name',
                                            'Stream Image'))[
                                        :250]}",
                                "image": blob}]}
                else:
                    logger.warning(
                        f"画像 '{image_path}' のアップロードに失敗したため、画像なしで投稿します。")
            elif image_path and not os.path.isfile(image_path):
                logger.warning(
                    f"指定された画像ファイルが見つかりません: {image_path}。画像なしで投稿します。")

            # Blueskyに投稿
            self.client.send_post(post_text, embed=embed)
            logger.info(
                f"Blueskyへの自動投稿に成功しました (stream.online): {event_context.get('stream_url')}")
            audit_logger.info(
                f"Bluesky投稿成功 (stream.online): URL - {event_context.get('stream_url')}, Title - {event_context.get('title')}")
            success = True
            return True
        except exceptions.AtProtocolError as e:
            logger.error(
                f"Bluesky APIエラー (stream.online投稿): {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(
                f"Bluesky投稿中 (stream.online)に予期せぬエラーが発生しました: {e}", exc_info=e)
            notify_discord_error(f"Bluesky投稿エラー: {e}")
            return False
        finally:
            # 投稿履歴を記録
            self._write_post_history(
                title=event_context.get("title", "N/A"),
                category=event_context.get(
                    "category_name", event_context.get("game_name", "N/A")),
                url=event_context.get(
                    "stream_url", f"https://twitch.tv/{event_context.get('broadcaster_user_login', '')}"),
                success=success,
                event_type="online"
            )

    @retry_on_exception(
        max_retries=RETRY_MAX,
        wait_seconds=RETRY_WAIT,
        exceptions=(exceptions.AtProtocolError,)
    )
    def post_stream_offline(self, event_context: dict, image_path=None, platform="twitch", template_path=None):
        """
        配信終了通知をBlueskyに投稿する（Twitch/YouTube/ニコニコ対応）
        """
        # --- Raid終了時やchannel.raid用のテンプレートパス指定に対応 ---
        if not template_path:
            if platform == "twitch":
                template_path = os.getenv(
                    "BLUESKY_TW_OFFLINE_TEMPLATE_PATH", "templates/twitch_offline_template.txt")
            elif platform == "youtube" or platform == "yt_nico":
                template_path = os.getenv(
                    "BLUESKY_YT_OFFLINE_TEMPLATE_PATH", "templates/yt_offline_template.txt")
            elif platform == "niconico":
                template_path = os.getenv(
                    "BLUESKY_NICO_OFFLINE_TEMPLATE_PATH", "templates/nico_offline_template.txt")
            else:
                template_path = os.getenv(
                    "BLUESKY_TW_OFFLINE_TEMPLATE_PATH", "templates/twitch_offline_template.txt")
        # --- 必須キー: 通常終了 or Raid終了で分岐 ---
        if template_path and "raid" in template_path:
            # Raidテンプレート用
            required_keys = [
                "from_broadcaster_user_name", "from_broadcaster_user_login", "to_broadcaster_user_name", "to_broadcaster_user_login", "raid_url"
            ]
        else:
            # 通常の配信終了
            required_keys = ["broadcaster_user_name", "broadcaster_user_login", "channel_url"]
        # テンプレートファイルがなければデフォルトテンプレートにフォールバック
        if not template_path or not os.path.isfile(template_path):
            logger.warning(f"配信終了テンプレートファイルが見つかりません: {template_path}. デフォルトテンプレートにフォールバックします。")
            template_path = DEFAULT_OFFLINE_TEMPLATE_PATH
        template_obj = load_template(path=template_path)

        # 必須キーのチェック
        missing_keys = [
            key for key in required_keys if key not in event_context or event_context[key] is None]
        if missing_keys:
            logger.warning(
                f"Blueskyオフライン投稿の入力event_contextが不正です。不足キー: {', '.join(missing_keys)}")
            return False

        success = False
        try:
            # Blueskyへログイン
            self.client.login(self.username, self.password)
            # テンプレートをレンダリングして投稿本文を生成
            post_text = template_obj.render(
                **event_context, template_path=template_path)

            # 画像なしで投稿
            self.client.send_post(text=post_text)
            logger.info(
                f"Blueskyへの自動投稿成功 (stream.offline): {event_context.get('broadcaster_user_name', event_context.get('from_broadcaster_user_name', 'N/A'))}")
            audit_logger.info(
                f"Bluesky投稿成功 (stream.offline): User - {event_context.get('broadcaster_user_name', event_context.get('from_broadcaster_user_name', 'N/A'))}")
            success = True
            return True
        except exceptions.AtProtocolError as e:
            logger.error(
                f"Bluesky APIエラー (stream.offline投稿): {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(
                f"Bluesky投稿中 (stream.offline)に予期せぬエラーが発生しました: {e}", exc_info=e)
            notify_discord_error(f"Bluesky投稿エラー: {e}")
            return False
        finally:
            # 投稿履歴を記録
            self._write_post_history(
                title=f"配信終了: {event_context.get('broadcaster_user_name', event_context.get('from_broadcaster_user_name', 'N/A'))}",
                category="Offline",
                url=event_context.get(
                    "channel_url", event_context.get("raid_url", f"https://twitch.tv/{event_context.get('broadcaster_user_login', event_context.get('to_broadcaster_user_login', ''))}")),
                success=success,
                event_type="offline"
            )

    @retry_on_exception(
        max_retries=RETRY_MAX,
        wait_seconds=RETRY_WAIT,
        exceptions=(exceptions.AtProtocolError,)
    )
    def post_new_video(self, event_context: dict, image_path=None, platform=None):
        """
        新着動画投稿をBlueskyに投稿する（YouTube/ニコニコ用）
        """
        if platform == "youtube":
            template_path = os.getenv(
                "BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH", "templates/yt_new_video_template.txt")
        elif platform == "niconico":
            template_path = os.getenv(
                "BLUESKY_NICO_NEW_VIDEO_TEMPLATE_PATH", "templates/nico_new_video_template.txt")
        else:
            template_path = os.getenv(
                "BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH", "templates/yt_new_video_template.txt")
        # テンプレートファイルがなければデフォルトテンプレートにフォールバック
        if not template_path or not os.path.isfile(template_path):
            logger.warning(f"新着動画テンプレートファイルが見つかりません: {template_path}. デフォルトテンプレートにフォールバックします。")
            template_path = DEFAULT_ONLINE_TEMPLATE_PATH
        template_obj = load_template(path=template_path)

        # 必須キーのチェック
        required_keys = ["title", "video_id", "video_url"]
        missing_keys = [
            key for key in required_keys if key not in event_context or event_context[key] is None]
        if missing_keys:
            logger.warning(
                f"Bluesky新着動画投稿の入力event_contextが不正です。不足キー: {', '.join(missing_keys)}")
            return False

        success = False
        try:
            # Blueskyへログイン
            self.client.login(self.username, self.password)
            # テンプレートをレンダリングして投稿本文を生成
            post_text = template_obj.render(
                **event_context, template_path=template_path)

            embed = None
            # 画像パスが指定されている場合は画像をアップロード
            if image_path and os.path.isfile(image_path):
                blob = self.upload_image(image_path)
                if blob:
                    embed = {
                        "$type": "app.bsky.embed.images",
                        "images": [
                            {
                                "alt": f"{event_context.get('title', 'New Video')[:250]}",
                                "image": blob
                            }
                        ]
                    }
                else:
                    logger.warning(
                        f"画像 '{image_path}' のアップロードに失敗したため、画像なしで投稿します。")
            elif image_path and not os.path.isfile(image_path):
                logger.warning(
                    f"指定された画像ファイルが見つかりません: {image_path}。画像なしで投稿します。")

            # Blueskyに投稿
            self.client.send_post(post_text, embed=embed)
            logger.info(
                f"Blueskyへの自動投稿に成功しました (new_video): {event_context.get('video_url')}")
            audit_logger.info(
                f"Bluesky投稿成功 (new_video): URL - {event_context.get('video_url')}, Title - {event_context.get('title')}")
            success = True
            return True
        except exceptions.AtProtocolError as e:
            logger.error(f"Bluesky APIエラー (new_video投稿): {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(
                f"Bluesky投稿中 (new_video)に予期せぬエラーが発生しました: {e}", exc_info=e)
            notify_discord_error(f"Bluesky投稿エラー: {e}")
            return False
        finally:
            # 投稿履歴を記録
            self._write_post_history(
                title=event_context.get("title", "N/A"),
                category="NewVideo",
                url=event_context.get("video_url", "N/A"),
                success=success,
                event_type="new_video"
            )

    def _write_post_history(
            self,
            title: str,
            category: str,
            url: str,
            success: bool,
            event_type: str):
        """
        投稿履歴をCSVファイルに記録する
        """
        os.makedirs("logs", exist_ok=True)
        csv_path = "logs/post_history.csv"
        is_new_file = not os.path.exists(csv_path)

        try:
            with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                if is_new_file:
                    writer.writerow(
                        ["日時", "イベントタイプ", "タイトル", "カテゴリ", "URL", "成功"])

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                writer.writerow(
                    [
                        current_time,
                        event_type,
                        title,
                        category,
                        url,
                        "○" if success else "×",
                    ]
                )
        except IOError as e:
            logger.error(
                f"投稿履歴CSVへの書き込みに失敗しました: {csv_path}, エラー: {e}", exc_info=e)
        except Exception as e:
            logger.error(
                f"投稿履歴CSVへの書き込み中に予期せぬエラーが発生しました: {csv_path}, エラー: {e}", exc_info=e)
