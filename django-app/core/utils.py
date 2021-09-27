'''
    Utility functions for the core app.
'''


def is_port_in_use(port: int):
    '''
        https://stackoverflow.com/a/52872579/5253580
    '''
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


# make sure the HOST has a named pip running
def start_code_server_instance(port: int, path, name="code-server"):
    import subprocess
    import os
    # print(dir(path), str(path))
    # path = os.environ.get("APP_HOST_DIR")
    path = os.environ.get("APP_HOST_DIR") + str(path)
    print(f"----> RUNNING CODE SERVER USING PORT {port} ON PATH {path}")
    code = subprocess.run(
        f'''echo 'docker run --rm --name {name} -e PUID=0 -e PGID=0 -e TZ=Europe/London -v "{path}:/source-code" -p {port}:8443 linuxserver/code-server:latest' > /hostpipe''',
        shell=True,
        text=True,
        capture_output=True
    )
    print(code, code.stdout)
