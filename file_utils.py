import urllib.request
import json
import platform
import sys

# should return something like 'consul_1.2.3'
def build_dir_name(program_name, version):
    return '{}_{}'.format(program_name, get_version(program_name, version))

def get_version(program_name, version):
    if version.lower() is 'latest':
        return get_latest_version(program_name)
    else:
        return version

# Should return something like '1.2.3'
# Please note that the checkpoint API doesn't support Vault
def get_latest_version(program_name):
    url = 'https://checkpoint-api.hashicorp.com/v1/check/{}'.format(program_name)
    try:
        with urllib.request.urlopen(url) as response:
            text = response.read().decode('utf-8')
            return json.loads(text)['current_version']
    except urllib.error.HTTPError as err:
        print('Problem retrieving version from {}.\nTry to manually specify a version (e.g., -v 1.2.3).\nThe error was {}:  Exiting!'.format(url, err))
        sys.exit(1)


# https://releases.hashicorp.com/consul/1.2.3/
def build_download_url(program_name, version, is_enterprise = None, ent_prefix = None):
    return '{}/{}/{}'.format(program_name, version, build_file_name(program_name, version, is_enterprise, ent_prefix))

# filename: consul_1.2.3_linux_amd64.zip
def build_file_name(program_name, version, is_enterprise, ent_prefix):
    if is_enterprise:
        if program_name == 'nomad' and ent_prefix == 'prem':
            return '{}-enterprise_{}+{}_{}_amd64.zip'.format(program_name, version, 'ent', platform.system().lower())
        elif program_name is 'nomad' and ent_prefix is 'pro':
            return '{}-enterprise_{}+{}_{}_amd64.zip'.format(program_name, version, ent_prefix, platform.system().lower())
        else:
            return '{}-enterprise_{}+{}_{}_amd64.zip'.format(program_name, version, ent_prefix, platform.system().lower())
    else:
        return '{}_{}_{}_amd64.zip'.format(program_name, version, platform.system().lower())
   

def download_binary(program_name, url):
    try:
        urllib.request.urlretrieve(url, '/tmp/{}.zip'.format(program_name))
    except Exception as err:
        print("Error downloading binary from {}.  The error was {}".format(url, err))
