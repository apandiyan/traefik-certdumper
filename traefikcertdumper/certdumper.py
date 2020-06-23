import os
import sys
import json
import base64
import shutil
from datetime import datetime, timedelta

from traefikcertdumper import ACME_FILE, CERTDUMP_DIR, ARCHIVE_DIR, CERTDUMPER_RETENTION

cert_dir = CERTDUMP_DIR + '/live/certs'
pkey_dir = CERTDUMP_DIR + '/live/private'
now = datetime.now()


def retentionpolicy():
    try:
        b3days = (now - timedelta(days=int(CERTDUMPER_RETENTION))).strftime('%Y%m%d')
        del_dir_path = ARCHIVE_DIR + '/' + b3days + '*'
        shutil.rmtree(del_dir_path)
        print('INFO: retention policy days {} maintained'.format(CERTDUMPER_RETENTION))
    except Exception as e:
        print(e)


def backupcerts():
    source = CERTDUMP_DIR + '/live'
    dest = ARCHIVE_DIR + '/' + now.strftime('%Y%m%d_%H%M')
    if os.path.exists(source):
        shutil.copytree(source, dest)
        print('INFO: backup taken source: {0}; destination:{1}'.format(source, dest))
        retentionpolicy()


def base64decode(msg):
    base64_bytes = msg.encode('ascii')
    msg_bytes = base64.b64decode(base64_bytes)
    return msg_bytes.decode('ascii')


def checkdumpdirs():
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
    else:
        if not os.path.isdir(cert_dir):
            os.remove(cert_dir)
            os.makedirs(cert_dir)

    if not os.path.exists(pkey_dir):
        os.makedirs(pkey_dir)
    else:
        if not os.path.isdir(pkey_dir):
            os.remove(pkey_dir)
            os.makedirs(pkey_dir)


def dumpcerts():
    backupcerts()
    checkdumpdirs()

    with open(ACME_FILE, 'r') as f:
        acme_json = json.load(f)

    try:
        cert_resolver = 'le'
        if len(acme_json.keys()) != 1:
            print('ERROR: invalid acme.json file')
            sys.exit(1)
        else:
            for i in acme_json.keys():
                cert_resolver = i

        no_of_certificates = len(acme_json[cert_resolver]['Certificates'])
        print('INFO: no of certificates: {}'.format(no_of_certificates))
        if no_of_certificates > 0:
            for i in acme_json[cert_resolver]['Certificates']:
                domain_name = i['domain']['main']
                certificate = base64decode(i['certificate'])
                privkey = base64decode(i['key'])
                cert_file = cert_dir + '/' + domain_name + '.pem'
                privkey_file = pkey_dir + '/' + domain_name + '.key'
                with open(privkey_file, 'w') as pf:
                    pf.write(privkey)
                    print('INFO: {} is dumped'.format(privkey_file))
                with open(cert_file, 'w') as cf:
                    cf.write(certificate)
                    print('INFO: {} is dumped'.format(cert_file))
    except Exception as e:
        print(e)
