#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys

MIN_PYTHON = (3, 5)
# I'm using `subprocess.run`, which requires Python >= 3.5
# on Python < 3.5 `subprocess.check_output` could be used instead
if sys.version_info < MIN_PYTHON:
    sys.exit("Error: Python %s.%s or later is required." % MIN_PYTHON)

REPOS_LOCATION = "repos"


def get_repos_from_github():
    # `gh repo list --json` takes fields that are documented on:
    # https://docs.github.com/en/graphql/reference/objects#repository
    try:
        result = subprocess.run(["gh", 'repo', 'list', '--limit', '999', '--json', 'name,sshUrl'],
                                stdout=subprocess.PIPE)
        repos = result.stdout.decode('utf-8')
    except FileNotFoundError:
        sys.exit("Error: there was a problem running the `gh` binary. Maybe it's not installed?")

    repos = json.loads(repos)
    return repos


def clone_repo(sshUrl):
    try:
        subprocess.run(f"git clone --mirror {sshUrl}",
                       shell=True, check=True)
    except subprocess.CalledProcessError:
        print("Error: there was an error calling 'git'")
    except Exception as e:
        print("Unexpected error:", e)


def update_repo():
    try:
        subprocess.run('git fetch --all',
                       shell=True, check=True)
    except subprocess.CalledProcessError:
        print("Error: there was an error calling 'git'")
    except Exception as e:
        print("Unexpected error:", e)


def updater(repos):
    os.makedirs(REPOS_LOCATION, exist_ok=True)
    os.chdir(REPOS_LOCATION)

    for repo in repos:
        name = repo['name'] + ".git"

        repo_exists = os.path.isdir(name)

        message = f"{'Updating:' if repo_exists else 'Cloning:'}: {repo.get('name')}"
        print(message)

        if repo_exists:
            os.chdir(name)
            update_repo()
            os.chdir('..')
        else:
            clone_repo(repo['sshUrl'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Git repositories backup tool')
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('-l', '--list', action='store_true',
                        help='list repositories')
    actions.add_argument('-s', '--sync', action='store_true',
                        help='sync local repositories with latest remote data')

    args = parser.parse_args()

    if len(sys.argv[1:]) == 0:
        # No arguments provided? show help and exit
        parser.print_help()
        sys.exit()

    repos = get_repos_from_github()

    if args.list:
        for repo in repos:
            print(repo.get("name"))

    if args.sync:
        updater(repos)
