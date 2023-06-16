import time
import docker
from tkinter import Tk
from tkinter.filedialog import askdirectory
import requests

# TODO: change
container_name = 'wildbook-ia-last-chance'


def check_docker_running():
    try:
        docker.from_env().ping()
        return True
    except Exception:
        return False


def check_wbia_container_exists():
    client = docker.from_env()
    containers = client.containers.list(all=True)
    # check if a container with the correct name exists, and make sure it is based on the correct image
    return any(
        container.name == container_name and 'wildme/wbia:latest' in container.image.tags for container in containers)


def ensure_docker_wbia(port=8081):
    if not check_docker_running():
        print('Docker is not running, please start Docker and try again.')
        return False
    try:
        client = docker.from_env()
        images = client.images.list()
        if not any(image.tags[0] == 'wildme/wbia:latest' for image in images):
            print('Downloading Docker image (~15GB), this may take a while...')
            client.images.pull('wildme/wbia')
            print('Docker image downloaded successfully.')
    except Exception as e:
        print('Make sure Docker is running please')
        return False
    else:
        print('Docker is running and ready to host the Wildbook backend.')
        ensure_wbia_container(client, port)
        return True


# can also be used to start the container in the event of a crash
def ensure_wbia_container(client, port):
    if not check_wbia_container_exists():
        print('Creating container...')
        db_path = select_folder("Select the folder with an existing database or where you would like a new "
                                "database to be created")
        volumes = {db_path: {'bind': '/data/docker/', 'mode': 'rw'}}
        # set max memory to 4GB, default is not enough
        client.containers.run('wildme/wbia', name=container_name, ports={'5000/tcp': port}, detach=True,
                              mem_limit='4g', volumes=volumes)
        print('Container created successfully.')
    container = client.containers.get(container_name)
    if container.status != 'running':
        print('Starting Wildbook container')
        container.start()
        # wait for the server to start
        while True:
            try:
                requests.get(f'http://localhost:{port}/api/test')
                break
            except requests.ConnectionError:
                time.sleep(1)
    print('Wildbook backend is running.')


def select_folder(title):
    Tk().withdraw()  # Hide the main window
    folder_path = askdirectory(title=title)
    return folder_path


# assuming the container is running
def stop_wbia_container():
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        container.stop()
        print('Wildbook backend stopped successfully.')
    except Exception:
        print('Failed while trying to stop the container')
