#!/usr/bin/env python3

# Python standard library imports
import textwrap


GRAPHQL_GITHUB_REPOS_QUERY_STRING = textwrap.dedent("""\
    query {{
      organization(login: "{org_name}") {{
        teams(first: 1, query: "{team_name}") {{
          edges {{
            node {{
              ... on Team {{
                repositories({repo_query_string}) {{
                  pageInfo {{
                    endCursor
                    hasNextPage
                }}
                  totalCount
                  edges {{
                    permission
                    node {{
                      description
                      nameWithOwner
                      url
                      isArchived
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}""")
