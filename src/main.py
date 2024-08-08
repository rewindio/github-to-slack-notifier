import sys
import logging
import os
import json

from clients.github.graphql import GithubGraphqlClient
from clients.slack.client import SlackClient
from exceptions import GithubUserNotFoundException, SlackUserNotFoundException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def run():
    # Validate the input
    required_env_vars = {
        "INPUT_GITHUB_TOKEN": "Missing GitHub token",
        "INPUT_SLACK_BOT_TOKEN": "Missing Slack token",
        "INPUT_LIST_OF_GITHUB_USERS": "Missing list of GitHub users",
        "INPUT_GITHUB_ORG": "Missing GitHub organization",
        "INPUT_MESSAGE": "Missing message",
    }

    for env_var, error_message in required_env_vars.items():
        if not os.getenv(env_var):
            logger.error(error_message)
            sys.exit(2)

    logger.debug("Creating clients...")

    gh_graphql = GithubGraphqlClient(
        token=os.getenv("INPUT_GITHUB_TOKEN"), org_id=os.getenv("INPUT_GITHUB_ORG")
    )
    slack_client = SlackClient(token=os.getenv("INPUT_SLACK_BOT_TOKEN"))

    logger.debug("Getting corporate emails for users...")

    users = get_list_of_users(os.getenv("INPUT_LIST_OF_GITHUB_USERS"))

    if users == []:
        logger.error(
            f"""
            User(s) was not provided in an expected format.
                Expected a string, comma-separated string or JSON list.
                Got: {os.getenv("INPUT_LIST_OF_GITHUB_USERS")}
            """
        )
        sys.exit(2)

    # Only one user - send a direct message
    if len(users) == 1:
        user = users[0]

        try:
            emails = gh_graphql.get_corporate_emails_for_user(user)
            slack_id = get_slack_id_for_user(slack_client, emails)

            if slack_id is None:
                logger.error(
                    f"Failed to find a Slack ID for user {user}. No message will be sent to this user"
                )
                sys.exit(1)

            try:
                slack_client.send_dm_to_user(slack_id, os.getenv("INPUT_MESSAGE"))
            except Exception as e:
                logger.error(f"Failed to send message to user {user}: {e}")
                sys.exit(1)

        except GithubUserNotFoundException as e:
            logger.error(f"Failed to get emails for Github user {user}: {e}")
            sys.exit(1)

    # More than one user, send a MPDM
    if len(users) > 1:
        slack_ids = []
        for user in users:
            try:
                emails = gh_graphql.get_corporate_emails_for_user(user)
                user_slack_id = get_slack_id_for_user(slack_client, emails)

                if user_slack_id is not None:
                    slack_ids.append(user_slack_id)
                else:
                    logger.warn(
                        f"Failed to find a Slack ID for user {user}. No message will be sent to this user"
                    )
            except GithubUserNotFoundException as e:
                logger.error(f"Failed to get emails for Github user {user}: {e}")
                sys.exit(1)

        try:
            slack_client.send_mpdm_to_users(slack_ids, os.getenv("INPUT_MESSAGE"))

        except Exception as e:
            logger.error(f"Failed to send message to multiple users: {e}")
            sys.exit(1)


def get_list_of_users(input):
    try:
        # is this json?
        parsed_value = json.loads(input)
        if isinstance(parsed_value, list):
            return parsed_value
    except json.JSONDecodeError:
        pass

    # is this just a comma separated string?
    if "," in input:
        return [item.strip() for item in input.split(",")]

    # i'm just a string, i need no parsing
    if isinstance(input, str) and input.strip():
        return [input.strip()]

    # easy come, easy go...
    return []


def get_slack_id_for_user(slack_client, emails):
    slack_id = None
    found_slack_id = False

    for email in emails:
        attempt = 1

        logger.info(f"Sending message to user with email {email}...")

        while attempt <= len(emails) and not found_slack_id:
            try:
                slack_id = slack_client.find_user_by_email(email)
                found_slack_id = True

                break
            except SlackUserNotFoundException as e:
                logger.warn(f"No user in Slack with email {email}: {e}")
                attempt += 1

    if not found_slack_id:
        logger.warn(
            f"Failed to find a Slack ID with emails {emails}. No message will be sent to this user"
        )

    return slack_id


if __name__ == "__main__":
    run()
