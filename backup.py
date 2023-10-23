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

# TODO:
# - option to skip sync repos, maybe some heavy fork that's irrelevant if lost
# - add org repo sync, i.e. Cabinet

def get_repos_from_github():
    # `gh repo list --json` takes fields that are documented on:
    # https://docs.github.com/en/graphql/reference/objects#repository
    try:
        result = subprocess.run(["gh", 'repo', 'list', '--limit', '999', '--json',
                                'name,sshUrl,isPrivate,isFork,isArchived'],
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

    repos = [{ 'name': name.removesuffix(".git") } for name in folders]

    return repos

def format_repo_info(repo):
    result = colorize('cyan', repo['name'])
    tags = []

    is_private = repo.get('isPrivate')
    if is_private is None:
        pass  # No info on whether is private/public
    elif is_private:
        tags.append(colorize('red', 'private'))
    elif not is_private:
        tags.append(colorize('green', 'public'))

    if repo.get('isFork'):
        tags.append("fork")

    if repo.get('isArchived'):
        tags.append("archived")

    if tags:
        result += " [" + ", ".join(tags) + "]"

    return result


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


def updater(repos, skip_archived=False):
    os.makedirs(REPOS_LOCATION, exist_ok=True)
    os.chdir(REPOS_LOCATION)

    for repo in repos:
        name = repo['name'] + ".git"

        if repo['isArchived']:
            message = f"{colorize('orange', 'Skipping:')}: "
            message += format_repo_info(repo)
            print(message)
            continue

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

    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('-l', '--list', action='store_true',
                         help='List repositories')
    actions.add_argument('-s', '--sync', action='store_true',
                         help='sync local repositories with latest remote data')

    g = parser.add_argument_group("Repositories",
                                  description="Get repository list from different sources")
    group = g.add_mutually_exclusive_group()
    group.add_argument(
        '-j', '--json', dest='load_from', action='store_const', const="json",
        help=(
            f"get repository list from '{JSON_REPOS_FILE}' file. "
            f"The '{JSON_REPOS_FILE}' file is created and updated when you use the '--github' option. This is the default source."
        )
    )
    group.add_argument(
        '-g', '--github', dest='load_from', action='store_const', const="github",
        help=(
            "get repository list from GitHub (calls the 'gh' cli app). "
            f"The '{JSON_REPOS_FILE}' file is created and updated when you use the '--github' option."
        )
    )
    group.add_argument(
        '-L', '--local', dest='load_from', action='store_const', const="local",
        help=(
            f"get repository list from '{REPOS_LOCATION}' folder. "
            "This option will list repositories with minimal information, "
            "and can be used to sync any git repo without depending on GitHub."
        )
    )
    group.set_defaults(load_from="json")

    group = parser.add_argument_group("Sync options")
    group.add_argument('-a', '--skip-archived', action='store_true', help='Skip archived repositories on sync')

    args = parser.parse_args()

    if len(sys.argv[1:]) == 0:
        # No arguments provided? show help and exit
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

    if args.list:
        list_repos(repos)

    if args.sync:
        updater(repos, args.skip_archived)
