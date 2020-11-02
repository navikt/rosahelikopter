#!/usr/bin/env python3 

import argparse
import json
import sys
import textwrap


def is_owned_by_aura(repo):
    return any(
        permission['name'] in (
            'aura',
        )
        and permission['permission'] == 'admin'
        for permission in repo.get('team_permissions', [])
    )


def make_table(data, *, predicate=is_owned_by_aura):
    table = textwrap.dedent('''\
        | Reponavn | Beskrivelse |
        | :------: | :---------- |''')
    for org_name, repos in data.items():
        for repo_name, repo in repos.items():
            if not predicate(repo): continue
            if repo['archived'] == True: continue
            desc = repo['description']
            table += f"\n| [{org_name}/{repo_name}]({repo['html_url']})"
            table += f" | {desc if desc else '**Mangler beskrivelse!**'} |"
    return table


if __name__ == '__main__':
    # Set up CLI
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_file',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='JSON input file. Defaults to stdin when not defined.',
    )
    args = parser.parse_args()

    # Parse input
    try:
        data = json.load(args.input_file)
    except json.decoder.JSONDecodeError:
        error_source = '<stdin>' if args.input_file is sys.stdin else args.input_file
        print(
            f"\nInvalid JSON in '{error_source}' - ensure the source contains valid JSON.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Tabulate and write output
    doc_body = textwrap.dedent('''\
    # Helikopteroversikt

    Dette er en oversikt samlet fra Github repositories innunder fra `navikt` og `nais` organisasjonene.
    Tabellen lister alle repoer som har spesifiserte (hardkodede) Github Teams listet som `'admin'` på repo-nivå.

    ''')
    doc_body += make_table(data, predicate=is_owned_by_aura)
    print(doc_body)
