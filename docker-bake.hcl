group "default" {
    targets = ["production"]
}

target "github-to-slack-notifier" {
    context = "."
    dockerfile = "Dockerfile"
    platforms = [
        "linux/amd64"
    ]
    cache = {
        disabled = true
    }
}

target "development" {
    inherits = ["github-to-slack-notifier"]
}

target "production" {
    inherits = ["github-to-slack-notifier"]
}
