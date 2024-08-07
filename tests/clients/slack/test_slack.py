import pytest
import os

from src.clients.slack.client import SlackClient


@pytest.fixture
def fixture(mocker):
    MockSlackWebClient = mocker.patch("src.clients.slack.client.WebClient")

    return MockSlackWebClient


def test_find_user_by_email(mocker, fixture):

    mock_client = fixture.return_value

    mock_client.users_lookupByEmail.return_value = {
        "ok": True,
        "user": {
            "id": "U01B2AB3D",
            "name": "elliot",
            "real_name": "Elliot Reid",
        },
    }

    slack_client = SlackClient(token="xoxb-123")
    response = slack_client.find_user_by_email(email="elliot.reid@sacredheart.com")

    assert response == "U01B2AB3D"


def test_find_user_by_email_with_exception(mocker, fixture):
    mock_client = fixture.return_value

    mock_client.users_lookupByEmail.return_value = {
        "ok": False,
        "error": "user_not_found",
    }

    slack_client = SlackClient(token="xoxb-123")

    with pytest.raises(Exception) as e:
        slack_client.find_user_by_email(email="allison@princetonplainsboro.health")


def test_send_dm_to_user(mocker, fixture):
    mock_client = fixture.return_value

    slack_client = SlackClient(token="xoxb-123")
    slack_client.send_dm_to_user(user_id="U01B2AB3D", message="Hello, Elliot!")

    mock_client.chat_postMessage.assert_called_once_with(
        channel="U01B2AB3D", text="Hello, Elliot!"
    )


def test_send_dm_to_user_with_exception(mocker, fixture):
    mock_client = fixture.return_value

    mock_client.chat_postMessage.side_effect = Exception("Failed to send message")

    slack_client = SlackClient(token="xoxb-123")

    with pytest.raises(Exception) as e:
        slack_client.send_dm_to_user(user_id="U01B2AB3D", message="Hello, Elliot!")

def test_send_mpdm_to_users(mocker, fixture):
    mock_client = fixture.return_value

    mock_client.conversations_open.return_value = {
        "ok": True,
        "channel": {"id": "C01B2AB3D"},
    }

    slack_client = SlackClient(token="xoxb-123")
    slack_client.send_mpdm_to_users(user_ids=["U01B2AB3D", "U01B2AB3E"], message="Hello, Elliot!")

    mock_client.conversations_open.assert_called_once_with(users=["U01B2AB3D", "U01B2AB3E"])
    mock_client.chat_postMessage.assert_called_once_with(channel="C01B2AB3D", text="Hello, Elliot!")
