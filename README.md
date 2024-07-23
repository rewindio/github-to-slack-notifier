# github-to-slack-notifier
A GitHub action to notify Slack user of GitHub events

## Exit Codes

Github to Slack Notifier can exit with the following codes:

| Code              | Reason   |
| :---------------- | :------: |
| 0                 |   Everything went well  |
| 1                 | Error querying API/GraphQL |
| 2                 |   Missing required input variables. See logs.  |
