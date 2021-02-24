#!/usr/bin/env python3
"""
Module containing "main()" logic for rosahelikopter.
"""

# Python standard library imports
from collections import defaultdict
import json
import os
import typing

# Non-standard library python package imports
# 3rd-party python package imports
import click
import gql
from gql.transport.requests import RequestsHTTPTransport

# Imports of module(s) internal to this project/package
from rosahelikopter import (
    GIT_REPO,
    repository_is_relevant_for_overview,
)
from rosahelikopter.github import graphql_fetch_access_permission_for_repoes_for_team_in_org
from rosahelikopter.markdown import (
    generate_markdown_template,
    write_markdown_files,
)


def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj


class hashable_dict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def fetch_and_filter_repositories(
    org_name: str,
    team_name: str,
    graphql_client: gql.Client,
) -> typing.Generator[GIT_REPO, None, None]:
    return (
        repo['node']
        for repo
        in graphql_fetch_access_permission_for_repoes_for_team_in_org(
            org_name=org_name,
            team_name=team_name,
            gql_transport=graphql_client,
        )
        if (
            # Remove empty results from GraphQL json output (happens sometimes)
            # This bug was fixed by giving the Github PAT the repo:security_events permission
            #  in addition to org:read permission. But keeping check just to avoid further issues.
            repo is not None and
            repository_is_relevant_for_overview(repo['node'], repo['permission'])
        )
    )



def main(
    teams: typing.Iterable[str],
    organizations: typing.Iterable[str],
    github_auth_token: str,
    make_org_folders: bool,
    make_team_files: bool,
    tee_output: bool,
    verbosity_level: int,
    **kwargs: dict[typing.Any, typing.Any],
) -> None:
    github_api_client = RequestsHTTPTransport(
        verify=True,
        url='https://api.github.com/graphql',
        headers=dict(Authorization=f"bearer {github_auth_token}"),
    )

    global_results = defaultdict(set)
    for org_name in sorted(organizations):
        if verbosity_level >= 1:
            click.echo(f"\nNow traversing {org_name}!", err=True)

        for team_name in sorted(teams):
            if verbosity_level >= 1:
                click.echo(f"\tLooking for repoes {team_name} is ADMIN for in {org_name}...", err=True)

            repoes_fetched = set(
                (
                    hashable_dict(repo)
                    for repo
                    in fetch_and_filter_repositories(
                        org_name=org_name,
                        team_name=team_name,
                        graphql_client=github_api_client,
                    )
                )
            )
            if verbosity_level >= 2:
                click.echo(f"\t\t{len(repoes_fetched)} found for {team_name} in {org_name}!", err=True)

            global_results[org_name] |= repoes_fetched
            global_results[team_name] |= repoes_fetched

        if verbosity_level >= 1:
            click.echo(f"{len(global_results[org_name])} repositories found in {org_name}!", err=True)

    # click.echo(json.dumps(global_results, indent=2, default=serialize_sets), err=True)
    if make_org_folders or make_team_files:
        # Save to files if requested!
        write_markdown_files(
            repoes_dataset=global_results,
            make_org_folders=make_org_folders,
            make_team_files=make_team_files,
            organizations=organizations,
            teams=teams,
        )
        if tee_output is False:
            # Job done! No output to stdout
            return

    # click.echo(f"{len(org_results)}", err=True)
    if all(
        len(global_results[org_name]) == 0
        for org_name in organizations
    ):
        click.echo(f"No repositories found for teams {teams} in any of orgs {organizations}!", err=True)
        click.exit(1)

    output_results = list()
    map(
        output_results.extend,
        (global_results[org_name] for org_name in organizations),
    )
    # click.echo(json.dumps(output_results, indent=2, default=serialize_sets), err=True)

    # Tabulate and write output
    markdown_output = generate_markdown_template(
        repositories=output_results,
        orgs=organizations,
        teams=teams,
    )
    click.echo(markdown_output)
