import socket
from ui import console, print_header, print_error, print_success, print_info, ask_input, ask_back, create_table, RED_PALETTE
from rich.panel import Panel

def whois(domain):
    domain = domain.split('/')[0].replace('http://','').replace('https://','').strip()
    print_info(f"Querying WHOIS servers for [bold white]{domain}[/bold white]...")
    
    server = 'whois.verisign-grs.com'
    try:
        s = socket.create_connection(('whois.iana.org', 43), timeout=8)
        s.send((domain + '\r\n').encode())
        iana = s.recv(8192).decode('utf-8', errors='ignore')
        s.close()
        for line in iana.splitlines():
            if line.lower().startswith('whois:'):
                server = line.split(':',1)[1].strip()
                break
    except Exception:
        server = 'whois.verisign-grs.com'

    try:
        s = socket.create_connection((server, 43), timeout=12)
        s.send((domain + '\r\n').encode())
        data = b''
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        s.close()
        raw = data.decode('utf-8', errors='ignore')
        console.print()

        panel = Panel(
            raw.strip(),
            title=f"[{RED_PALETTE['primary_bold']}] WHOIS Record: {domain} ({server}) [/{RED_PALETTE['primary_bold']}]",
            border_style="#a8001e",
            padding=(1, 2)
        )
        console.print(panel)
    except Exception as e:
        print_error(f"WHOIS lookup failed: {e}")

def wip():
    while True:
        print_header("WHOIS Domain Lookup", category="OSINT / DOMAIN")
        domain = ask_input("Enter domain name (e.g. google.com)")
        if not domain:
            return
        whois(domain)

        if not ask_back("another domain"):
            return

if __name__ == "__main__":
    wip()