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


def write_markdown_files(
    dataset,
    organizations: Iterable[str],
    teams: Iterable[str],
    make_org_folders: bool,
    make_team_files: bool,
) -> None:
    for org_name in organizations:
        # First set-up folder if flag is set
        file_output_dir = Path.cwd()
        if make_org_folders and len(dataset[org_name]) > 0:
            file_output_dir = file_output_dir / org_name
            file_output_dir.mkdir(exist_ok=True)

        # Then, write to file specified with CLI options/flags
        if make_team_files:
            for team in teams:
                file_specific_team_repoes = OrderedDict(
                    sorted(
                        {
                            repo_name: repo_data
                            for repo_name, repo_data
                            in dataset.get(team, dict()).items()
                            if not make_org_folders or (
                                make_org_folders and repo_name.startswith(f"{org_name}/")
                            )
                        }.items()
                    )
                )
                if len(file_specific_team_repoes) == 0:
                    continue
                output_file = file_output_dir / f"{team}.md"
                output_file.write_text(make_markdown_template(file_specific_team_repoes))
        else:
            if len(dataset[org_name]) == 0:
                file_output_dir.rmdir()
                continue
            output_file = file_output_dir / "overview.md"
            output_file.write_text(make_markdown_template(dataset[org_name]))
    return


def fetch_and_filter_repositories(
    org_name: str,
    team_name: str,
    graphql_client,
) -> dict:
    correctly_configured_repoes = dict()
    for repo_data in (
        repo_data
        for repo_data
        in graphql_fetch_access_permission_for_repoes_for_team_in_org(
            org_name=org_name,
            team_name=team_name,
            client=graphql_client,
        )
        if repo_data    # Remove empty results from GraphQL json output (happens sometimes)
    ):
        # print(json.dumps(repo_data_list, indent=2), file=sys.stderr)
        repo_name = repo_data['node']['nameWithOwner']

        if not repo_filter(repo_data['node']):
            # Repository does not match criteria for filtering
            continue

        # If first time repo is seen by a team we're iterating over, add to collecting variable
        if repo_name not in correctly_configured_repoes:
            correctly_configured_repoes[repo_name] = repo_data['node']

        perms = 'permissions'
        if not isinstance(correctly_configured_repoes[repo_name].get(perms), dict):
            correctly_configured_repoes[repo_name][perms] = dict()

        # Set permission level team has for repo in question
        team_permission_role = repo_data['permission']
        if not isinstance(correctly_configured_repoes[repo_name][perms].get(team_permission_role), set):
            correctly_configured_repoes[repo_name][perms][team_permission_role] = set()
        correctly_configured_repoes[repo_name][perms][team_permission_role].add(team_name)

    return correctly_configured_repoes



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
        if verbosity_level >= 1:
            click.echo(f"\nNow traversing {org_name}!", err=True)

        if org_name not in global_results:
            global_results[org_name] = dict()
        for team_name in teams:
            if verbosity_level >= 1:
                click.echo(f"\tLooking for repoes {team_name} is ADMIN for in {org_name}...", err=True)

            repoes_fetched = fetch_and_filter_repositories(
                org_name=org_name,
                team_name=team_name,
                graphql_client=client,
            )
            if verbosity_level >= 2:
                click.echo(f"\t\t{len(repoes_fetched)} found for {team_name} in {org_name}!", err=True)

            if team_name not in global_results:
                global_results[team_name] = dict()
            global_results[org_name].update(repoes_fetched)
            global_results[team_name].update(repoes_fetched)

        if verbosity_level >= 1:
            click.echo(f"\t{len(global_results[org_name])} repositories found in {org_name}!", err=True)

    # click.echo(json.dumps(global_results, indent=2, default=serialize_sets), err=True)
    if make_org_folders or make_team_files:
        # Save to files if requested!
        write_markdown_files(
            dataset=global_results,
            make_org_folders=make_org_folders,
            make_team_files=make_team_files,
            organizations=organizations,
            teams=teams,
        )
        if tee_output is False:
            # Job done! No output to stdout
            return

    # print(f"{len(org_results)}", file=sys.stderr)
    if all(
        len(global_results[org_name]) == 0
        for org_name in organizations
    ):
        click.echo(f"No repositories found for teams {teams} in any of orgs {organizations}!", err=True)
        return

    output_results = OrderedDict()
    for org_name in sorted(organizations):
        output_results.update(sorted(global_results.get(org_name, dict()).items()))
    # click.echo(json.dumps(output_results, indent=2, default=serialize_sets), err=True)

    # Tabulate and write output
    markdown_output = make_markdown_template(output_results)
    click.echo(markdown_output)
