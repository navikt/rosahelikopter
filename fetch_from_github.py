#!/usr/bin/env python3

import contextlib
import json
import os
import sys
import textwrap

from python_graphql_client import GraphqlClient


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
    )['data']['organization']['teams']['edges'][0]['node']['repositories']

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
        first=1,
        query=f"\"{team_name}\"",
        after=f"\"{repositories_continuation_token}\""
    )
    if not repositories_continuation_token:
        del query_parameters['after']
    team_query_string = ', '.join([
        f"{key}: {value}"
        for key, value
        in query_parameters.items()
    ])

    # Build multi-line query string _with_ built query params
    return textwrap.dedent(f"""\
        query {{
          organization(login: "{org_name}") {{
            teams({team_query_string}) {{
              edges {{
                node {{
                  ... on Team {{
                    repositories(first:100) {{
                      pageInfo {{
                        endCursor
                        hasNextPage
                      }}
                      totalCount
                      edges {{
                        permission
                        node {{
                          description
                          nameWithOwner
                          url
                          isArchived
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}""")


if __name__ == '__main__':
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
            for repo_data in graphql_fetch_access_permission_for_repoes_for_team_in_org(
                org_name=org_name,
                team_name=team_name,
                client=client,
            ):
                repo_name = repo_data['node']['nameWithOwner']
                if repo_name not in results:
                    results[repo_name] = repo_data['node']
                results[repo_name][f"team:{team_name}:repo_permission"] = repo_data['permission']

    print(json.dumps(results, indent=2))
