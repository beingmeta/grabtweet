import os
import sys
import yaml

PROFILE=False

__all__ = ['PROFILE', 'CONFIG']

if len(sys.argv) > 2:
    PROFILE=sys.argv[2]
elif os.getenv('PROFILE'):
    PROFILE=os.getenv('PROFILE')
else:
    PROFILE='combo'

if os.getenv("CREDENTIALS"):    
    FILE = os.getenv("CREDENTIALS")
else:
    FILE = os.path.join(os.path.dirname(__file__), 'config.yml')

CONFIGS = yaml.load(open(FILE))

if CONFIGS[PROFILE]:
    CONFIG = CONFIGS[PROFILE]
else:
    CONFIG = CONFIGS['default']
