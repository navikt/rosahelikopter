#!/usr/bin/env python3

# Python standard library imports
import json
import textwrap
from typing import Dict


def make_table(data: Dict[str, Dict[str, str]]) -> str:
    table = textwrap.dedent('''\
        | Reponavn | Beskrivelse |
        | :------: | :---------- |''')
    for repo_name, repo in data.items():
        if (
            repo['isArchived'] is True
            or 'ADMIN' not in repo['permissions']
        ):
            # We're not interested in parsing/displaying info of this repository.
            continue
        desc = repo['description']
        table += f"\n| [{repo_name}]({repo['url']}) | {desc if desc else '**Mangler beskrivelse!**'} |"
    return table


def make_markdown_template(repo_data: Dict[str, Dict[str, str]]) -> str:
    # Tabulate and write output
    doc_body = textwrap.dedent('''\
    # Helikopteroversikt

    Dette er en oversikt over Github repositories fra innunder `navikt` og `nais` organisasjonene.
    Tabelloversikten lister alle ikke-arkiverte repoer som har spesifiserte (hardkodede) Github Teams listet som `'admin'`s.

    ''')
    doc_body += make_table(repo_data)
    return doc_body


if __name__ == '__main__':
    # Python standard library imports
    import argparse
    import sys

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

    make_markdown_template(data)
    print(doc_body)
