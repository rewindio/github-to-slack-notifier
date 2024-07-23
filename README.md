# github-to-slack-notifier
A GitHub action to notify Slack user of GitHub events

## Input Variables

The action requires the following input variables:

| Input              | Description   |
| :---------------- | :------: |
| github_token                 |   Github token. See below for required permissions.  |
| slack_bot_token                 |  Slack OAuth token. See below for required permissions. |
| github_org                 |  Github Org ID  |
| list_of_github_users | List of users to DM |
| message | Message to send to user(s) |

### GITHUB_TOKEN permissions

### SLACK_TOKEN permissions

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
