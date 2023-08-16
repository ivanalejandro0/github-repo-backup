# GitHub backup repo tool

This is a simple script to backup and keep local backup in sync with GitHub repositories.

This only backups git repositories, it ignores other GitHub data like issues/wiki/projects/etc.

Part of the tool depends on GitHub (like getting your remote repos), but other
parts like syncing the repositories does not. So this tool should work with
other providers with not many changes.
