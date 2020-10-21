# Rosahelikopter

This is a trivial utility to generate a central overview of repositories, to give a birds-eye view of our repositories and their descriptions.

## Example usage 

NB: Ensure you have a valid Github access token with all `repo` scope-permissions.
This token must be available as the environment variable `GITHUB_USER_TOKEN` while running the python scripts.

Then, run:

pipenv run ./fetch_from_github.py | pipenv run ./generate_markdown.py | multimarkdown > test.html
