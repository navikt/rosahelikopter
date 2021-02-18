#!/usr/bin/env python3

# Python standard library imports
from typing import Dict

# Non-standard library python package imports
from hypothesis import given
from hypothesis import strategies as st

# Imports of module(s) internal to this project/package
from rosahelikopter.string_templates import GRAPHQL_GITHUB_REPOS_QUERY_STRING


@given(
    st.fixed_dictionaries(
        dict(
            org_name=st.text(min_size=1),
            team_query_string=st.text(min_size=1),
        )
    )
)
def ensure_required_graphql_query_variables_are_templated(input_dict: Dict[str, str]) -> bool:
    generated_template = GRAPHQL_GITHUB_REPOS_QUERY_STRING.format(**input_dict)
    all(
        string_value in generated_template
        for _, string_value
        in input_dict.items()
    )
