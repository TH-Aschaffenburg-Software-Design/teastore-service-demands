import subprocess


def get_property(key: str):
    return subprocess.check_output(["properties/get_property.sh", key]).decode().strip()
