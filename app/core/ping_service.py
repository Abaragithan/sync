import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed


def ping_host(ip: str) -> bool:
    """
    Return True if host reachable, else False.
    Timeout: 1 second max per ping.
    """
    if platform.system().lower() == "windows":
        cmd = ["ping", "-n", "1", "-w", "1000", ip]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", ip]

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0


def check_many(hosts: list[str], max_workers: int = 50) -> dict:
    """
    Ping all hosts IN PARALLEL using a thread pool.
    All pings run at the same time — total time = slowest single ping.
    return { ip : True/False }
    """
    if not hosts:          # ← guard: nothing to ping
        return {}

    results = {}

    with ThreadPoolExecutor(max_workers=min(max_workers, len(hosts))) as executor:
        # Submit all pings at once
        future_to_ip = {
            executor.submit(ping_host, ip): ip
            for ip in hosts
        }

        # Collect results as they finish
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                results[ip] = future.result()
            except Exception:
                results[ip] = False  # treat error as offline

    return results