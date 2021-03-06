#!/usr/bin/env python

import argparse
import yaml
from subprocess import check_output
import re
import sys
import difflib

def _unidiff_output(expected, actual):
    """
    Helper function. Returns a string containing the unified diff of two multiline strings.
    """

    expected=expected.splitlines(1)
    actual=actual.splitlines(1)

    diff=difflib.unified_diff(expected, actual)

    return ''.join(diff)

parser = argparse.ArgumentParser(
    description='Check/Upgrade requirements.yml file')
parser.add_argument(
    '-f',
    default='./requirements.yml',
    metavar='FILE',
    help='path to requirements.yml file')
parser.add_argument(
    '--check', action='store_true', help='Fail on outdated roles')

args = parser.parse_args()

requirements_file_path = args.f

requirements_file = open(requirements_file_path, 'r')

roles = yaml.load(requirements_file)

updated_roles = []

for role in roles:

    new_role = dict(role)

    # Get last git tag
    refs = check_output(["git", "ls-remote", "--tags", "--sort=v:refname", role['src']], encoding="utf-8")

    tags = []

    for ref in refs.splitlines():
        if "tags" in ref and "^{}" not in ref:
            tags.append(ref)

    if not tags:
      print('No tags avail able for ' + role['src'] + ' doing nothing')
      exit(13)

    new_role['version'] = re.search('refs/tags/(.+?)$', tags[-1]).group(1)

    updated_roles.append(new_role)

requirements_file.close()

old_roles_string = yaml.dump(roles, default_flow_style=False)
new_roles_string = yaml.dump(updated_roles, default_flow_style=False)

if old_roles_string != new_roles_string:

    if args.check:
        # Fail on version mismatch

        print('Outdated role(s) please upgrade')

        print(_unidiff_output(old_roles_string, new_roles_string))

        exit(1)

    else:
        # Write new versions

        print('Writing new role versions to {}'.format(requirements_file_path))

        update_requirements_file = open(requirements_file_path, 'w')

        update_requirements_file.write(
            yaml.dump(updated_roles, default_flow_style=False))

        update_requirements_file.close()

else:

    print('No outdated roles detected')
