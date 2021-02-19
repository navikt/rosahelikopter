#!/usr/bin/env python3
"""
Sub-module defining the program's interaction with the user via the commandline.
"""

# Python standard library imports
import json
import textwrap

# Non-standard library python package imports
import click

# Imports of module(s) internal to this project/package
from rosahelikopter.main import main

DEFAULT_TEAM_NAMES=(
    'aura',
    'nais',
    'naisdevice',
)


@click.command(
    options_metavar='<options>',
    context_settings=dict(
        help_option_names=['-h', '--help'],
        max_content_width=120,
    ),
    help=textwrap.dedent(
        f"""List all (un-archived) repositories in <GITHUB ORGS> for which the <GITHUB TEAMS> are ADMINs of.
        Output is a Markdown file with one repository per row in a table.
        The table has the columns: `Name (as GH URL)` and `Description (GH Repo description)`.

        <GITHUB TEAMS> is one or more Github team names (strings).
        <GITHUB TEAMS> defaults to the Github team names {DEFAULT_TEAM_NAMES} if unspecified."""
    )
)
@click.option(
    '-o', '--github-org', 'organizations',
    default=('navikt', 'nais'), multiple=True,
    type=str, metavar='<GITHUB ORGS>', show_default=True,
    help=textwrap.dedent(
        """One or more Github organization names whose repositories this tool will iterate through.
        Multiple can be specified as one per `-o/--github-org` flag."""
    ),

)
@click.argument(
    'TEAMS', nargs=-1, type=str, metavar='<GITHUB TEAMS>',
)
@click.option(
    '-T', '--separate-output-per-team', 'make_team_files', is_flag=True,
    help=textwrap.dedent(
        """Flag to change output of program from stdout to one file per team named '<team name>.md'.
        Can be used in conjunction with `--separate-output-per-org` flag.

        Intended for use when wanting to know which team has a relation to which repositories,
        """
    ),
)
@click.option(
    '-O', '--separate-output-per-org', 'make_org_folders',
    is_flag=True, default=False,
    help=textwrap.dedent(
        """Flag to output of program from stdout to `<org name>/overview.md` files.
        Can be used in conjunction with `--seperate-output-per-team` flag."""
    ),
)
@click.option(
    '--tee-output', 'tee_output',
    is_flag=True, default=False,
    help='Flag to send output of program to stdout even if other flag for writing to files have been set.',
)
@click.option(
    '-a', '--github-auth-token',
    type=str, envvar='GITHUB_USER_TOKEN', required=True,
    help=textwrap.dedent(
        """User token (PAT) with which to authenticate against Githubs GraphQL API.
        Defaults to environment variable "GITHUB_USER_TOKEN" if present."""
    ),
)
@click.option(
    '--verbose', '-v', 'verbosity',
    type=int, count=True,
    help=textwrap.dedent(
        """Verbosity level.
        Causes program to increase debug output during its execution.
        Multiple `-v`s increase verbosity.

        Final level of verbosity (V) is calculated as `V = sum(verbose) - sum(silent)`"""
    ),
)
@click.option(
    '--silent', '-s', 'silence',
    type=int, count=True,
    help=textwrap.dedent(
        """Quiet/silence level.
        Causes program to decrease debug output during its execution.
        Multiple `-s`s decrease verbosity.

        Final level of verbosity (V) is calculated as `V = sum(verbose) - sum(silent)`"""
    ),
)
# @click.pass_context
def cli(
    # 'ctx' is required for click CliRunner integration tests
    #   when checking exit_code, and for when to exit program early.
    # ctx,
    organizations: list[str],
    teams: list[str],
    make_org_folders: bool,
    make_team_files: bool,
    tee_output: bool,
    github_auth_token: str,
    verbosity: int,
    silence: int,
):
    local_vars = {name: value for name, value in locals().items() if not name.startswith('_')}
    # Set`verbosity_level`
    del local_vars['verbosity']
    del local_vars['silence']
    local_vars['verbosity_level'] = verbosity - silence

    # Set Github teams if empty
    if not teams:
        local_vars['teams'] = ('nais', 'aura')

    if local_vars['verbosity_level'] >= 2:
        # Remove so that json.dumps doesn't have a fit
        #  Use dict.pop() instead of del dict[key] here in case ctx is not in use
        local_vars.pop('ctx', None)
        click.echo(
            json.dumps(local_vars, indent=2),
            err=True,
        )
        # Add back so that functionality further down in program
        # continues to work as expected
        if 'ctx' in locals().keys(): local_vars['ctx'] = ctx

    main(**local_vars)

if __name__ == '__main__':
    cli()
