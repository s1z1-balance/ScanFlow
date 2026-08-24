import asyncio
import socket
import time
import re
from rich import print as rprint
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

COMMON_SERVICES = {
    20: "FTP-Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 43: "WHOIS",
    53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP", 88: "Kerberos",
    110: "POP3", 111: "RPCBind", 123: "NTP", 135: "MS-RPC", 137: "NetBIOS-NS",
    138: "NetBIOS-DGM", 139: "NetBIOS-SSN", 143: "IMAP", 161: "SNMP", 162: "SNMP-Trap",
    179: "BGP", 389: "LDAP", 443: "HTTPS", 445: "Microsoft-DS", 465: "SMTPS",
    500: "ISAKMP", 514: "Syslog", 515: "LPD", 520: "RIP", 587: "Submission",
    631: "IPP", 636: "LDAPS", 873: "Rsync", 993: "IMAPS", 995: "POP3S",
    1080: "SOCKS", 1194: "OpenVPN", 1433: "MSSQL", 1434: "MSSQL-mgt", 1521: "Oracle",
    1723: "PPTP", 2049: "NFS", 2082: "cPanel", 2083: "cPanel-SSL", 2086: "WHM",
    2087: "WHM-SSL", 2181: "ZooKeeper", 2222: "SSH-Alt", 2375: "Docker",
    2376: "Docker-SSL", 3000: "Node/React/Grafana", 3128: "Squid-Proxy", 3306: "MySQL",
    3389: "RDP", 3690: "SVN", 4000: "Web-App", 4243: "Docker", 4840: "OPC-UA",
    5000: "Flask/Docker-Reg", 5001: "Control-Port", 5432: "PostgreSQL", 5672: "RabbitMQ",
    5900: "VNC", 5984: "CouchDB", 6000: "X11", 6379: "Redis", 6667: "IRC",
    7000: "Cassandra", 7001: "WebLogic", 7077: "Spark", 8000: "HTTP-Alt",
    8008: "HTTP-Alt", 8080: "HTTP-Proxy", 8081: "HTTP-Alt", 8088: "HTTP-Alt",
    8090: "HTTP-Alt", 8443: "HTTPS-Alt", 8888: "Jupyter/HTTP", 9000: "SonarQube/PHP",
    9042: "Cassandra", 9090: "Prometheus", 9092: "Kafka", 9100: "Node-Exporter",
    9200: "Elasticsearch", 9300: "Elasticsearch-Cluster", 9418: "Git", 9999: "Abyss",
    10000: "Webmin", 11211: "Memcached", 15672: "RabbitMQ-Mgmt", 27017: "MongoDB",
    27018: "MongoDB", 28017: "MongoDB-Web", 50000: "SAP", 50070: "Hadoop-HDFS",
}

TOP_100_PORTS = [
    20, 21, 22, 23, 25, 53, 69, 80, 88, 110, 111, 123, 135, 137, 138, 139, 143,
    161, 162, 179, 389, 443, 445, 465, 500, 514, 515, 520, 587, 631, 636, 873,
    993, 995, 1080, 1194, 1433, 1434, 1521, 1723, 2049, 2082, 2083, 2086, 2087,
    2181, 2222, 2375, 2376, 3000, 3128, 3306, 3389, 3690, 4000, 4243, 4840, 5000,
    5001, 5432, 5672, 5900, 5984, 6000, 6379, 6667, 7000, 7001, 7077, 8000, 8008,
    8080, 8081, 8088, 8090, 8443, 8888, 9000, 9042, 9090, 9092, 9100, 9200, 9300,
    9418, 9999, 10000, 11211, 15672, 27017, 27018, 28017, 50000, 50070
]

def get_top_1000_ports():
    ports = set(TOP_100_PORTS)
    ports.update(range(1, 1025))
    ports.update(COMMON_SERVICES.keys())
    extra_common = [
        1025, 1026, 1027, 1028, 1029, 1030, 1080, 1111, 1234, 1433, 1521, 1720,
        1723, 1812, 1813, 1900, 2000, 2001, 2049, 2121, 2222, 2375, 2376, 2483,
        2484, 3000, 3128, 3268, 3269, 3306, 3389, 3690, 4000, 4369, 4443, 4444,
        4567, 4840, 5000, 5001, 5060, 5061, 5432, 5671, 5672, 5900, 5901, 5984,
        5985, 5986, 6000, 6001, 6379, 6666, 6667, 7000, 7001, 7077, 7443, 7777,
        8000, 8001, 8008, 8080, 8081, 8082, 8088, 8090, 8443, 8888, 9000, 9001,
        9042, 9090, 9091, 9092, 9100, 9200, 9300, 9418, 9999, 10000, 11211,
        15672, 27017, 27018, 28017, 50000, 50070
    ]
    ports.update(extra_common)
    return sorted(list(ports))[:1000]

