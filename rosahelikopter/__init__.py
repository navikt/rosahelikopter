# Python standard library imports
import typing


_GITHUB_GRAPHQL_RESPONSE = dict[
	str,
	typing.Union[
		str,
		bool,
	],
]
GIT_REPO = _GITHUB_GRAPHQL_RESPONSE


def repository_is_relevant_for_overview(
        repo_data: GIT_REPO,
        permission_string: str,
) -> bool:
    if repo_data['isArchived'] is not True or 'ADMIN' != permission_string:
        # We're not interested in parsing/displaying info of this repository.
        False
    return True
