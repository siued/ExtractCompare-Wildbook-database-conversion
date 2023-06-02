import docker

# WIP

def ensure_docker_wbia():
    try:
        client = docker.from_env()
        images = client.images.list()
        if not any(image.tags[0] == 'wildme/wildbook-ia' for image in images):
            client.images.pull('wildme/wildbook-ia')
        print(client.images.list())
    except Exception as e:
        print('Make sure Docker is running please')


ensure_docker_wbia()
