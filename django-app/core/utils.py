'''
    Utility functions for the core app.
'''


def is_port_in_use(port: int):
    '''
        https://stackoverflow.com/a/52872579/5253580
    '''
    # import socket
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     print(s.connect_ex(('localhost', port)) == 0)
    #     return s.connect_ex(('localhost', port)) == 0
    import subprocess as sp
    proc = sp.run(
        f'''echo 'lsof -i :{port}' > /hostpipe''',
        shell=True,
        text=True,
        capture_output=True,
        # stdout=sp.PIPE
    )
    print("~~~~~++++++~~~~~~>",proc)
    if proc.stderr == '':
        return False
    else:
        return True


def pipeCMD(cmd: str) -> str:
    '''
        Executes a command through the named pipe used by the system and returns its output
    '''
    import subprocess

    print(f"Running the command {cmd} throuhg the system's named pipe")
    code = subprocess.run(
        f'''echo '{cmd}' > /hostpipe''',
        shell=True,
        text=True,
        capture_output=True
    )
    return code.stdout
    

# make sure the HOST has a named pip running
def start_code_server_instance(port: int, path: str, name="code-server"):
    import subprocess
    import os

    path = os.environ.get("APP_HOST_DIR") + str(path)
    print(f"----> RUNNING CODE SERVER USING PORT {port} ON PATH {path}")
    code = subprocess.run(
        f'''echo 'docker run -d --rm --name {name} -e PUID=0 -e PGID=0 -e TZ=Europe/London -v "{path}:/{name}" -p {port}:8443 linuxserver/code-server:latest' > /hostpipe''',
        shell=True,
        text=True,
        capture_output=True
    )
    return code.stdout


def kill_code_server_instance(name: str):
    '''
        Tries to kill an instance named name
    '''
    print("~~~~~~~> Killing", name)
    # import subprocess
    
    # code = subprocess.run(
    #     f'''echo 'docker stop {name}' > /hostpipe''',
    #     shell=True,
    #     text=True,
    #     capture_output=True
    # )
    # print(code, code.stdout)
    pipeCMD(f"docker stop {name}")