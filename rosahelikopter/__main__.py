#!/usr/bin/env python3

# Python standard library imports
import json
import os

# 3rd-party python package imports
from python_graphql_client import GraphqlClient

# Imports of module(s) internal to this project/package
from rosahelikopter.github import graphql_fetch_access_permission_for_repoes_for_team_in_org


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
            repo_data_list = graphql_fetch_access_permission_for_repoes_for_team_in_org(
                org_name=org_name,
                team_name=team_name,
                client=client,
            )
            repo_data_list = [r for r in repo_data_list if r]
            # print(json.dumps(repo_data_list, indent=2), file=sys.stderr)
            for repo_data in repo_data_list:
                repo_name = repo_data['node']['nameWithOwner']
                if repo_name not in results:
                    results[repo_name] = repo_data['node']
                results[repo_name][f"team:{team_name}:repo_permission"] = repo_data['permission']

    # print(f"{len(results)}", file=sys.stderr)
    print(json.dumps({repo_name: results[repo_name] for repo_name in sorted(results)}, indent=2))
    

if __name__ == '__main__':
    main()
