#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys

from typing import Literal

MIN_PYTHON = (3, 5)
# I'm using `subprocess.run`, which requires Python >= 3.5
# on Python < 3.5 `subprocess.check_output` could be used instead
if sys.version_info < MIN_PYTHON:
    sys.exit("Error: Python %s.%s or later is required." % MIN_PYTHON)

JSON_REPOS_FILE = "repositories.json"
REPOS_LOCATION = "repos"


def get_repos_from_github():
    # `gh repo list --json` takes fields that are documented on:
    # https://docs.github.com/en/graphql/reference/objects#repository
    try:
        result = subprocess.run(["gh", 'repo', 'list', '--limit', '999', '--json',
                                'name,sshUrl,isPrivate,isFork,isArchived,pushedAt'],
                                stdout=subprocess.PIPE)
        repos = result.stdout.decode('utf-8')
    except FileNotFoundError:
        sys.exit("Error: there was a problem running the `gh` binary. Maybe it's not installed?")

    repos = json.loads(repos)
    return repos


def get_repos_from_json():
    try:
        with open(JSON_REPOS_FILE) as f:
            repos = f.read()
    except FileNotFoundError:
        sys.exit(f"There was a problem reading the '{JSON_REPOS_FILE}' file."
            " Maybe you need to sync with GitHub first?")

    repos = json.loads(repos)
    return repos


def save_repos_to_json(repos):
    try:
        with open(JSON_REPOS_FILE, "w") as f:
            f.write(json.dumps(repos, indent=2))
    except Exception:
        sys.exit(f"There was a problem saving the '{JSON_REPOS_FILE}' file")


def get_repos_from_folders():
    folders = []
    try:
        folders = os.listdir(REPOS_LOCATION)
    except FileNotFoundError:
        # no public repos
        pass

    repos = [{
        'name': name.removesuffix(".git"),
        '__no_info__': True,  # no local info about the repo
    } for name in folders]

    return repos


def format_repo_info(repo):
    if repo.get("__no_info__"):
        # no local info about the repo
        return colorize('cyan', repo['name'])

    # TODO: handle missing repo info (like isArchived)
    return (
        f"{colorize('cyan', repo['name'])} "
        "["
        f"{colorize('red', 'private') if repo['isPrivate'] else colorize('green', 'public')}"
        f"{', fork' if repo['isFork'] else ''}"
        f"{', archived' if repo['isArchived'] else ''}"
        "]"
    )


def list_repos(repos):
    for repo in repos:
        info = format_repo_info(repo)
        print(info)


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


ColorOptions = Literal["red", "green", "orange", "cyan"]
def colorize(color_name: ColorOptions, text: str):
    reset = '\033[0m'
    colors = {
        'red': '\033[31m',
        'green': '\033[32m',
        'orange': '\033[33m',
        'cyan': '\033[36m',
    }
    color = colors.get(color_name)
    if color is None: return text
    return f"{color}{text}{reset}"


def updater(repos):
    os.makedirs(REPOS_LOCATION, exist_ok=True)
    os.chdir(REPOS_LOCATION)

    for repo in repos:
        name = repo['name'] + ".git"

        repo_exists = os.path.isdir(name)

        message = f"{colorize('orange', 'Updating:' if repo_exists else 'Cloning:')}: "
        message += format_repo_info(repo)
        print(message)

        if repo_exists:
            os.chdir(name)
            update_repo()
            os.chdir('..')
        else:
            clone_repo(repo['sshUrl'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Git repositories backup tool')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list repositories')
    parser.add_argument('-s', '--sync', action='store_true',
                        help='sync local repositories with latest remote data')
    parser.add_argument(
        '-f', '--from', dest='load_from',
        choices=['json', 'github', 'local'], default='json',
        help=(
            f'use repositories from "{JSON_REPOS_FILE}" file, github, or local folders '
                "(default: %(default)s). "
                f'Note that using "github" will update the "{JSON_REPOS_FILE}" file.'
        )
    )

    args = parser.parse_args()

    if len(sys.argv[1:]) == 0:
        # No arguments provided? show help
        parser.print_help()
        sys.exit()

    repos = None
    if args.load_from == "json":
        repos = get_repos_from_json()
    elif args.load_from == "github":
        repos = get_repos_from_github()
        save_repos_to_json(repos)
    elif args.load_from == "local":
        repos = get_repos_from_folders()

    if repos is None:
        sys.exit("Error: no repos found")

    if args.list:
        list_repos(repos)

    if args.sync:
        # TODO: maybe if there are no json/local repos, load from github
        updater(repos)