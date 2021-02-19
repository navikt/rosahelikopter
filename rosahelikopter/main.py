#!/usr/bin/env python3

"""
File containing "main()" logic for rosahelikopter.
"""

# Python standard library imports
from collections import OrderedDict
import json
import os
import sys

# Non-standard library python package imports
# 3rd-party python package imports
from python_graphql_client import GraphqlClient

# Imports of module(s) internal to this project/package
from rosahelikopter.github import graphql_fetch_access_permission_for_repoes_for_team_in_org
from rosahelikopter.markdown import make_markdown_template

def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj


def main():
    try:
        authorization_token = os.environ['GITHUB_USER_TOKEN']
    except KeyError:
        print('Authorization token must be set in $GITHUB_USER_TOKEN', file=sys.stderr)
        sys.exit(1)

    client = GraphqlClient('https://api.github.com/graphql')
    client.headers.update(
        dict(Authorization=f"bearer {authorization_token}")
    )

    results = dict()
    for org_name, team_names in dict(
        navikt=('aura', 'pig-aiven'),
        nais=('aura', 'naisdevice'),
    ).items():
        for team_name in team_names:
            for repo_data in (
                repo_data
                for repo_data
                in graphql_fetch_access_permission_for_repoes_for_team_in_org(
                    org_name=org_name,
                    team_name=team_name,
                    client=client,
                )
                if repo_data
            ):
                # print(json.dumps(repo_data_list, indent=2), file=sys.stderr)
                repo_name = repo_data['node']['nameWithOwner']

                # If first time repo is seen by a team we're iterating over, add to collecting variable
                if repo_name not in results:
                    results[repo_name] = repo_data['node']

                perms = 'permissions'
                if not isinstance(results[repo_name].get(perms), dict):
                    results[repo_name][perms] = dict()

                # Set permission level team has for repo in question
                team_permission_role = repo_data['permission']
                if not isinstance(results[repo_name][perms].get(team_permission_role), set):
                    results[repo_name][perms][team_permission_role] = set()
                results[repo_name][perms][team_permission_role].add(team_name)

    # print(f"{len(results)}", file=sys.stderr)
    results = OrderedDict(sorted(results.items()))
    # print(json.dumps(results, indent=2, default=serialize_sets), file=sys.stderr)

    # Tabulate and write output
    markdown_output = make_markdown_template(results)
    print(markdown_output)


if __name__ == '__main__':
    main()
