# Rosahelikopter

This is a utility to generate an overview of repositories, giving a "birds-eye view" of repositories owned by teams and their descriptions.

## Requirements
- `poetry`
- `python3.9`

## Installation

First, fetch rosahelikopter's dependencies by running:
```bash
$ poetry install
```

## Example usage 

NB: Ensure you have a valid Github access token with all `repo` scope-permissions.  
As of right now, after a bug-hunting escapade, the `repo:security_events` permission _**also**_ seems to be necessary/required.

This token must be available as the environment variable `GITHUB_USER_TOKEN` while running the python scripts.

Then, run:
```bash
$ poetry run python rosahelikopter --help
```

Check `Makefile` for other runs/testing commands.

## Example usage for NAIS-people

An appropriately scoped `GITHUB_USER_TOKEN` is available in `gcloud` under the project named `nais-team-credentials`. Grabbing it for use as an environment variable is as simple as running:
```bash
$ export GITHUB_USER_TOKEN=$(gcloud secrets versions access 1 --secret='srvgithubnavikt-github-reader-token' --project='nais-team-credentials')
```

Then, as described before:
```bash
$ poetry run python rosahelikopter --help
```