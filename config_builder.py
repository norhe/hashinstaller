
# Please note that this is not a fully featured lexer/parser.  You must 
# ensure that you are passing in what will become valid HCL.
def build_hcl_config(conf, value):
    conf += conf + "\n{}".format(value)
    return conf

def build_consul_config(is_server, dc, aj):
    conf = 'client_addr = "0.0.0.0"\ndata_dir    = "/opt/consul"'
    conf = build_hcl_config(conf, 'server = {}'.format(str(is_server).lower()))
    conf = build_hcl_config(conf, 'datacenter = {}'.format(str(dc).lower()))
    conf = build_hcl_config(conf, 'retry_join = [{}]'.format(str(aj)))
    return conf

def build_nomad_config(is_server, dc, aj):
    conf = 'client_addr = "0.0.0.0"\ndata_dir    = "/opt/nomad"'
    conf = build_hcl_config(conf, 'server = {}'.format(str(is_server).lower()))
    conf = build_hcl_config(conf, 'datacenter = {}'.format(str(dc).lower()))
    conf = build_hcl_config(conf, 'retry_join = [{}]'.format(str(aj)))
    return conf

def build_vault_config():
    conf = "ui = true\n"
    conf = vault_storage(conf)
    conf = vault_telemetry(conf)
    conf = vault_listener(conf)
    return conf

def vault_storage(conf):
    return

def vault_telemetry(conf):
    return

def vault_listener(conf):
    return

# Reference the function based on program_name 
config_builder = {
    'consul' : build_consul_config,
    'vault'  : build_vault_config,
    'nomad'  : build_nomad_config
}

def get_config_builder():
    return config_builder

client_hcl = """
client_addr      = "0.0.0.0"
data_dir         = "/opt/consul"
datacenter       = "east"
log_level        = "INFO"
server           = false
acl_datacenter   = "east"
acl_down_policy  = "extend-cache"
retry_join       = [
    "provider=gce project_name=connect-env tag_value=consul-server"
]
"""