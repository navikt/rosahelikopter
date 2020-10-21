#!/usr/bin/env python3

import contextlib
import json
import os
import requests
import sys


def get_repos_of_org(org_name, authorization_token):
    return requests.get(
        f"https://api.github.com/orgs/{org_name}/repos",
        headers=dict(
            Accept='application/vnd.github.v3+json',
            Authorization=f"token {authorization_token}"
        )
    ).json()


def read_repo_file(repo_name, org_name, file_path, *, ref_name='master'):
    response = requests.get(
        f"https://api.github.com/repos/{org_name}/{repo_name}/contents/{file_path}",
        headers=dict(
            Accept='application/vnd.github.v3.raw+json',
            Authorization=f"token {authorization_token}"
        ),
        params=dict(ref=ref_name),
    )
    # print(response.text, file=sys.stderr)
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

    #repos['org']['name'] = { codeowners: 'foo', gh_data: json_data, ... }
    for org_name in desired_orgs:
        repos = get_repos_of_org(org_name, authorization_token)
        orgs[org_name] = {r['name']: dict(gh_data=r) for r in repos}

        for repo_name, repo in orgs[org_name].items():
            with contextlib.suppress(KeyError):
                orgs[org_name][repo_name]['CODEOWNERS'] = read_repo_file(
                    repo_name=repo_name,
                    org_name=org_name,
                    file_path='CODEOWNERS',
                    ref_name=repo['gh_data']['default_branch'],
                )

    print(json.dumps(orgs, indent=2))
    sys.exit(0)

    repos_with_description = [r for r in repos if r['description'] is not None]
    print(f"Total repos found: {len(repos)}, of which {len(repos_with_description)} have description!", file=sys.stderr)

    all_repos['repos'], all_repos['repos_with_description'] = repos, repos_with_description

    repos_with_codeowners = list()
    for repo in repos:
        with contextlib.suppress(KeyError):
            repo['CODEOWNERS'] = read_repo_file(
                repo_name=repo['name'],
                org_name=repo['owner']['login'],
                file_path='CODEOWNERS',
                ref_name=repo['default_branch'],
            )
            repos_with_codeowners.append(repo)
    print(f"{len(repos_with_codeowners)} repos with CODEOWNERS file in root!")

    aura_repos = [r for r in repos_with_codeowners if 'navikt/aura' in r.get('CODEOWNERS', '')]
    # print(*[r['name'] for r in aura_repos], sep='\n')
    aura_owned_repos_with_description = {
        f"{repo['owner']['login']}/{repo['name']}": repo.get('description', None)
        for repo in aura_repos
    }

    print(json.dumps(aura_owned_repos_with_description, indent=2))
