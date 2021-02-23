#!/usr/bin/env python3
"""
Module containing "main()" logic for rosahelikopter.
"""

# Python standard library imports
from collections import OrderedDict
import json
import os
import typing

# 3rd-party python package imports
import click
import gql
from gql.transport.requests import RequestsHTTPTransport

# Imports of module(s) internal to this project/package
from rosahelikopter import GIT_REPO, repository_is_relevant_for_overview
from rosahelikopter.github import graphql_fetch_access_permission_for_repoes_for_team_in_org
from rosahelikopter.markdown import generate_markdown_template, write_markdown_files


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
) -> list[GIT_REPO]:
    # graphql_results = graphql_fetch_access_permission_for_repoes_for_team_in_org(
    #     org_name=org_name,
    #     team_name=team_name,
    #     gql_transport=graphql_client,
    # )
    # click.echo(f"{len(graphql_results)} repoes returned through grapqhl for {org_name}/{team_name}", err=True)
    # click.echo(f"{json.dumps(graphql_results, indent=2)}", err=True)
    correctly_configured_repoes = list()
    for repo_data in (
        repo_data
        for repo_data
        in graphql_fetch_access_permission_for_repoes_for_team_in_org(
            org_name=org_name,
            team_name=team_name,
            gql_transport=graphql_client,
        )
        # Remove empty results from GraphQL json output (happens sometimes)
        # This bug was fixed by giving the Github PAT the repo:security_events permission
        #  in addition to org:read permission. But keeping check just to avoid further issues.
        if repo_data
    ):
        repo_name = repo_data['node']['nameWithOwner']

        if not repository_is_relevant_for_overview(repo_data['node'], repo_data['permission']):
            click.echo(f"{json.dumps(repo_data, indent=2)}", err=True)
            # Repository does not match criteria for filtering
            continue

        correctly_configured_repoes.append(repo_data['node'])
    # click.echo(f"\t{len(correctly_configured_repoes)} repoes returned to main", err=True)
    return correctly_configured_repoes



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

    global_results = dict()
    for org_name in organizations:
        if verbosity_level >= 1:
            click.echo(f"\nNow traversing {org_name}!", err=True)

        if org_name not in global_results:
            global_results[org_name] = set()
        for team_name in teams:
            if verbosity_level >= 1:
                click.echo(f"\tLooking for repoes {team_name} is ADMIN for in {org_name}...", err=True)

            repoes_fetched = fetch_and_filter_repositories(
                org_name=org_name,
                team_name=team_name,
                graphql_client=github_api_client,
            )
            if verbosity_level >= 2:
                click.echo(f"\t\t{len(repoes_fetched)} found for {team_name} in {org_name}!", err=True)

            repoes_fetched = set(
                (
                    hashable_dict(repo)
                    for repo
                    in repoes_fetched
                )
            )
            if team_name not in global_results:
                global_results[team_name] = set()
            global_results[org_name] |= repoes_fetched
            global_results[team_name] |= repoes_fetched

        if verbosity_level >= 1:
            click.echo(f"\t{len(global_results[org_name])} repositories found in {org_name}!", err=True)

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
        return

    output_results = OrderedDict()
    for org_name in sorted(organizations):
        output_results.update(sorted(global_results.get(org_name, dict()).items()))
    # click.echo(json.dumps(output_results, indent=2, default=serialize_sets), err=True)

    # Tabulate and write output
    markdown_output = generate_markdown_template(output_results)
    click.echo(markdown_output)
