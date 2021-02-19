#!/usr/bin/env python3
"""
Sub-module defining the program's interaction with the user via the commandline.
"""

import json
import textwrap

import click

from rosahelikopter.main import main


@click.command(
    context_settings=dict(
        help_option_names=['-h', '--help'],
        max_content_width=120,
    )
)
@click.option(
    '-o', '--github-org', 'organizations',
    default=('navikt', 'nais'), multiple=True, type=str,
    help=textwrap.dedent(
        """\
        One or more Github organization names whose repositories this tool will iterate through.
        Can be specified one per `-o/--github-org` flag.
        """
    ),

)
@click.argument(
    'TEAMS', nargs=-1, type=str,
)
@click.option(
    '--separate-output-per-team', 'separate_team_output', is_flag=True,
    help='Flag to tell the program to separate outputs into files separated by folders per organization.',
)
@click.option(
    '--separate-output-per-org', 'separate_org_output',
    is_flag=True, default=False,
    help='Flag to tell the program to separate outputs into one file per team.'
)
@click.option(
    '--verbose', '-v', 'verbosity',
    type=int, count=True,
    help=textwrap.dedent(
        """\
        Verbosity level.

        \b
        Causes program to increase debug output during its execution.
        Multiple `-v`s increase verbosity.

        "Final level of verbosity" (V) is calculated as `V = sum(verbosity) - sum(silent)`
        """
    ),
)
@click.option(
    '--silent', '-s', 'silence',
    type=int, count=True,
    help=textwrap.dedent(
        """\
        Quiet/silence level.

        \b
        Causes program to silence debug output during its execution.
        Multiple `-s`s decrease verbosity.

        "Final level of verbosity" (V) is calculated as `V = sum(verbosity) - sum(silent)`
        """
    ),
)
@click.pass_context
def cli(
    ctx,
    organizations: list[str],
    teams: list[str],
    separate_org_output: bool,
    separate_team_output: bool,
    verbosity: int,
    silence: int,
):
    """List all repositories in GITHUB-ORG for  which the GITHUB-TEAMS have ADMIN role.

    One or more Github team names that must have some access rights to the repositories in the specified orgs.
    This argument parameter is a variadic one and doesn't need any `-X/--XY` flagging.

    Defaults to Github team names 'nais' and 'aura' if unspecified."""

    local_vars = {**locals()}

    # Set`verbosity_level`
    del local_vars['verbosity']
    del local_vars['silence']
    local_vars['verbosity_level'] = verbosity - silence

    # Set Github teams if empty
    if not teams:
        local_vars['teams'] = ('nais', 'aura')

    if local_vars['verbosity_level'] >= 2:
        # Remove so that json.dumps doesn't have a fit
        del local_vars['ctx']
        click.echo(
            json.dumps(local_vars, indent=2),
            err=True,
        )
        # Add back so that functionality further down in program
        # continues to work as expected
        local_vars['ctx'] = ctx

    main()

if __name__ == '__main__':
    cli()
