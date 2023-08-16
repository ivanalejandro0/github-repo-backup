#!/bin/sh

# This script uses the json data we got from GitHub and use the `jq` app to
# filter through the json information.

cat repositories.json | jq -r -c '.[] | select(.isPrivate) | .name'  # show private repos, only names
# cat repositories.json | jq -c '.[] | select(.isPrivate)'  # show private repos
# cat repositories.json | jq -c '.[] | select(.isPrivate | not)'  # show public repos
# cat repositories.json | jq -c '.[] | select(.isFork)'  # show forks
# cat repositories.json | jq -c '.[] | select(.isFork | not)'  # show non forks
