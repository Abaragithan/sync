import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed

IS_WINDOWS = platform.system().lower() == "windows"


def ping_host(ip: str) -> bool:
    """
    Return True if host reachable, else False.
    Timeout: 1 second max per ping.
    """

    if IS_WINDOWS:
        cmd = ["ping", "-n", "1", "-w", "1000", ip]  # 1000 ms
    else:
        cmd = ["ping", "-c", "1", "-W", "1", ip]  # 1 second

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False


def check_many(hosts: list[str], max_workers: int = 50) -> dict:
    """
    Ping all hosts IN PARALLEL using a thread pool.
    return { ip : True/False }
    """

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
                results[ip] = future.result()
            except Exception:
                results[ip] = False

    return results
