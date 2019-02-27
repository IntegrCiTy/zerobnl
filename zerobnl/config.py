import subprocess

# TODO: move to conftest.py ?
cmd = "git rev-parse --abbrev-ref HEAD"
BRANCH =  subprocess.check_output(cmd.split()).decode("utf-8").rstrip()

PORT_PUB_SUB = 5556
PORT_PUSH_PULL = 5557

TEMP_FOLDER = "TMP_FOLDER"

ORCH_FOLDER = "orch"
ORCH_CONFIG_FILE = "config.json"
# TODO: switch to relative path copy (and add to MANIFEST)
ORCH_STR_FILE = 'from zerobnl.kernel import Master\n\nif __name__ == "__main__":\n    orch = Master()\n    orch.run()\n'
ORCH_HOST_NAME = ORCH_FOLDER
ORCH_MAIN_FILE = "main.py"

NODE_CONFIG_FILE = "config.json"
NODE_WRAP_FILE = "wrapper.py"
NODE_DOCKERFILE = "Dockerfile"

DOCKER_COMPOSE_FILE = "docker-compose.yml"

START = "2000-01-01 00:00:00"

REDIS_PORT = 6379
REDIS_HOST_NAME = "ict_redis"

SIM_NET = "simulation"
