import subprocess
import zipfile
import os
import sys

def run_cmd(command):
    subprocess.run(command.split(" "))

def unzip(filename, program_name):
    try:
        with zipfile.ZipFile(filename) as zfile:
            zfile.extractall(path='/tmp/')
    # python zipfile does not preserve executable permission
            os.chmod('/tmp/{}'.format(program_name), 0o755)
    except FileNotFoundError as fnf:
        print("Oh no!  There is no file to unzip!!  The error says: {}".format(fnf))
        sys.exit(1)
    except Exception as e:
        print("Something has gone terribly wrong: {}".format(e))
        sys.exit(1)