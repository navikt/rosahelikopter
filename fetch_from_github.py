#!/usr/bin/env python3

import contextlib
import json
import os
import requests
import sys
import time


def get_repos_of_org(org_name, authorization_token, *, max_pages=None):
    def get_next_url(response) -> str:
        if 'link' not in response.headers:
            return ''
        next_link = list(filter(
            lambda link_dict: link_dict['rel'] == 'next',
            requests.utils.parse_header_links(response.headers['link'])
        ))
        return '' if len(next_link) != 1 else next_link[0]['url']

    def check_page_limit(counter, page_limit):
        if not isinstance(page_limit, int): return True
        return counter <= page_limit

    json_data, counter = list(), 0
    target_url = f"https://api.github.com/orgs/{org_name}/repos?per_page=100"
    while target_url and check_page_limit(counter, max_pages):
        response = requests.get(
            url=target_url,
            headers=dict(
                Accept='application/vnd.github.v3+json',
                Authorization=f"token {authorization_token}",
            ),
        )
        if response.status_code in (403, 429):
            # 429 is the rate-limiting error code. Resets every hour
            print(
                f"Request {target_url} has been rate-limited! Sleeping for one hour.",
                file=sys.stderr,
            )
            time.sleep(60 * 60)
            continue
        assert response.status_code in range(200, 400)
        json_data.extend(response.json())
        target_url = get_next_url(response)
        counter += 1
    return json_data


def get_team_permissions_for_repo(repo_name, org_name):
    response = requests.get(
        f"https://api.github.com/repos/{org_name}/{repo_name}/teams",
        headers=dict(
            Accept='application/vnd.github.v3.raw+json',
            Authorization=f"token {authorization_token}",
        ),
    )
    if response.status_code == 404:
        raise RuntimeError(f"Cannot read {org_name}/{repo_name}'s team permissions!")
    assert response.status_code in range(200, 400)
    return response.json()


if __name__ == '__main__':
    try:
        authorization_token = os.environ['GITHUB_USER_TOKEN']
    except KeyError:
        print('Authorization token must be set in $GITHUB_USER_TOKEN', file=sys.stderr)
        sys.exit(1)

    results = dict()
    for org_name in ('navikt', 'nais'):
        for repo in get_repos_of_org(org_name, authorization_token):
            with contextlib.suppress(RuntimeError):
                repo['team_permissions'] = get_team_permissions_for_repo(
                    repo_name=repo['name'],
                    org_name=org_name,
                )
            results[f"{org_name}/{repo['name']}"] = repo

    print(json.dumps(results, indent=2))
