#!/usr/bin/env python3 

import json
import sys
import textwrap


def is_owned_by_aura(repo):
    return any(
        owner in repo.get('CODEOWNERS', '')
        for owner
        in ('navikt/aura', 'nais/aura')
    )


def make_table(data, *, predicate=is_owned_by_aura):
    table = textwrap.dedent('''\
        | Reponavn | Beskrivelse |
        | :------: | :---------- |''')
    for org_name, repos in data.items():
        for repo_name, repo in repos.items():
            if not predicate(repo): continue
            desc = repo['gh_data']['description']
            table += f"\n| [{org_name}/{repo_name}]({repo['gh_data']['html_url']})"
            table += f" | {desc if desc else '**Mangler beskrivelse!**'} |"
    return table


if __name__ == '__main__':
    data = json.load(sys.stdin)
    doc_body = textwrap.dedent('''\
    # Helikopteroversikt

    Dette er en oversikt over repositories med enten `navikt/aura` eller `nais/aura` i sin [`CODEOWNERS`](https://docs.github.com/en/free-pro-team@latest/github/creating-cloning-and-archiving-repositories/about-code-owners)-fil på repo-rotnivå.

    ''')
    doc_body += make_table(data, predicate=is_owned_by_aura)
    print(doc_body)
