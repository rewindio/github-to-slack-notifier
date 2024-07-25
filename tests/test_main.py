import pytest
import os

from main import run
from exceptions import SlackUserNotFoundException
from clients.github.graphql import GithubGraphqlClient
from clients.slack.client import SlackClient


def test_input_validation_missing_required():
    os.environ["INPUT_GITHUB_TOKEN"] = "gh"
    os.environ["INPUT_SLACK_BOT_TOKEN"] = "xoxb-123"
    os.environ["INPUT_LIST_OF_GITHUB_USERS"] = '["jan_itor","luuuucy"]'

    with pytest.raises(SystemExit) as e:
        run()

    assert e.value.code == 2

    del os.environ["INPUT_GITHUB_TOKEN"]
    del os.environ["INPUT_SLACK_BOT_TOKEN"]
    del os.environ["INPUT_LIST_OF_GITHUB_USERS"]


def test_run_no_slack_id(mocker):
    mocker.patch(
        "os.getenv",
        side_effect=lambda var: {
            "INPUT_GITHUB_TOKEN": "gh",
            "INPUT_SLACK_BOT_TOKEN": "xoxb",
            "INPUT_LIST_OF_GITHUB_USERS": '["jordan_sullivan"]',
            "INPUT_GITHUB_ORG": "sacred_heart",
            "INPUT_MESSAGE": "Hooch is crazy!",
        }.get(var),
    )

    mocker.patch(
        "clients.github.graphql.GithubGraphqlClient.get_corporate_emails_for_user",
        return_value=["jsulliavan@sacredheart.com", "jordan_sullivan@sacredheart.com"],
    )
    mocker.patch("clients.slack.client.SlackClient.send_dm_to_user", return_value=None)
    mocker.patch(
        "clients.slack.client.SlackClient.find_user_by_email",
        side_effect=SlackUserNotFoundException,
    )

    with pytest.raises(SystemExit) as e:
        run()

    assert e.value.code == 1
    assert SlackClient.send_dm_to_user.call_count == 0


def test_run_all_env_vars_present(mocker):
    mocker.patch(
        "os.getenv",
        side_effect=lambda var: {
            "INPUT_GITHUB_TOKEN": "gh",
            "INPUT_SLACK_BOT_TOKEN": "xoxb",
            "INPUT_LIST_OF_GITHUB_USERS": '["vanillabear"]',
            "INPUT_GITHUB_ORG": "sacred_heart",
            "INPUT_MESSAGE": "Hooch is crazy!",
        }.get(var),
    )

    mocker.patch(
        "clients.github.graphql.GithubGraphqlClient.get_corporate_emails_for_user",
        return_value=["jd@sacredheart.com"],
    )

    mocker.patch(
        "clients.slack.client.SlackClient.find_user_by_email", return_value="jd"
    )
    mocker.patch("clients.slack.client.SlackClient.send_dm_to_user", return_value=None)

    run()

    GithubGraphqlClient.get_corporate_emails_for_user.assert_called_once_with(
        "vanillabear"
    )
    SlackClient.find_user_by_email.assert_called_once_with("jd@sacredheart.com")
    SlackClient.send_dm_to_user.assert_called_once_with("jd", "Hooch is crazy!")
