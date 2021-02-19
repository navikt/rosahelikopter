#!/usr/bin/env python3

# vim: shiftwidth=4 softtabstop=4 tabstop=4 expandtab

# Python standard library imports
import json
import sys

# Non-standard library python package imports
from python_graphql_client import GraphqlClient

# Imports of module(s) internal to this project/package
from rosahelikopter.string_templates import GRAPHQL_GITHUB_REPOS_QUERY_STRING


# TODO: Make this into a generator function for lazy evaluation
def graphql_fetch_access_permission_for_repoes_for_team_in_org(
    org_name: str,
    team_name: str,
    client: GraphqlClient,
    *,
    continue_pagination_token='',
):
    repositories_data = client.execute(
        _graphql_get_repository_access_permissions_for_team_in_org(
            org_name=org_name,
            team_name=team_name,
            repositories_continuation_token=continue_pagination_token,
        )
    )
    if repositories_data.get('errors', dict()):
        print(f"Failed GraphQL query with params:", file=sys.stderr)
        print(f"\torg_name='{org_name}'", file=sys.stderr, end=', ')
        print(f"team_name='{team_name}'", file=sys.stderr, end=', ')
        print(f"continuation_token='{continue_pagination_token}'", file=sys.stderr)
        print(json.dumps(repositories_data, indent=2), file=sys.stderr)
    try:
        repositories_data = repositories_data['data']['organization']['teams']['edges'][0]['node']['repositories']
    except IndexError:
        # Due to no results for given team/org combination
        return tuple()

    remaining_repositories = list()
    if repositories_data['pageInfo']['hasNextPage'] is True:
        remaining_repositories = graphql_fetch_access_permission_for_repoes_for_team_in_org(
            org_name=org_name,
            team_name=team_name,
            client=client,
            continue_pagination_token=repositories_data['pageInfo']['endCursor'],
        )

    return repositories_data['edges'] + remaining_repositories


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
    if not repositories_continuation_token:
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


if __name__ == '__main__':
    # Python standard library imports
    import os
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
            repo_data_list = graphql_fetch_access_permission_for_repoes_for_team_in_org(
                org_name=org_name,
                team_name=team_name,
                client=client,
            )
            repo_data_list = [r for r in repo_data_list if r]
            # print(json.dumps(repo_data_list, indent=2), file=sys.stderr)
            results = {
                repo_data['node']['nameWithOwner']: dict(
                    **repo_data['node'],
                    **{repo_data['permission']: team_name}
                )
                for repo_data in repo_data_list
            }
            for repo_data in repo_data_list:
                repo_name = repo_data['node']['nameWithOwner']
                if repo_name not in results:
                    results[repo_name] = repo_data['node']
                results[repo_name][f"team:{team_name}:repo_permission"] = repo_data['permission']

    # print(f"{len(results)}", file=sys.stderr)
    print(json.dumps({repo_name: results[repo_name] for repo_name in sorted(results)}, indent=2))
