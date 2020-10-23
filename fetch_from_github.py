#!/usr/bin/env python3

import contextlib
import json
import os
import requests
import sys


# TODO: 429 Status Code - sleep for 60 minutes
def get_repos_of_org(org_name, authorization_token):
    json_data = list()
    def get_next_url(response) -> str:
        next_link = list(filter(
            lambda link_dict: link_dict['rel'] == 'next',
            requests.utils.parse_header_links(response.headers['link'])
        ))
        return '' if len(next_link) != 1 else next_link[0]['url']

    target_url = f"https://api.github.com/orgs/{org_name}/repos?per_page=100"
    while target_url:
        response = requests.get(
            url=target_url,
            headers=dict(
                Accept='application/vnd.github.v3+json',
                Authorization=f"token {authorization_token}",
            ),
        )
        json_data.extend(response.json())
        target_url = get_next_url(response)
    return json_data


def read_repo_file(repo_name, org_name, file_path, *, ref_name='master'):
    response = requests.get(
        f"https://api.github.com/repos/{org_name}/{repo_name}/contents/{file_path}",
        headers=dict(
            Accept='application/vnd.github.v3.raw+json',
            Authorization=f"token {authorization_token}"
        ),
        params=dict(ref=ref_name),
    )
    if response.status_code == 404:
        raise KeyError(f"'{file_path}' not found in '{org_name}/{repo_name}@{ref_name}'")
    return response.text


if __name__ == '__main__':
    try:
        authorization_token = os.environ['GITHUB_USER_TOKEN']
    except KeyError:
        print('Authorization token must be set in $GITHUB_USER_TOKEN', file=sys.stderr)
        sys.exit(1)

    desired_orgs = ('navikt', 'nais')
    orgs = {}

    for org_name in desired_orgs:
        repos = get_repos_of_org(org_name, authorization_token)
        orgs[org_name] = {r['name']: r for r in repos}

        for repo_name, repo in orgs[org_name].items():
            with contextlib.suppress(KeyError):
                orgs[org_name][repo_name]['CODEOWNERS'] = read_repo_file(
                    repo_name=repo_name,
                    org_name=org_name,
                    file_path='CODEOWNERS',
                    ref_name=repo['default_branch'],
                )

    print(json.dumps(orgs, indent=2))
