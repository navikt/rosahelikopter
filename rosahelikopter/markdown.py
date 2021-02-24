#!/usr/bin/env python3
"""
Module containing markdown-specific logic; writing files and making their content
"""

# Python standard library imports
import collections
import json
import pathlib
import textwrap
import typing

# Imports of module(s) internal to this project/package
from rosahelikopter import GIT_REPO


def make_markdown_table(
    repositories: typing.Iterable[GIT_REPO]
) -> str:
    # Table columns and horizontal justification
    table_markdown_string = textwrap.dedent('''\
        | Reponavn | Beskrivelse |
        | :------: | :---------- |''')

    # Table 'body'/contents
    for repo in repositories:
        desc, name = repo['description'], repo['nameWithOwner']
        table_markdown_string += f"\n| [{name}]({repo['url']}) | {desc if desc else '**Mangler beskrivelse!**'} |"

    return table_markdown_string


def generate_markdown_template(
    orgs: typing.Iterable[str],
    teams: typing.Iterable[str],
    repositories: typing.Iterable[GIT_REPO],
) -> str:
    # List of orgs used in intro template below
    orgs_string = ', '.join(
        (
            f"[{org}](https://github.com/{org})"
            for org in sorted(orgs)
        )
    )

    # List of teams used in intro template below
    indent = ' ' * 4
    teams_list = '\n'.join(
        (
            f"{indent}- @{team}"
            for team in sorted(teams)
        )
    )

    # Make document intro
    doc_body = textwrap.dedent(f"""\
    # Helikopteroversikt

    Dette er en oversikt over Github repoer som ligger innunder organisasjonen(e); {orgs_string}
    Tabelloversikten lister repoer som:
      - ikke er arkivert,
      - og som har følgende Github team(s) i organisasjonen(e) over listet som `ADMIN` i repoet(\[1\]):
    """)
    doc_body += teams_list + '\n' * 2

    # Add table
    doc_body += make_markdown_table(repositories)

    # Add footer
    doc_body += textwrap.dedent('\n\n\[1\]: <Github repo url> -> `Settings` fane -> `Access Management`.')
    return doc_body

def write_markdown_files(
    repoes_dataset: dict[str, list[GIT_REPO]],
    organizations: typing.Iterable[str],
    teams: typing.Iterable[str],
    make_org_folders: bool,
    make_team_files: bool,
) -> None:
    for org_name in organizations:
        # First set-up folder if flag is set
        file_output_dir = pathlib.Path.cwd()
        if make_org_folders and len(repoes_dataset[org_name]) > 0:
            file_output_dir = file_output_dir / org_name
            file_output_dir.mkdir(exist_ok=True)

        # Then, write to file specified with CLI options/flags
        if make_team_files:
            for team in teams:
                # Filter out repoes depending on `make_org_folders` flag and sort them
                file_specific_team_repoes = sorted(
                    filter(
                        lambda r: make_org_folders is False or (
                            make_org_folders and r['nameWithOwner'].startswith(f"{org_name}/")
                        ),
                        repoes_dataset.get(team, tuple())
                    ),
                    key=lambda repo: repo['nameWithOwner'],
                )
                if len(file_specific_team_repoes) == 0:
                    continue

                # Write to team-named file, but use the `file_output_dir` variable
                # to respect the logic of `make_org_folders`:
                output_file = file_output_dir / f"{team}.md"
                output_file.write_text(
                    generate_markdown_template(
                        teams=(team, ),
                        orgs=(org_name, ) if make_org_folders is True else organizations,
                        repositories=file_specific_team_repoes,
                    )
                )
        else:
            if len(repoes_dataset[org_name]) == 0:
                file_output_dir.rmdir()
                continue
            output_file = file_output_dir / "overview.md"
            output_file.write_text(
                generate_markdown_template(
                    teams=teams,
                    orgs=(org_name, ) if make_org_folders is True else organizations,
                    repositories=sorted(
                        repoes_dataset[org_name],
                        key=lambda repo: repo['nameWithOwner'],
                    )
                )
            )
    return
