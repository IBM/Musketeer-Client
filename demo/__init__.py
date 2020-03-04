import json

import pycloudmessenger.ffl.abstractions as ffl


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
