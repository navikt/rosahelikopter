#!/usr/bin/env python3 

import argparse
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
            f"\nInvalid JSON in '{error_source}' - ensure the file/stdin contains valid JSON.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Tabulate and write output
    doc_body = textwrap.dedent('''\
    # Helikopteroversikt

    Dette er en oversikt over repositories med enten `navikt/aura` eller `nais/aura` i sin [`CODEOWNERS`](https://docs.github.com/en/free-pro-team@latest/github/creating-cloning-and-archiving-repositories/about-code-owners)-fil på repo-rotnivå.

    ''')
    doc_body += make_table(data, predicate=is_owned_by_aura)
    print(doc_body)
