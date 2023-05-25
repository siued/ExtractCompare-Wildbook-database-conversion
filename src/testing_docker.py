import docker

client = docker.from_env()

# get a list of containers
wbia = client.containers.get('test-db-load-wbia')


