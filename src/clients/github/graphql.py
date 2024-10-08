import requests
import re

from exceptions import GithubUserNotFoundException

from .queries import QUERIES
from http import HTTPStatus


class GithubGraphqlClient:
    def __init__(self, token: str, org_id: str):
        self.org_id = org_id
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self.url = "https://api.github.com/graphql"

    def get_corporate_emails_for_user(self, git_user: str) -> list:
        """
        Returns a list of corporate emails for a user
        """

        query = QUERIES["GET_LIST_OF_MEMBERS_IN_ORG"]
        after = None

        user = None
        git_username = self._parse_user(git_user)

        while True:
            reponse = self._make_post_request(query=query, after=after)

            if reponse.status_code == HTTPStatus.OK:
                data = reponse.json()
                members = data["data"]["organization"]["membersWithRole"]["edges"]

                user = next(
                    (
                        edge["node"]
                        for edge in members
                        if edge["node"]["login"] == git_username
                    ),
                    None,
                )

                if user:
                    break

                page_info = data["data"]["organization"]["membersWithRole"]["pageInfo"]
                if page_info["hasNextPage"]:
                    after = page_info["endCursor"]
                else:
                    break
            else:
                raise Exception(f"Failed to make request: {data.status_code}")

        if user is None:
            raise GithubUserNotFoundException(
                f"User {git_user} not found in organization {self.org_id}"
            )

        return user["organizationVerifiedDomainEmails"]

    def _make_post_request(
        self, query: str, variables: dict = {}, after: str = None
    ) -> any:
        vars = variables | {"org": self.org_id, "after": after}

        response = requests.post(
            url=self.url, headers=self.headers, json={"query": query, "variables": vars}
        )

        return response

    def _parse_user(self, user: str) -> str:
        """
        Parse the Github user ID from the value provided in the action.

        If `user` is ID+username@users.noreply.github.com, return username.
        If `user` is username@users.noreply.github.com, return username.
        If `user` is an email address, return the username part of the email address
        If `user` is not an email address, just return it as-is.

        """
        match = re.match(
            r"^(\d+\+)?([a-zA-Z0-9._%+-]+)(@users\.noreply\.github\.com|@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})?$",
            user,
        )

        if match:
            return match.group(2)
        else:
            return user
