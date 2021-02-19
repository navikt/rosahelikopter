#!/usr/bin/env python3

# Python standard library imports
import re
from typing import Union

# Non-standard library python package imports
from hypothesis import given
from hypothesis import strategies as st

# Imports of module(s) internal to this project/package
from rosahelikopter.markdown import make_table
from rosahelikopter.main import repo_filter

MARKDOWN_VALID_TABLE_ROWS_REGEX_PATTERN = r'\| \[[-\w\d]+/[-\w\d]+\]\(.*\) \| .+ \|'
GITHUB_NAME_WITH_OWNER = r'[\w\d-]+/[\w\d-]+'
HYPOTHESIS_GITHUB_NAMES_CHARACTERS=st.characters(
    whitelist_categories=(
        # https://en.wikipedia.org/wiki/Unicode_character_property#General_Category
        'Lu',
        'Ll',
        'Nd',
    ),
)


# https://stackoverflow.com/a/1151705/1503549
class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


@given(
    st.lists(
        st.fixed_dictionaries(
            hashabledict(
                description=st.text(alphabet=HYPOTHESIS_GITHUB_NAMES_CHARACTERS, min_size=1),
                nameWithOwner=st.from_regex(GITHUB_NAME_WITH_OWNER, fullmatch=True),
                url=st.text(alphabet=HYPOTHESIS_GITHUB_NAMES_CHARACTERS, min_size=1),
                isArchived=st.booleans(),
                permissions=st.dictionaries(
                    st.sampled_from(('ADMIN', 'READER', 'USER')),
                    st.tuples(st.text(),),
                    dict_class=hashabledict,
                    min_size=1,
                    max_size=1,
                ),
            )
        ),
        unique=True,
        min_size=1,
    )
)
def ensure_markdown_output_table_matches_expected_size(input_repoes: list[dict[str, Union[str, bool]]]) -> bool:
    repoes = {repo['nameWithOwner']: repo for repo in input_repoes}
    num_valid_repoes = len([repo for repo in repoes.values() if repo_filter(repo)])
    num_valid_table_rows = 0
    for _ in re.finditer(MARKDOWN_VALID_TABLE_ROWS_REGEX_PATTERN, make_table(repoes)):
        num_valid_table_rows += 1
    assert(num_valid_repoes == num_valid_table_rows)
