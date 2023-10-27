# Extras
On this folder I have some scripts to help me work with the many repositories I
backup. Feel free to check it out, use or ignore it.

# Filtering json file
Information about repositories is stored on the `repositories.json` file, and
you can use [jq](https://jqlang.github.io/jq/) to filter its contents.

Here are some examples:
```sh
# show private repos
jq -r '.[] | select(.isPrivate)' repositories.json

# show private repos, only names
jq -r '.[] | select(.isPrivate) | .name' repositories.json

# show non-archived repos, only names
jq -r '.[] | select(.isArchived | not) | .name' repositories.json

# show non forks
jq -r '.[] | select(.isFork | not)' repositories.json
```
