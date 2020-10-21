#!/usr/bin/env python3 

import json
import textwrap
from pathlib import Path

doc_body = textwrap.dedent('''\
    # Helikopteroversikt

    | Reponavn | Beskrivelse |
    | :------: | :---------- |
    ''')

if __name__ == '__main__':
    data = json.loads(Path('indata.json').read_text())
    for org_name, repos in data.items():
        for repo_name, repo in repos.items():
            desc = repo['gh_data']['description']
            doc_body += textwrap.dedent(f"""\
                | [{org_name}/{repo_name}]({repo['gh_data']['html_url']}) \
                | {desc if desc else '**INGEN BESKRIVELSE**'} |
            """)


    print(doc_body)
