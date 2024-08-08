from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from exceptions import SlackUserNotFoundException


class SlackClient:
    def __init__(self, token: str):
        self.client = WebClient(token=token)

    def find_user_by_email(self, email: str) -> str:
        response = self.client.users_lookupByEmail(email=email)

        if not response["ok"]:
            raise SlackUserNotFoundException(
                f"Failed to find user: {response['error']}"
            )

        return response["user"]["id"]

    def send_dm_to_user(self, user_id: str, message: str):
        try:
            self.client.chat_postMessage(channel=user_id, text=message)

        except SlackApiError as e:
            raise Exception(f"Failed to send message: {e.response['error']}") from e

    def send_mpdm_to_users(self, user_ids: list, message: str):
        try:
            resp = self.client.conversations_open(users=user_ids)
            channel_id = resp["channel"]["id"]

            self.send_dm_to_user(channel_id, message)

        except SlackApiError as e:
            raise Exception(f"Failed to send message: {e.response['error']}") from e
