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
            resp = self.client.chat_postMessage(channel=user_id, text=message)
            print(resp)
        except SlackApiError as e:
            raise Exception(f"Failed to send message: {e.response['error']}") from e
