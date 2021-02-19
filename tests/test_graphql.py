#!/usr/bin/env python3

# Python standard library imports
from typing import (
    Dict,
    Union,
)

# Non-standard library python package imports
from hypothesis import given
from hypothesis import strategies as st

# Imports of module(s) internal to this project/package
from rosahelikopter.string_templates import GRAPHQL_GITHUB_REPOS_QUERY_STRING


@given(
    st.fixed_dictionaries(
        {
            'org_name': st.text(min_size=1),
            'team_name': st.text(min_size=1),
        }
    ),
    st.one_of(st.none(), st.text()),
)
def ensure_required_graphql_query_variables_are_templated(
    input_dict: Dict[str, str],
    continuation_token: Union[str, None]
) -> bool:
    input_dict['repo_query_string'] = 'first: 100'
    if continuation_token:
        input_dict['repo_query_string'] += f", after: \"{continuation_token}\""
    generated_template = GRAPHQL_GITHUB_REPOS_QUERY_STRING.format(**input_dict)
    all(
        string_value in generated_template
        for _, string_value
        in input_dict.items()
    )
