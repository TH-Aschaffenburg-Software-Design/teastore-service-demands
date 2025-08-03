import subprocess


def get_service_ip(service: str):
    return (
        subprocess.check_output(["scripts/get_service_ip.sh", service]).decode().strip()
    )
