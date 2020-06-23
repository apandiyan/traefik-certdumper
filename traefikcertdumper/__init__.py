import os
import sys

ACME_FILE = os.environ.get('TRAEFIK_ACME_FILE') if os.environ.get('TRAEFIK_ACME_FILE') else '/traefik/acme.json'
CERTDUMP_DIR = os.environ.get('TRAEFIK_CERTDUMP_DIR') if os.environ.get('TRAEFIK_CERTDUMP_DIR') else '/traefik/ssl'
CERTDUMPER_RETENTION = int(os.environ.get('CERTDUMPER_RETENTION')) if os.environ.get('CERTDUMPER_RETENTION') else 3
ARCHIVE_DIR = CERTDUMP_DIR + '/archive'

if not os.path.exists(ACME_FILE):
    print('ERROR: no ACME file found at {}'.format(ACME_FILE))
    sys.exit(1)
else:
    if not os.path.isfile(ACME_FILE):
        print('ERROR: {} is not a file'. format(ACME_FILE))
        sys.exit(1)

if not os.path.exists(CERTDUMP_DIR):
    print('INFO: creating certdump directory at {}'.format(CERTDUMP_DIR))
    os.mkdir(CERTDUMP_DIR)
    print('INFO: creating archive directory at {}'.format(ARCHIVE_DIR))
    os.mkdir(ARCHIVE_DIR)
