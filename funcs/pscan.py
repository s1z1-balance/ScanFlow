import asyncio
import socket
import time
import re
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from ui import console, print_header, print_error, print_success, print_info, ask_input, ask_back, create_table, RED_PALETTE

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
        SpinnerColumn(style=f"bold {RED_PALETTE['primary']}"),
        TextColumn(f"[bold {RED_PALETTE['accent']}]{{task.description}}[/bold {RED_PALETTE['accent']}]"),
        BarColumn(bar_width=40, style="dim #5a000e", complete_style=f"bold {RED_PALETTE['primary']}"),
        TextColumn(f"[bold {RED_PALETTE['text']}]{{task.percentage:>3.0f}}%[/bold {RED_PALETTE['text']}]"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"Scanning {target_ip}...", total=len(ports))
        
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
    except Exception:
        return None

def pscan():
    while True:
        print_header("Async TCP Port Scanner", category="PORT SCANNER")
        target = ask_input("Enter target domain/IP (empty to exit)")
        if not target:
            return

        target_ip = resolve_target(target)
        if not target_ip:
            print_error(f"Could not resolve host '{target}'")
            if not ask_back("another target"):
                return
            continue

        print_info(f"Target: [bold white]{target}[/bold white] -> [bold {RED_PALETTE['primary']}]{target_ip}[/]")
        console.print()
        console.print(f"  [{RED_PALETTE['tag']}][1][/{RED_PALETTE['tag']}] Quick Scan    (Top 100 ports)   ~ 1-2s")
        console.print(f"  [{RED_PALETTE['tag']}][2][/{RED_PALETTE['tag']}] Standard Scan (Top 1000 ports)  ~ 3-5s")
        console.print(f"  [{RED_PALETTE['tag']}][3][/{RED_PALETTE['tag']}] Full Scan     (All 1-65535)     ~ 20-30s")
        console.print(f"  [{RED_PALETTE['tag']}][4][/{RED_PALETTE['tag']}] Custom Ports  (e.g. 80,443,8000-8080)")
        console.print(f"  [{RED_PALETTE['tag']}][0][/{RED_PALETTE['tag']}] Back to menu")
        console.print()

        choice = ask_input("Choose scan mode", default="1")
        if choice == "1":
            ports = TOP_100_PORTS
        elif choice == "2":
            ports = get_top_1000_ports()
        elif choice == "3":
            ports = list(range(1, 65536))
        elif choice == "4":
            raw_ports = ask_input("Enter ports (e.g. 22,80,443,8000-8080)")
            ports = parse_custom_ports(raw_ports)
            if not ports:
                print_error("No valid ports specified.")
                continue
        elif choice == "0":
            return
        else:
            ports = TOP_100_PORTS

        console.print()
        print_info(f"Initiating async scan on [bold white]{len(ports)}[/bold white] ports...")
        console.print()
        t_start = time.time()
        
        try:
            open_results = asyncio.run(run_scan(target_ip, ports, concurrency=500, timeout=0.8))
        except Exception as e:
            print_error(f"Scan failed: {e}")
            continue

        duration = round(time.time() - t_start, 2)
        console.print()
        print_success(f"Scan finished in {duration}s. Found [bold {RED_PALETTE['primary']}]{len(open_results)}[/] open ports.")
        console.print()

        if open_results:
            table = create_table(
                title=f"Open Ports for {target} ({target_ip})",
                columns=[
                    ("PORT", {"style": f"bold {RED_PALETTE['primary']}", "width": 10}),
                    ("STATE", {"style": "bold green", "width": 8}),
                    ("SERVICE", {"style": "bold yellow", "width": 18}),
                    ("BANNER / DETAILS", {"style": "white", "width": 40}),
                    ("LATENCY", {"style": "magenta", "width": 10}),
                ]
            )

            for r in open_results:
                table.add_row(
                    str(r["port"]),
                    r["state"],
                    r["service"],
                    r["banner"] if r["banner"] else "-",
                    f"{r['rtt']} ms"
                )
            console.print(table)
        else:
            print_warning("No open ports discovered in target port range.")

        if not ask_back("another scan"):
            return

if __name__ == "__main__":
    pscan()
