# GitHub repo backup
This is a simple script to backup and keep local backup in sync with GitHub
repositories.

This only backups git repositories, it ignores other GitHub data like
issues/wiki/projects/etc.

You can copy and run `backup.py` and it should be enough, you only need Python
3.5+ and (for getting the repo list) the [GitHub CLI](https://cli.github.com/)

There's a `simple.py` script that's the simplest version of the `backup.py`
script with no colors and no extra information. You may want to check that out
if you want to quickly grasp how things are done.

## About the script
One goal of this script is to be short and simple, so it can be easily reviewed
for you to know what code you're running if you decide to use it.
That's why I kept it on just one file and without third party dependencies.
Which will also help with using it, just download the file and run, no need to
pull packages to get it to work.

Even though I want to keep it simple, I did add some extra code to make it
nicer. The script uses some colors and also shows some extra information about
each repo (like whether is private or public, or if is archived) to make it
using the tool a bit more enjoyable (to my taste at least).

I'm using this only on Linux, but it should work on Mac as well.

## Made to be used with GitHub
Part of the tool depends on GitHub (like getting your remote repos), but other
parts like syncing the repositories does not. So this tool should work with
other providers with not many changes.
For example, you could fill up the json file yourself and the script should
sync with no problem.

