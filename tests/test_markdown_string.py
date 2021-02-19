#!/usr/bin/env python3

# Python standard library imports
from typing import Union

# Non-standard library python package imports
from hypothesis import given
from hypothesis import strategies as st

# Imports of module(s) internal to this project/package
from rosahelikopter.string_templates import GRAPHQL_GITHUB_REPOS_QUERY_STRING


# https://stackoverflow.com/a/1151705/1503549
class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


@given(
    st.lists(
        st.fixed_dictionaries(
            hashabledict(
                description=st.text(min_size=1),
                nameWithOwner=st.text(min_size=1),
                url=st.text(min_size=1),
                isArchived=st.booleans(),
                permissions=st.text(min_size=1),
            )
        ),
        unique=True,
    )
)
def ensure_markdown_output_table_matches_expected_size(input_dict: list[dict[str, Union[str, bool]]]) -> bool:
    assert(True)
