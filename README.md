# Github to Slack Notifier

A Github action to send a Slack Direct Message.

This action finds the corporate e-mails of a git user in the configured org and sends a DM to a user in Slack with the same corporate e-mail address

## Usage

### Using the pre-built container

```yaml
jobs:
  send-slack-dm:
    name: Send a Slack DM
    runs-on: ubuntu-latest

    steps:
     name: Send Slack DM to user on deploy failure
     id: send-slack-dm
     uses: docker://ghcr.io/rewindio/github-to-slack-notifier:latest
     with:
        github_token: ${{ secrets.GITHUB_USER_LOOKUP_TOKEN }}
        slack_bot_token: ${{ secrets.SLACK_DM_TOKEN }}
        github_org: ${{ github.repository_owner }}
        list_of_github_users: "github_user"
        message: "Hello!"
```

### Building the container on each Github Action run

```yaml
jobs:
  send-slack-dm:
    name: Send a Slack DM
    runs-on: ubuntu-latest

    steps:
     name: Send Slack DM to user on deploy failure
     id: send-slack-dm
     uses: rewindio/github-to-slack-notifier@v{VERSION_TAG}
     with:
        github_token: ${{ secrets.GITHUB_USER_LOOKUP_TOKEN }}
        slack_bot_token: ${{ secrets.SLACK_DM_TOKEN }}
        github_org: ${{ github.repository_owner }}
        list_of_github_users: "github_user"
        message: "Hello!"
```

This will build the `github-to-slack-notifier` action container on each workflow run.

The docker build may hang when the action builds the container.

To prevent long action run times, using the pre-built container is recommended.

## Input Variables

The action requires the following input variables:

| Input              | Description   |
| :---------------- | :------: |
| github_token                 |   Github token. See below for required permissions.  |
| slack_bot_token                 |  Slack OAuth token. See below for required permissions. |
| github_org                 |  Github Org ID  |
| list_of_github_users | List of users to DM. See Github Users for more information. |
| message | Message to send to user(s) |

### GITHUB_TOKEN permissions

The default `GITHUB_TOKEN` will not have sufficent permissions to look-up the user's verified corporate e-mail addresses.
The supplied `GITHUB_TOKEN` will require the `read:org` permissions.

### SLACK_TOKEN permissions

The `SLACK_TOKEN` will require the following scopes:

| Scope              | Reason   |
| :---------------- | :------: |
| users:read.email  |  Required by the `users.lookupByEmail` method.  |
| chat:write        | Required by the `chat.postMessage` method. |
| channels:manage | Required by the `conversations.open` method. |
| groups:write | Required by the `conversations.open` method. |
| im:write | Required by the `conversations.open` method. |
| mpim: write | Required by the `conversations.open` method. |

## Exit Codes

Github to Slack Notifier can exit with the following codes:

| Code              | Reason   |
| :---------------- | :------: |
| 0                 |   Everything went well  |
| 1                 | Error querying API/GraphQL |
| 2                 |   Missing required input variables. See logs.  |

## Github Users

The parameter `list_of_github_users` accepts a list of users to notify. This list can be a single string, comma-separated string or a JSON list of strings. ("user", '["user"'], "user1,user2,user3").

The list of users can be of the following values:
    - Private Github email address. This is in the format of `{ID}+{user}@users.noreply.github.com`
    - Private Github email address without ID prepend. This is in the format of `{user}@users.noreply.github.com`
    - An email address. This is in the format of `user@company.com`. Or
    - Github username.

[See Github documentation on profiles to understand why there are two formats of Github private email addresses](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address#about-commit-email-addresses)

## A note about e-mails

Organization e-mail(s) for a user is only available if the e-mail domain is verified for the Github organization.
[See Github documentation for this procedure](https://docs.github.com/en/organizations/managing-organization-settings/verifying-or-approving-a-domain-for-your-organization).
