

# Including our unit files
def build_consul_uf(install_dir):
  consul_unit_file = '''
  [Unit]
  Description=Consul Agent
  Requires=network-online.target
  After=network.target

  [Service]
  User=consul
  Group=consul
  ExecStart={}/consul agent -config-dir /etc/consul/ $FLAGS
  ExecReload=/bin/kill -HUP $MAINPID
  KillSignal=SIGTERM
  Restart=on-failure
  LimitNOFILE=131072

  [Install]
  WantedBy=multi-user.target
  '''.format(install_dir)
  return consul_unit_file

def build_vault_uf(install_dir):
  vault_unit_file = '''
  [Unit]
  Description="HashiCorp Vault - A tool for managing secrets"
  Documentation=https://www.vaultproject.io/docs/
  Requires=network-online.target
  After=network-online.target
  ConditionFileNotEmpty=/etc/vault/vault.hcl
  Wants=consul.service
  After=consul.service

  [Service]
  User=vault
  Group=vault
  ProtectSystem=full
  ProtectHome=read-only
  PrivateTmp=yes
  PrivateDevices=yes
  #SecureBits=keep-caps
  Capabilities=CAP_IPC_LOCK+ep
  CapabilityBoundingSet=CAP_SYSLOG CAP_IPC_LOCK
  LimitMEMLOCK=infinity
  NoNewPrivileges=yes
  ExecStart={}/vault server -config=/etc/vault/vault.hcl
  ExecReload=/bin/kill --signal HUP $MAINPID
  KillMode=process
  KillSignal=SIGINT
  Restart=on-failure
  RestartSec=5
  TimeoutStopSec=30
  StartLimitInterval=60
  StartLimitBurst=3

  [Install]
  WantedBy=multi-user.target
  '''.format(install_dir)
  return vault_unit_file

def build_nomad_uf(install_dir):
  nomad_unit_file = '''
  [Unit]
  Description=Nomad
  Documentation=https://nomadproject.io/docs/
  Wants=network-online.target
  After=network-online.target

  # If you are running Consul, please uncomment following Wants/After configs.
  # Assuming your Consul service unit name is "consul"
  Wants=consul.service
  After=consul.service

  [Service]
  KillMode=process
  KillSignal=SIGINT
  ExecStart={}/nomad agent -config /etc/nomad
  ExecReload=/bin/kill -HUP $MAINPID
  Restart=on-failure
  RestartSec=2
  StartLimitBurst=3
  StartLimitInterval=10
  LimitNOFILE=65536

  [Install]
  WantedBy=multi-user.target
  '''.format(install_dir)
  return nomad_unit_file

def build_consul_template_uf(install_dir):
  consul_template_unit_file = '''
  [Unit]
  Description=consul-template
  Requires=network-online.target
  After=network-online.target consul.service

  [Service]
  Restart=on-failure
  ExecStart={}/consul-template $OPTIONS -config=/etc/consul-template

  [Install]
  WantedBy=multi-user.target
  '''.format(install_dir)
  return consul_template_unit_file

def envconsul_unit_file(install_dir):
  envconsul_unit_file = '''
  [Unit]
  Description=envconsul
  Requires=network-online.target
  After=network-online.target consul.service

  [Service]
  Restart=on-failure
  ExecStart={}/envconsul $OPTIONS -config=/etc/envconsul

  [Install]
  WantedBy=multi-user.target
  '''.format(install_dir)
  return envconsul_unit_file
