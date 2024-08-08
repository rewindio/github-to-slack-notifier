# github-to-slack-notifier

A Github action to send a Slack Direct Message.

This action finds the corporate e-mails of a git user in the configured org and sends a DM to a user in Slack with the same corporate e-mail address

## Input Variables

The action requires the following input variables:

| Input              | Description   |
| :---------------- | :------: |
| github_token                 |   Github token. See below for required permissions.  |
| slack_bot_token                 |  Slack OAuth token. See below for required permissions. |
| github_org                 |  Github Org ID  |
| list_of_github_users | List of users to DM. Can be a single string, comma-separated string or a JSON list of strings. ("user", '["user"'], "user1,user2,user3") |
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

## A note about e-mails

Organization e-mail(s) for a user is only available if the e-mail domain is verified for the Github organization.
[See Github documentation for this procedure](https://docs.github.com/en/organizations/managing-organization-settings/verifying-or-approving-a-domain-for-your-organization).
