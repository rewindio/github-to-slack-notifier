import sys
import logging
import os
import json

from src.clients.github.graphql import GithubGraphqlClient
from src.clients.slack.client import SlackClient
from exceptions import GithubUserNotFoundException, SlackUserNotFoundException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def run():
    # Validate the input
    required_env_vars = {
        "INPUT_GITHUB_TOKEN": "Missing GitHub token",
        "INPUT_SLACK_TOKEN": "Missing Slack token",
        "INPUT_LIST_OF_GITHUB_USER": "Missing list of GitHub users",
        "INPUT_GITHUB_ORG": "Missing GitHub organization",
    }

    for env_var, error_message in required_env_vars.items():
        if not os.getenv(env_var):
            logger.error(error_message)
            sys.exit(2)

    logger.debug("Creating clients...")

    gh_graphql = GithubGraphqlClient(
        token=os.getenv("INPUT_GITHUB_TOKEN"), org_id=os.getenv("INPUT_GITHUB_ORG")
    )
    slack_client = SlackClient(token=os.getenv("INPUT_SLACK_TOKEN"))

    logger.debug("Getting corporate emails for users...")

    users = json.loads(os.getenv("INPUT_LIST_OF_GITHUB_USER"))

    emails = []
    for user in users:
        try:
            emails = gh_graphql.get_corporate_emails_for_user(user)
        except GithubUserNotFoundException as e:
            logger.error(f"Failed to get emails for Github user {user}: {e}")
            sys.exit(1)

    for email in emails:
        try:
            slack_id = slack_client.find_user_by_email(email)
            slack_client.send_dm_to_user(slack_id, os.getenv("INPUT_MESSAGE"))
        except SlackUserNotFoundException as e:
            logger.error(f"No user in Slack with email {email}: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to send message to user with email {email}: {e}")
            sys.exit(1)


if __name__ == "__main__":
    run()
