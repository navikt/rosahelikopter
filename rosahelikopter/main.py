#!/usr/bin/env python3

"""
File containing "main()" logic for rosahelikopter.
"""

# Python standard library imports
from collections import OrderedDict
import json
import os
from pathlib import Path
import sys
from typing import (
    Any,
    Iterable,
    Union,
)

# 3rd-party python package imports
import click
from python_graphql_client import GraphqlClient

# Imports of module(s) internal to this project/package
from rosahelikopter.github import graphql_fetch_access_permission_for_repoes_for_team_in_org
from rosahelikopter.markdown import make_markdown_template


def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj


def repo_filter(repo_data: dict[str, Union[str, dict[str, set[str]]]]) -> bool:
    if repo_data['isArchived'] or 'ADMIN' not in repo_data.get('permissions', {}):
        # We're not interested in parsing/displaying info of this repository.
        False
    return True


def main(
    teams: Iterable[str],
    organizations: Iterable[str],
    github_auth_token: str,
    make_org_folders: bool,
    make_team_files: bool,
    tee_output: bool,
    verbosity_level: int,
    **kwargs: dict[Any, Any],

) -> None:
    client = GraphqlClient('https://api.github.com/graphql')
    client.headers.update(
        dict(Authorization=f"bearer {github_auth_token}")
    )

    global_results = dict()
    for org_name in organizations:
        # First set-up folder if flag is set
        org_folder = Path.cwd()
        if make_org_folders:
            org_folder = org_folder / org_name
            org_folder.mkdir(exist_ok=True)

        org_results = dict()
        for team_name in teams:
            team_results = dict()
            for repo_data in (
                repo_data
                for repo_data
                in graphql_fetch_access_permission_for_repoes_for_team_in_org(
                    org_name=org_name,
                    team_name=team_name,
                    client=client,
                )
                if repo_data    # Remove empty results from GraphQL json output (happens sometimes)
            ):
                # print(json.dumps(repo_data_list, indent=2), file=sys.stderr)
                repo_name = repo_data['node']['nameWithOwner']

                # If first time repo is seen by a team we're iterating over, add to collecting variable
                if repo_name not in team_results:
                    team_results[repo_name] = repo_data['node']

                perms = 'permissions'
                if not isinstance(team_results[repo_name].get(perms), dict):
                    team_results[repo_name][perms] = dict()

                # Set permission level team has for repo in question
                team_permission_role = repo_data['permission']
                if not isinstance(team_results[repo_name][perms].get(team_permission_role), set):
                    team_results[repo_name][perms][team_permission_role] = set()
                team_results[repo_name][perms][team_permission_role].add(team_name)

            # Clean up results variable of non-valid repoes first
            team_results = {
                repo_name: repo_data
                for repo_name, repo_data,
                in team_results.items()
                if repo_filter(repo_data)
            }

            # Save in case flags specify stdout/global output
            org_results.update(team_results)
            if make_team_files is False or len(team_results) == 0:
                continue

            # Write to team-named files
            team_file = org_folder / f"{team_name}.md"
            team_file.write_text(make_markdown_template(team_results))

        # No repos for any of the teams in this org
        if len(org_results) == 0: continue
        global_results.update(org_results)
        # Files have either already been written, or won't be written
        if  make_team_files or make_org_folders is False: continue

        # Write to org specific files
        org_file = org_folder / 'overview.md'
        org_file.write_text(make_markdown_template(org_results))

    if (make_org_folders or make_team_files) and tee_output is False:
        # Job done! No output to stdout
        return

    # print(f"{len(org_results)}", file=sys.stderr)
    if len(global_results) == 0:
        click.echo(f"No repositories found for teams {teams} in any of orgs {organizations}!", err=True)
        return

    global_results = OrderedDict(sorted(global_results.items()))
    # click.echo(json.dumps(global_results, indent=2, default=serialize_sets), err=True)

    # Tabulate and write output
    markdown_output = make_markdown_template(global_results)
    click.echo(markdown_output)
