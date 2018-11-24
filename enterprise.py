import sys
import urllib.parse
import file_utils

# only import boto3 if we're downloading from s3 as these will need to 
# installed on the target system (pip3 install botocore boto3).
# boto3 will look for access credentials in your .aws/credentials file, or
# in AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SESSION_TOKEN
# environment variables.  Use either method to pass in valid credentials
def s3_download(url, program_name):
    import botocore
    import boto3
    
    p = urllib.parse.urlparse(url)
    
    client = boto3.client('s3')

    try:
        #s3.Bucket(p.netloc).download_file(filename, '/tmp/{}.zip'.format(program_name))
        client.download_file(p.netloc, p.path[1:], "/tmp/{}.zip".format(program_name))
        print("Found file...")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    except Exception as err:
        print('Exception occurred: {}'.format(err))

def retrieve_from_s3(url, version, program_name, ent_prefix):
    ent_url = build_ent_url(url, program_name, version, ent_prefix)
    print('Downloading {} from s3...'.format(ent_url))
    s3_download(ent_url, program_name)
    

# s3://hc-enterprise-binaries/consul/prem/1.3.0/
# s3://hc-enterprise-binaries/vault/prem/0.11.3/
def build_ent_url(url, program_name, version, ent_prefix):
    ent_url = ''
    if program_name == 'nomad':
      if url.endswith('/'):
        ent_url = '{}nomad-enterprise/{}/{}'.format(url, version, file_utils.build_file_name(program_name, version, True, ent_prefix))
      else:
        ent_url = '{}/nomad-enterprise/{}/{}'.format(url, version, file_utils.build_file_name(program_name, version, True, ent_prefix))
      return ent_url
    elif program_name == 'consul' or program_name =='vault':
      if url.endswith('/'):
        ent_url = '{}{}/prem/{}/{}'.format(url, program_name, version, file_utils.build_file_name(program_name, version, True, ent_prefix))
      else:
        ent_url = '{}/{}/prem/{}/{}'.format(url, program_name, version, file_utils.build_file_name(program_name, version, True, ent_prefix))
      return ent_url
    else:
      print('No enterprise path for {}.  Exiting!'.format(program_name))
      sys.exit(1)
