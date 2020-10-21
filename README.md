# Rosahelikopter

This is a trivial utility to generate a central overview of repositories, to give a birds-eye view of our repositories and their descriptions.

## Example usage 

First, ensure you have a valid Github access token (TODO: Figure out exactly which permissions this token needs). Put that in GITHUB_USER_TOKEN.

Then, run:

pipenv run ./fetch_from_github.py | pipenv run ./generate_markdown.py | multimarkdown > test.html
