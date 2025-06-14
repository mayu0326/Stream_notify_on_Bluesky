# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky - Integration Tests
"""
import pytest
from unittest.mock import patch, MagicMock
import jinja2
import utils
import utils.utils
from tunnel import start_tunnel, stop_tunnel


# pytestの警告抑制: mark.integration
pytestmark = pytest.mark.filterwarnings(
    r"ignore:Unknown pytest\.mark\.integration",
)


# Flaskアプリを利用
from main import app


@pytest.fixture
def test_client():
    from main import app
    app.config['TESTING'] = True
    yield app



# jinja2のグローバルフィルタにformat_datetime_filterを登録
jinja2.filters.FILTERS['datetimeformat'] = utils.utils.format_datetime_filter


# MainAppの依存性注入を適用し、mock_blueskyを正しく参照
@pytest.mark.integration
def test_full_notification_flow(test_client):
    """完全な通知フローのテスト"""
    app = test_client
    with patch('bluesky.BlueskyPoster') as mock_bluesky_cls, \
         patch('tunnel.subprocess.Popen'):
        proc = start_tunnel()
        poster = MagicMock()
        poster.post_stream_online.return_value = True
        poster.post_stream_offline.return_value = True
        mock_bluesky_cls.side_effect = lambda *args, **kwargs: poster
        # 必要な環境変数をセット
        with patch.dict('os.environ', {
            "BLUESKY_USERNAME": "dummyuser",
            "BLUESKY_APP_PASSWORD": "dummypass",
            "BLUESKY_TW_ONLINE_TEMPLATE_PATH": "templates/twitch_online_template.txt",
            "NOTIFY_ON_TWITCH_OFFLINE": "true",
            "NOTIFY_ON_TWITCH_ONLINE": "True"
        }):
            # verify_signature を常に True にする
            with patch('eventsub.verify_signature', return_value=True):
                try:
                    # ストリーム開始通知
                    with app.test_client() as client:
                        response = client.post('/webhook',
                                               json={
                                                   'subscription': {'type': 'stream.online'},
                                                   'event': {
                                                       'broadcaster_user_login': 'testuser',
                                                       'broadcaster_user_name': 'Test User',
                                                       'started_at': '2024-03-20T12:00:00Z',
                                                       'title': 'テスト配信',
                                                       'category_name': 'ゲーム',
                                                       'broadcaster_user_id': '12345'
                                                   }
                                               },
                                               headers={
                                                   "Twitch-Eventsub-Message-Type": "notification",
                                                   "Twitch-Eventsub-Message-Id": "dummy-id",
                                                   "Twitch-Eventsub-Message-Timestamp": "2024-05-26T13:45:00Z",
                                                   "Twitch-Eventsub-Message-Signature": "sha256=dummy"
                                               }
                                               )
                        assert response.status_code == 200
                        assert response.get_json()["status"] == "success"
                        # ストリーム終了通知
                        response = client.post('/webhook',
                                               json={
                                                   'subscription': {'type': 'stream.offline'},
                                                   'event': {
                                                       'broadcaster_user_login': 'testuser',
                                                       'broadcaster_user_name': 'Test User',
                                                       'broadcaster_user_id': '12345'
                                                   }
                                               },
                                               headers={
                                                   "Twitch-Eventsub-Message-Type": "notification",
                                                   "Twitch-Eventsub-Message-Id": "dummy-id",
                                                   "Twitch-Eventsub-Message-Timestamp": "2024-05-26T13:45:00Z",
                                                   "Twitch-Eventsub-Message-Signature": "sha256=dummy"
                                               }
                                               )
                        assert response.status_code == 200
                        assert response.get_json()["status"].startswith("success")
                finally:
                    # トンネル停止
                    stop_tunnel(proc)
