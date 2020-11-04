#!/usr/bin/env python3


def is_owned_by_aura(repo):
    return any(
        permission['name'] in (
            'aura',
        )
        and permission['permission'] == 'admin'
        for permission in repo.get('team_permissions', [])
    )
