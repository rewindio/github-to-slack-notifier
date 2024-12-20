import pytest
import requests
import requests_mock
import json

from clients.github.graphql import GithubGraphqlClient

MOCK_RESPONSE_WITH_PAGINATION = {
    "data": {
        "organization": {
            "membersWithRole": {
                "pageInfo": {"endCursor": "Y3Vyc29yOjEwMA==", "hasNextPage": True},
                "edges": [
                    {
                        "node": {
                            "login": "chocolatebear",
                            "organizationVerifiedDomainEmails": [
                                "chris.turk@sacredheart.com",
                                "turkelton@sacredheart.com",
                            ],
                        },
                    }
                ],
            }
        }
    }
}

MOCK_RESPONSE = {
    "data": {
        "organization": {
            "membersWithRole": {
                "pageInfo": {"endCursor": "Y3Vyc29yOjEwMA==", "hasNextPage": False},
                "edges": [
                    {
                        "node": {
                            "login": "two_thumbs",
                            "organizationVerifiedDomainEmails": [
                                "bob.kelso@sacredheart.com",
                                "bkelso@sacredheart.com",
                            ],
                        },
                    },
                    {
                        "node": {
                            "login": "drcox",
                            "organizationVerifiedDomainEmails": [
                                "perry.cox@sacredheart.com",
                                "perry.cox+ratemydoc@sacredheart.com",
                            ],
                        }
                    },
                ],
            }
        }
    }
}


@pytest.fixture
def fixture():
    org = "rewindio"
    token = "who_put_bullion_in_the_shower_head"

    return GithubGraphqlClient(token, org)


def test_get_all_corporate_emails_for_user(requests_mock, fixture):
    requests_mock.post("https://api.github.com/graphql", json=MOCK_RESPONSE)

    emails = fixture.get_corporate_emails_for_user("two_thumbs")

    assert emails == ["bob.kelso@sacredheart.com", "bkelso@sacredheart.com"]


def test_get_all_corporate_emails_for_user_private_github_email(requests_mock, fixture):
    requests_mock.post("https://api.github.com/graphql", json=MOCK_RESPONSE)

    emails = fixture.get_corporate_emails_for_user(
        "1234+two_thumbs@users.noreply.github.com"
    )

    assert emails == ["bob.kelso@sacredheart.com", "bkelso@sacredheart.com"]


def test_get_all_corporate_emails_for_user_with_github_email(requests_mock, fixture):
    requests_mock.post("https://api.github.com/graphql", json=MOCK_RESPONSE)

    emails = fixture.get_corporate_emails_for_user(
        "two_thumbs@users.noreply.github.com"
    )

    assert emails == ["bob.kelso@sacredheart.com", "bkelso@sacredheart.com"]


def test_get_all_corporate_emails_for_user_with_custom_email(requests_mock, fixture):
    requests_mock.post("https://api.github.com/graphql", json=MOCK_RESPONSE)

    emails = fixture.get_corporate_emails_for_user("two_thumbs@sacredheart.com")

    assert emails == ["bob.kelso@sacredheart.com", "bkelso@sacredheart.com"]


def test_get_corporate_emails_for_user_with_pagination(requests_mock, fixture):
    requests_mock.post(
        "https://api.github.com/graphql", json=MOCK_RESPONSE_WITH_PAGINATION
    )
    requests_mock.post(
        "https://api.github.com/graphql",
        json=MOCK_RESPONSE,
        additional_matcher=lambda req: json.loads(req.text)["variables"]["after"]
        == "Y3Vyc29yOjEwMA==",
    )

    emails = fixture.get_corporate_emails_for_user("drcox")

    assert emails == [
        "perry.cox@sacredheart.com",
        "perry.cox+ratemydoc@sacredheart.com",
    ]


def test_exception_raise_if_user_not_found(requests_mock, fixture):
    requests_mock.post("https://api.github.com/graphql", json=MOCK_RESPONSE)

    with pytest.raises(Exception):
        fixture.get_corporate_emails_for_user("greghouse")


parse_github_user_test_data = [
    ("1234+jd@users.noreply.github.com", "jd"),
    ("turk@users.noreply.github.com", "turk"),
    ("hooch", "hooch"),
    ("jan.itor@rewind.io", "jan.itor"),
    ("3333+bob.kelso@rewind.io", "bob.kelso"),
]


@pytest.mark.parametrize("actual, expected", parse_github_user_test_data)
def test_parse_github_user(actual, expected, fixture):
    assert fixture._parse_user(actual) == expected
