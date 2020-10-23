#!/usr/bin/env python3

import json
import sys
import typing


def get_repos_missing_key(
    data: typing.Dict[str, typing.Dict[str, typing.Dict]],
    *keys_to_check: typing.Iterable[str],
) -> typing.Dict[str, typing.Dict[str, str]]:
    return_data = {key: dict() for key in keys_to_check}
    for org_name, repos in data.items():
        for repo_name, repo_data in repos.items():
            for missing_key in keys_to_check:
                if not repo_data.get(missing_key):
                    return_data[missing_key][f"{org_name}/{repo_name}"] = repo_data['html_url']
    return return_data


def make_markdown_table(data) -> typing.Dict[str, typing.Dict[str, str]]:
    # First two rows of output
    table = '| Reponavn | ' + '| '.join(data.keys()) + ' |\n'
    table += '| :--- | ' + '| '.join(':---: ' for _ in data.keys()) + ' |\n'

    # Re-format data for ease of iteration
    list_of_rows = dict()
    for missing_data, repo in data.items():
        for repo_name, repo_url in repo.items():
            key = f"[{repo_name}]({repo_url})"
            try:
                list_of_rows[key].append(missing_data)
            except KeyError:
                list_of_rows[key] = [missing_data]
    
    # Write table data, row for row
    for repo_name, missing_keys in list_of_rows.items():
        table += f"| {repo_name} "
        for key in data.keys():
            # Set check-mark for each key _not_ missing per repo/row
            # <ul><li>[x] item1</li><li>[ ] item2</li></ul>
            table += '| '
            table += ':heavy_check_mark:' if key not in missing_keys else ':x:'
        table += ' |\n'
    return table


if __name__ == '__main__':
    try:
        input_file = open(sys.argv[1], 'r')
    except IndexError:
        input_file = sys.stdin
    with input_file as f:
        json_string = f.read()

    try:
        data = json.loads(json_string)
    except json.decoder.JSONDecodeError as e:
        print(input_string, file=sys.stderr)
        raise e

    repos_missing_keys = get_repos_missing_key(
        data,
        'CODEOWNERS',
        'description',
    )
    # print(json.dumps(repos_missing_keys, indent=2))
    print(make_markdown_table(repos_missing_keys))
