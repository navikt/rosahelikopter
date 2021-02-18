#!/usr/bin/env python3

# Python standard library imports
import textwrap


GRAPHQL_GITHUB_REPOS_QUERY_STRING = textwrap.dedent("""\
	query {{
	  organization(login: "{org_name}") {{
	    teams({team_query_string}) {{
	      edges {{
		node {{
		  ... on Team {{
		    repositories(first:100) {{
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
