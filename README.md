# Rosahelikopter

This is a utility to generate an overview of repositories, giving a "birds-eye view" of repositories owned by teams and their descriptions.

## Requirements
- `poetry`
- `python3.9`

## Example usage 

NB: Ensure you have a valid Github access token with all `repo` scope-permissions.
As of right now, after a bug-hunting escapade, the `repo:security_events` permission _**also**_ seems to be necessary/required.

This token must be available as the environment variable `GITHUB_USER_TOKEN` while running the python scripts.

Then, run:
```bash
$ poetry run rosahelikopter --help
```

Check `Makefile` for other runs/testing commands.
