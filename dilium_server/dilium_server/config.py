import os

DEBUG = bool(os.environ.get('DEBUG'))
TMP_BLOCKERS = {}
DEFAULT = object()
DATABASE = 'dilium.db' if not DEBUG else ':memory:'
CAPABILITIES = 'capabilities'
MAX_INSTANCES = 'maxInstances'
BROWSER_NAME = 'browserName'
CLIENT_UUID = 'client-uuid'
TMP_BLOCK_DURATION = 10
