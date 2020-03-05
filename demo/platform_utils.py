import sys
sys.path.append("..")

import json
import argparse

import pycloudmessenger.ffl.abstractions as ffl



def platform(config: str = 'cloud', credentials: str = None, user: str = None, password: str = None):
    if config == 'local':
        import comm.localapi as fflapi
    elif config == 'cloud':
        import pycloudmessenger.ffl.fflapi as fflapi
    else:
        raise ValueError('We currently support only `cloud` or `local` platform')

    ffl.Factory.register(config, fflapi.Context, fflapi.User, fflapi.Aggregator, fflapi.Participant)

    return ffl.Factory.context(config, credentials, user, password)


def create_args(description: str = None):
    """
    Set up command line args.

    :return: namespace of key/value cmdline args.
    :rtype: `namespace`
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--credentials', required=True, help='Original credentials file from IBM')
    parser.add_argument('--user', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--platform', required=False, default='cloud', help='Over-ride platform')
    return parser


"""
with open('../config') as cfg:
    config = json.load(cfg)

if config['platform'] == 'local':
    import comm.localapi as fflapi
elif config['platform'] == 'cloud':
    import pycloudmessenger.ffl.fflapi as fflapi
else:
    raise ValueError('We currently support only `cloud` or `local` platform')

platform = config['platform']
ffl.Factory.register(platform, fflapi.Context, fflapi.User, fflapi.Aggregator, fflapi.Participant)
topology = fflapi.Topology.star
"""
