#!/usr/bin/env python3

# vim: shiftwidth=4 softtabstop=4 tabstop=4 expandtab

# Python standard library imports
import json
import sys
import typing

# Non-standard library python package imports
import click
import gql
from gql.transport import Transport

# Imports of module(s) internal to this project/package
from rosahelikopter.string_templates import GRAPHQL_GITHUB_REPOS_QUERY_STRING


def graphql_fetch_access_permission_for_repoes_for_team_in_org(
    org_name: str,
    team_name: str,
    gql_transport: Transport,
) -> typing.Generator[dict, None, None]:
    client = gql.Client(transport=gql_transport)
    continue_pagination_token = ''
    while True:
        # Build graphql query string
        query_string = _graphql_get_repository_access_permissions_for_team_in_org(
            org_name=org_name,
            team_name=team_name,
            repositories_continuation_token=continue_pagination_token,
        )

        # Execute query
        query = gql.gql(query_string)
        graphql_response = client.execute(query)

        # click.echo(json.dumps(graphql_response, indent=2), err=True)
        # Handle errors
        if graphql_response.get('errors', False):
            click.echo(f"Failed GraphQL query with params:", err=True)
            click.echo(
                (
                    f"\torg_name='{org_name}', team_name='{team_name}'"
                    f", continuation_token='{continue_pagination_token}'"
                ),
                err=True
            )
            click.echo(json.dumps(graphql_response, indent=2), err=True)
        try:
            graphql_response = graphql_response['organization']['teams']['edges'][0]['node']['repositories']
        except IndexError:
            # Due to no results for given team/org combination
            yield tuple()
            break

        # if org_name == 'navikt' and team_name == 'pig-sikkerhet':
        #     click.echo(json.dumps(graphql_response, indent=2), err=True)
        # Return
        yield from graphql_response['edges']

        if graphql_response['pageInfo']['hasNextPage'] is False:
            # No more results to yield, finish while-loop and session
            break

        # Continue next loop with same async http session yielding remaining results
        continue_pagination_token = graphql_response['pageInfo']['endCursor']

    return


def _graphql_get_repository_access_permissions_for_team_in_org(
    org_name: str,
    team_name: str,
    *,
    repositories_continuation_token=None
):
    # Build query parameters which might change depending on pagination
    query_parameters = dict(
        first=100,  # Max repos github lets ut fetch per query
        after=f"\"{repositories_continuation_token}\""
    )
    if not repositories_continuation_token or repositories_continuation_token is True:
        del query_parameters['after']

    # Build multi-line grapqhl query string _with_ given query params
    return GRAPHQL_GITHUB_REPOS_QUERY_STRING.format(
        org_name=org_name,
        team_name=team_name,
        repo_query_string=', '.join(
            [
                f"{key}: {value}"
                for key, value
                in query_parameters.items()
            ]
        )
    )
