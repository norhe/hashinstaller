import argparse
import subprocess
import platform
import zipfile
import os
import urllib.request
import urllib.error
import json
import shutil
import sys

import enterprise
import sys_utils
import config_builder
import systemd_utils
import file_utils

parser = argparse.ArgumentParser(description='Install HashiCorp tools')

parser.add_argument('--Program', '-p', choices=['consul', 'Consul', 'vault', 'Vault', 'nomad', 'Nomad','consul-template', 'envconsul'],
    default='consul', dest='program_name',
    help='Which tool to install.  Valid values are consul, vault, nomad, consul-template, envconsul.')
parser.add_argument('--Version', '-v', default='latest',help='The version to download and install (default: latest open source version)')
parser.add_argument('--Download-location', '-loc', default='https://releases.hashicorp.com', help='The URL to download from (default: https://releases.hashicorp.com)')
parser.add_argument('--Skip-download', type=bool, default=False, help='Use local archive')
parser.add_argument('--Archive-location', '-al', default='', help='Location of local archive')
parser.add_argument('--Install-dir', '-id', default='/usr/local/bin', help='Where to place the executable.  Default: /usr/local/bin')
parser.add_argument('--Create-users', '-cu', default=True, help='Create user or group')
#parser.add_argument('--no-install-prereqs', default=False, help='Do not install jq, wget, unzip'))
parser.add_argument('--Create-directories', '-cd', default=True, help='Create directories')
parser.add_argument('--Create-unit-files', '-cuf', default=True, help='Create systemd unit files')
parser.add_argument('--Enable-systemd-service', '-ess', default=True, help='Enable systemd service')
parser.add_argument('--Create-config-file', '-ccf',default=False, help="Build config file")

parser.add_argument('--Config-only', '-co', default=False, help="Only create the config file")

parser.add_argument('--Ent-prefix', '-ep', default='prem', help='What to append to the filename when downloading enterprise versions', choices=['prem', 'pro', 'ent'])
parser.add_argument('--Is-enterprise', '-ie', default=False, help='Append "enterprise" to filename')
parser.add_argument('--Override-filename', '-of', default=None, help='Specify file name for beta install (i.e, "consul-enterprise_1.6.0+prem-beta2_linux_amd64.zip"' )

# Consul/Nomad options
parser.add_argument('--Is-Server', '-server', type=bool, default=False, help="Install default server config file")
parser.add_argument('--Datacenter', '-dc', default='dc1', help="Which datacenter is the agent in?")
parser.add_argument('--Autojoin', '-aj', help="Autojoin stanza")
parser.add_argument('--Loglevel', '-log', default='INFO', help="Log level for config")

parser.add_argument('--Read-Config-stdin', default=False, help="Read config file piped in")
parser.add_argument('--Read-Config-File', default=False, help="Read config file piped in")
parser.add_argument('--Config-File', help='Location of config file (i.e., /tmp/client.hcl)')

args = parser.parse_args()

program_name = args.program_name.lower()

create_directories = args.Create_directories
create_user = args.Create_users
retrieve_binary = args.Skip_download == False
create_systemd = args.Create_unit_files
enable_service = args.Enable_systemd_service
build_conf = args.Create_config_file

# start the install
if __name__ == "__main__":
    if args.Config_only is False:
        if create_user:
            print('Creating {} user and group'.format(program_name))
            sys_utils.run_cmd('sudo adduser --no-create-home --disabled-password --gecos "" {}'.format(program_name))

        if create_directories:
            print("Creating directories")
            os.makedirs("/etc/{}/".format(program_name), exist_ok=True)
            shutil.chown("/etc/{}/".format(program_name), user=program_name, group=program_name)
            if program_name is not "vault":
                os.makedirs("/opt/{}/".format(program_name),exist_ok=True)
                shutil.chown("/opt/{}/".format(program_name), user=program_name, group=program_name)

        if retrieve_binary:
            if not args.Archive_location:
                print('Retrieving binary from {}'.format(args.Download_location))
                if args.Version.lower() == 'latest':
                    version = file_utils.get_latest_version(program_name)
                else:        
                    version = args.Version 
                if args.Download_location.startswith('http'):
                    url = '{}/{}'.format(args.Download_location, file_utils.build_download_url(program_name, version))
                    
                    print('Downloading {}'.format(url))
                    file_utils.download_binary(program_name, url)
                elif args.Download_location.startswith('s3'):
                    enterprise.retrieve_from_s3(args.Download_location, version, program_name, args.Ent_prefix, args.Override_filename)
                else:
                    print('unsupported download scheme/location: {}'.format(args.Download_location))
                    sys.exit(1)

            else:
                print('Unzipping binary {}'.format(args.Archive_location))
                sys_utils.unzip(args.Archive_location, program_name)
            sys_utils.unzip('/tmp/{}.zip'.format(program_name), program_name)
            shutil.move('/tmp/{}'.format(program_name), '{}/{}'.format(args.Install_dir, program_name))
            print('{} placed in {}'.format(program_name, args.Install_dir))


        if create_systemd:
            print('Creating systemd unit files...')
            path = '/lib/systemd/system/{}.service'.format(program_name)
            unit_file = open(path, 'w')
            units = {
                'consul'          : systemd_utils.build_consul_uf(args.Install_dir),
                'vault'           : systemd_utils.build_vault_uf(args.Install_dir),
                'nomad'           : systemd_utils.build_nomad_uf(args.Install_dir),
                'consul-template' : systemd_utils.build_consul_template_uf(args.Install_dir),
                'envconsul'       : systemd_utils.envconsul_unit_file(args.Install_dir)
            }
            unit_file.write(units[program_name])
            unit_file.close()

        if enable_service:
            commands = [
                "sudo systemctl daemon-reload",
                "sudo systemctl enable {}.service".format(program_name)
            ]
            print("Enabling service...")
            for cmd in commands:
                sys_utils.run_cmd(cmd)
        else:
            print("Not enabling service...")

        if build_conf:
            print("Building {} config file".format(program_name))
            config_builder.get_config_builder()[program_name](args.Is_server, args.Datacenter, args.Autojoin)

    if args.Config_only or args.Create_config_file:
        print("Building {} config file".format(program_name))
        #config_builder.get_config_builder()[program_name](args.Is_server, args.Datacenter, args.Autojoin)

