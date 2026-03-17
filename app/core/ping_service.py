import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed

IS_WINDOWS = platform.system().lower() == "windows"


def detect_os_from_ping(output: str) -> str:
    output = output.lower()

    if "ttl=" in output:
        try:
            ttl = int(output.split("ttl=")[1].split()[0])

            if ttl >= 100:
                return "windows"
            else:
                return "linux"

        except Exception:
            return "unknown"

    return "unknown"


def ping_host(ip: str) -> tuple[bool, str]:
    if IS_WINDOWS:
        cmd = ["ping", "-n", "1", "-w", "1000", ip]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", ip]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        reachable = result.returncode == 0

        if reachable:
            os_type = detect_os_from_ping(result.stdout)
        else:
            os_type = "unknown"

        return reachable, os_type

    except Exception:
        return False, "unknown"


def check_many(hosts: list[str], max_workers: int = 50) -> dict:
    if not hosts:
        return {}

    results = {}

    with ThreadPoolExecutor(max_workers=min(max_workers, len(hosts))) as executor:
        future_to_ip = {
            executor.submit(ping_host, ip): ip
            for ip in hosts
        }

        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                results[ip] = future.result()  # (reachable, os)
            except Exception:
                results[ip] = (False, "unknown")

    return results