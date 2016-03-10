# -*- mode: python tab-width: 4 coding: utf-8 -*-
# Dummy routine. Create your own secret.py with real values.
# Don't put the real values on GitHub
def get_connection(name):
    return {
        'fmphp_sample': {
            'hostspec': 'http://localhost',
            'username': 'user',
            'password': 'password',
            'db_name': 'FMPHP_Sample',
        },
        'connection2': {
            'hostspec': 'http://localhost:80',
            'username': 'user',
            'password': 'password'
        },
        'connection3': {
            'hostspec': 'https://localhost',
            'username': 'user',
            'password': 'password'
        },
        'connection4': {
            'hostspec': 'https://localhost:443',
            'username': 'user',
            'password': 'password'
        },
    }[name]
