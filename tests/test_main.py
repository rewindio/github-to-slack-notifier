import pytest
import os
import src

from src import main, clients
from src.clients.github.graphql import GithubGraphqlClient
from src.clients.slack.client import SlackClient


def test_input_validation_missing_required():
    os.environ["INPUT_GITHUB_TOKEN"] = "gh"
    os.environ["INPUT_SLACK_TOKEN"] = "xoxb-123"
    os.environ["INPUT_LIST_OF_GITHUB_USER"] = '["jan_itor","luuuucy"]'

    with pytest.raises(SystemExit) as e:
        main.run()

    assert e.value.code == 2

    del os.environ["INPUT_GITHUB_TOKEN"]
    del os.environ["INPUT_SLACK_TOKEN"]
    del os.environ["INPUT_LIST_OF_GITHUB_USER"]


def test_run_all_env_vars_present(mocker):
    mocker.patch(
        "os.getenv",
        side_effect=lambda var: {
            "INPUT_GITHUB_TOKEN": "gh",
            "INPUT_SLACK_TOKEN": "xoxb",
            "INPUT_LIST_OF_GITHUB_USER": '["vanillabear"]',
            "INPUT_GITHUB_ORG": "sacred_heart",
            "INPUT_MESSAGE": "Hooch is crazy!",
        }.get(var),
    )

    mocker.patch(
        "src.clients.github.graphql.GithubGraphqlClient.get_corporate_emails_for_user",
        return_value=["jd@sacredheart.com"],
    )

    mocker.patch(
        "src.clients.slack.client.SlackClient.find_user_by_email", return_value="jd"
    )
    mocker.patch(
        "src.clients.slack.client.SlackClient.send_dm_to_user", return_value=None
    )
    # Mock the logger
    mock_logger = mocker.patch("src.main.logger")

    main.run()

    assert mock_logger.debug.call_count == 2

    src.clients.github.graphql.GithubGraphqlClient.get_corporate_emails_for_user.assert_called_once_with(
        "vanillabear"
    )
    src.clients.slack.client.SlackClient.find_user_by_email.assert_called_once_with(
        "jd@sacredheart.com"
    )
    src.clients.slack.client.SlackClient.send_dm_to_user("jd", "Hooch is crazy!")
