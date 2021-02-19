#!/usr/bin/env python3

# Python standard library imports
import json
import textwrap


def make_table(data: dict[str, dict[str, str]]) -> str:
    table = textwrap.dedent('''\
        | Reponavn | Beskrivelse |
        | :------: | :---------- |''')
    for repo_name, repo in data.items():
        desc = repo['description']
        table += f"\n| [{repo_name}]({repo['url']}) | {desc if desc else '**Mangler beskrivelse!**'} |"
    return table


def make_markdown_template(repo_data: dict[str, dict[str, str]]) -> str:
    # Tabulate and write output
    doc_body = textwrap.dedent('''# Helikopteroversikt

    Dette er en oversikt over Github repositories fra innunder `navikt` og `nais` organisasjonene.
    Tabelloversikten lister alle ikke-arkiverte repoer som har spesifiserte (hardkodede) Github Teams listet som `'admin'`s.

    ''')
    doc_body += make_table(repo_data)
    return doc_body
