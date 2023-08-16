# GitHub repo backup
This is a simple script to backup and keep local backup in sync with GitHub
repositories.

This only backups git repositories, it ignores other GitHub data like
issues/wiki/projects/etc.


## About the script
One goal of this script is to be short and simple, so it can be easily reviewed
for you to know what code you're running if you decide to use it.
That's why I kept it on just one file and without third party dependencies.
Which will also help with using it, just download the file and run, no need to
pull packages to get it to work.

I'm using this only on Linux, but it should work on Mac as well.

## Made to be used with GitHub
Part of the tool depends on GitHub (like getting your remote repos), but other
parts like syncing the repositories does not. So this tool should work with
other providers with not many changes.

