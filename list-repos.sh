#!/bin/sh

# This script uses the json data we got from GitHub and use the `jq` app to
# filter through the json information.

jq -r '.[] | select(.isArchived) | .name' repositories.json  # show archived repos, only names
# jq -r '.[] | select(.isPrivate) | .name' repositories.json  # show private repos, only names
# jq -r '.[] | select(.isPrivate)' repositories.json  # show private repos
# jq -r '.[] | select(.isPrivate | not)' repositories.json  # show public repos
# jq -r '.[] | select(.isFork)' repositories.json  # show forks
# jq -r '.[] | select(.isFork | not)' repositories.json  # show non forks