async def grab_banner(host, port, timeout=1.0):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
    except Exception:
        return ""

    banner = ""
    try:
        try:
            raw = await asyncio.wait_for(reader.read(256), timeout=0.3)
            if raw:
                banner = raw.decode("utf-8", errors="ignore").strip()
        except asyncio.TimeoutError:
            pass

        if not banner:
            probe = b"\r\n"
            if port in (80, 8080, 8000, 8081, 8088, 8090, 8888, 3000, 5000):
                probe = f"GET / HTTP/1.0\r\nHost: {host}\r\nUser-Agent: ScanFlow\r\n\r\n".encode()
            writer.write(probe)
            await writer.drain()
            try:
                raw = await asyncio.wait_for(reader.read(512), timeout=0.5)
                if raw:
                    text = raw.decode("utf-8", errors="ignore")
                    server_match = re.search(r"Server:\s*([^\r\n]+)", text, re.IGNORECASE)
                    if server_match:
                        banner = f"HTTP ({server_match.group(1).strip()})"
                    else:
                        first_line = text.splitlines()[0].strip() if text.splitlines() else ""
                        banner = first_line[:60]
            except asyncio.TimeoutError:
                pass
    except Exception:
        pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

    clean_banner = " ".join(banner.split())
    return clean_banner[:70]

async def check_port(host, port, semaphore, timeout=0.8):
    async with semaphore:
        t0 = time.time()
        try:
            conn = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(conn, timeout=timeout)
            rtt_ms = round((time.time() - t0) * 1000, 1)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

            service = COMMON_SERVICES.get(port, "unknown")
            banner = await grab_banner(host, port, timeout=1.0)
            return {"port": port, "state": "open", "service": service, "banner": banner, "rtt": rtt_ms}
        except Exception:
            return None

def parse_custom_ports(raw_str):
    ports = set()
    parts = raw_str.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            try:
                start_p, end_p = part.split("-", 1)
                s = int(start_p.strip())
                e = int(end_p.strip())
                if 1 <= s <= 65535 and 1 <= e <= 65535:
                    for p in range(min(s, e), max(s, e) + 1):
                        ports.add(p)
            except ValueError:
                continue
        else:
            try:
                p = int(part)
                if 1 <= p <= 65535:
                    ports.add(p)
            except ValueError:
                continue
    return sorted(list(ports))

async def run_scan(target_ip, ports, concurrency=500, timeout=0.8):
    semaphore = asyncio.Semaphore(concurrency)
    open_ports = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total} ports)"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(f"scanning {target_ip}...", total=len(ports))
        
        async def worker(p):
            res = await check_port(target_ip, p, semaphore, timeout)
            progress.update(task, advance=1)
            return res

        results = await asyncio.gather(*(worker(p) for p in ports))
        for res in results:
            if res is not None:
                open_ports.append(res)

    open_ports.sort(key=lambda x: x["port"])
    return open_ports

def resolve_target(target):
    try:
        return socket.gethostbyname(target)
    except Exception as e:
        return None

def pscan():
    while True:
        target = input("enter domain or ip (or empty to return): ").strip()
        if not target:
            return

        target_ip = resolve_target(target)
        if not target_ip:
            print(f"error: could not resolve host '{target}'")
            continue

        print(f"\ntarget: {target} ({target_ip})\n")
        print("[1] quick scan (top 100 ports) ~ 1-2s")
        print("[2] standard scan (top 1000 ports) ~ 3-5s")
        print("[3] full scan (all 1-65535 ports) ~ 20-30s")
        print("[4] custom ports (e.g. 80,443,8000-8080)")
        print("[0] back")

        choice = input("\nchoose scan mode: ").strip()
        if choice == "1":
            ports = TOP_100_PORTS
        elif choice == "2":
            ports = get_top_1000_ports()
        elif choice == "3":
            ports = list(range(1, 65536))
        elif choice == "4":
            raw_ports = input("enter ports (comma/range separated, e.g. 22,80,443,8000-8080): ").strip()
            ports = parse_custom_ports(raw_ports)
            if not ports:
                print("no valid ports specified.")
                continue
        elif choice == "0":
            return
        else:
            print("invalid choice.")
            continue

        print(f"\nstarting async port scan on {len(ports)} ports...")
        t_start = time.time()
        
        try:
            open_results = asyncio.run(run_scan(target_ip, ports, concurrency=500, timeout=0.8))
        except Exception as e:
            print(f"scan failed: {e}")
            continue

        duration = round(time.time() - t_start, 2)
        print(f"\nscan completed in {duration}s. found {len(open_results)} open ports.\n")

        if open_results:
            table = Table(title=f"Open Ports for {target} ({target_ip})", show_header=True, header_style="bold cyan")
            table.add_column("PORT", style="bold green", width=10)
            table.add_column("STATE", width=8)
            table.add_column("SERVICE", style="yellow", width=18)
            table.add_column("BANNER / DETAILS", style="white", width=40)
            table.add_column("LATENCY", style="magenta", width=10)

            for r in open_results:
                table.add_row(
                    str(r["port"]),
                    r["state"],
                    r["service"],
                    r["banner"] if r["banner"] else "-",
                    f"{r['rtt']} ms"
                )
            rprint(table)
        else:
            print("no open ports found.")

        back = input("\nscan another target? (y/n): ").lower().strip()
        if back != "y":
            return

if __name__ == "__main__":
    pscan()
