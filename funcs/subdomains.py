import asyncio
import socket
import re
import requests
from rich.table import Table
from ui import console, print_header, print_error, print_success, print_info, print_warning, ask_input, ask_back, create_table, RED_PALETTE

COMMON_SUBDOMAINS = [
    "www", "mail", "remote", "blog", "webmail", "server", "ns1", "ns2", "smtp",
    "secure", "vpn", "api", "dev", "staging", "test", "portal", "admin", "app",
    "auth", "shop", "beta", "cloud", "cpanel", "autodiscover", "m", "support",
    "status", "git", "gitlab", "jenkins", "direct", "s3", "cdn", "stage", "corp",
    "internal", "vps", "preview", "prod", "demo", "dashboard", "monitor",
    "grafana", "kibana", "vault", "sso", "idp", "login", "docs", "help", "billing",
    "whm", "web", "router", "gw", "gateway", "mx", "pop", "imap", "relay",
    "db", "database", "sql", "redis", "elastic", "k8s", "node", "ns", "dns",
    "static", "assets", "media", "img", "files", "download", "pay", "payment",
    "member", "account", "client", "panel", "stage-api", "dev-api", "connect"
]

def clean_domain(domain):
    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain)
    domain = domain.split("/")[0].split(":")[0]
    return domain

def fetch_otx(domain):
    subs = set()
    try:
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
        resp = requests.get(url, timeout=5, headers={"User-Agent": "ScanFlow"})
        if resp.status_code == 200:
            data = resp.json()
            for record in data.get("passive_dns", []):
                hostname = record.get("hostname", "").lower().strip()
                if hostname.endswith(f".{domain}") or hostname == domain:
                    subs.add(hostname)
    except Exception:
        pass
    return subs

def fetch_hackertarget(domain):
    subs = set()
    try:
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        resp = requests.get(url, timeout=5, headers={"User-Agent": "ScanFlow"})
        if resp.status_code == 200 and "error" not in resp.text.lower():
            for line in resp.text.splitlines():
                parts = line.split(",")
                if parts:
                    host = parts[0].strip().lower()
                    if host.endswith(f".{domain}") or host == domain:
                        subs.add(host)
    except Exception:
        pass
    return subs

def fetch_crtsh(domain):
    subs = set()
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        resp = requests.get(url, timeout=4, headers={"User-Agent": "ScanFlow"})
        if resp.status_code == 200:
            for entry in resp.json():
                name_val = entry.get("name_value", "")
                for sub in name_val.split("\n"):
                    sub = sub.strip().lower().lstrip("*.")
                    if sub.endswith(f".{domain}") or sub == domain:
                        subs.add(sub)
    except Exception:
        pass
    return subs

async def resolve_subdomain(subdomain, semaphore):
    async with semaphore:
        loop = asyncio.get_running_loop()
        try:
            addrinfo = await loop.getaddrinfo(subdomain, None, family=socket.AF_INET)
            ips = sorted(list(set(item[4][0] for item in addrinfo)))
            return subdomain, ips
        except Exception:
            return subdomain, []

async def resolve_all(subdomains, concurrency=50):
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [resolve_subdomain(sub, semaphore) for sub in subdomains]
    results = await asyncio.gather(*tasks)
    return {sub: ips for sub, ips in results}

def find_subdomains(domain, include_bruteforce=True):
    domain = clean_domain(domain)
    found = {}

    print_info(f"Querying OSINT sources for [bold white]{domain}[/bold white]...")

    otx_results = fetch_otx(domain)
    for s in otx_results:
        found.setdefault(s, set()).add("AlienVault OTX")

    ht_results = fetch_hackertarget(domain)
    for s in ht_results:
        found.setdefault(s, set()).add("HackerTarget")

    crt_results = fetch_crtsh(domain)
    for s in crt_results:
        found.setdefault(s, set()).add("crt.sh")

    if include_bruteforce:
        for prefix in COMMON_SUBDOMAINS:
            sub = f"{prefix}.{domain}"
            if sub not in found:
                found.setdefault(sub, set()).add("Wordlist")

    all_subs = sorted(list(found.keys()))
    print_info(f"Verifying DNS resolution for [bold white]{len(all_subs)}[/bold white] candidate subdomains...")
    
    resolved = asyncio.run(resolve_all(all_subs))

    active_results = []
    for sub, ips in resolved.items():
        if ips:
            sources = ", ".join(sorted(found[sub]))
            active_results.append({
                "subdomain": sub,
                "ips": ips,
                "source": sources
            })

    active_results.sort(key=lambda x: x["subdomain"])
    return active_results

def subdomains():
    while True:
        print_header("Subdomain Enumeration", category="RECONNAISSANCE")
        target = ask_input("Enter domain (e.g. example.com)")
        if not target:
            return

        domain = clean_domain(target)
        if not domain:
            continue

        console.print()
        console.print(f"  [{RED_PALETTE['tag']}][1][/{RED_PALETTE['tag']}] Fast Search (Passive OSINT sources)")
        console.print(f"  [{RED_PALETTE['tag']}][2][/{RED_PALETTE['tag']}] Deep Search (Passive OSINT + Wordlist Brute-force)")
        console.print(f"  [{RED_PALETTE['tag']}][0][/{RED_PALETTE['tag']}] Back to menu")
        console.print()

        mode = ask_input("Choose mode", default="1")
        if mode == "1":
            include_bf = False
        elif mode == "2":
            include_bf = True
        elif mode == "0":
            return
        else:
            include_bf = False

        console.print()
        results = find_subdomains(domain, include_bruteforce=include_bf)
        console.print()

        if results:
            table = create_table(
                title=f"Discovered Active Subdomains for {domain}",
                columns=[
                    ("SUBDOMAIN", {"style": f"bold {RED_PALETTE['primary']}", "width": 38}),
                    ("IP ADDRESS(ES)", {"style": "bold yellow", "width": 26}),
                    ("SOURCE(S)", {"style": "white", "width": 24}),
                ]
            )

            for r in results:
                table.add_row(
                    r["subdomain"],
                    ", ".join(r["ips"]),
                    r["source"]
                )
            console.print(table)
            console.print()
            print_success(f"Discovered [bold {RED_PALETTE['primary']}]{len(results)}[/] active subdomains.")
        else:
            print_warning("No active subdomains discovered for this domain.")

        if not ask_back("another domain"):
            return

if __name__ == "__main__":
    subdomains()
