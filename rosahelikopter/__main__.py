#!/usr/bin/env python3
"""
Required file when running `python rosahelikopter` -> it's the one that's actually executed with such invocations.
Just used as a proxy to the `main()` function in `rosahelikopter/main.py`.
"""

# Imports of module(s) internal to this project/package
from rosahelikopter.cli import cli


if __name__ == '__main__':
    cli()
