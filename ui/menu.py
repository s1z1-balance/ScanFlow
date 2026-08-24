import sys
import webbrowser
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

from ui.theme import RED_PALETTE
from ui.banner import get_header_panel
from ui.components import console, clear_screen, print_error

MODULES = [
    {
        "id": "1",
        "category": "DNS & DOMAIN",
        "name": "DNS Records Extractor",
        "desc": "A, AAAA, MX, TXT, SOA, CAA, SRV records",
        "target": ("funcs.dtip", "dtip")
    },
    {
        "id": "2",
        "category": "OSINT / IP",
        "name": "IP Geolocation & ASN",
        "desc": "ISP, organization, coordinates, AS info",
        "target": ("funcs.iplp", "ip_lookup")
    },
    {
        "id": "3",
        "category": "ROUTING",
        "name": "ICMP Traceroute",
        "desc": "Hop latency and hostname resolution",
        "target": ("funcs.tracert", "tracert")
    },
    {
        "id": "4",
        "category": "PORT SCANNER",
        "name": "Async TCP Port Scanner",
        "desc": "Pure Python fast scanner + banner grabber",
        "target": ("funcs.pscan", "pscan")
    },
    {
        "id": "5",
        "category": "RECON",
        "name": "Subdomain Enumeration",
        "desc": "Passive OSINT (OTX, HT) + Async DNS",
        "target": ("funcs.subdomains", "subdomains")
    },
    {
        "id": "6",
        "category": "OSINT / DOMAIN",
        "name": "WHOIS Lookup",
        "desc": "Registrar, creation & expiration data",
        "target": ("funcs.whois", "wip")
    },
    {
        "id": "7",
        "category": "SSL / TLS",
        "name": "SSL/TLS Cert Inspector",
        "desc": "SANs, chain validation & expiry audit",
        "target": ("funcs.ctls", "ctls")
    },
    {
        "id": "8",
        "category": "NMAP WRAPPER",
        "name": "Nmap CLI Scanner",
        "desc": "Advanced NSE scripts (-sC, -sV, vuln)",
        "target": ("funcs.wnmap", "wnmap")
    },
]

def render_main_menu():
    clear_screen()
    banner, subtitle = get_header_panel()
    console.print(banner)
    console.print(subtitle)
    console.print()

    table = Table(
        title=f"[{RED_PALETTE['primary_bold']}]✦ SYSTEM MODULES ✦[/{RED_PALETTE['primary_bold']}]",
        title_style="bold #ff1e42",
        header_style="bold #ffffff on #5a000e",
        border_style="#7a0015",
        row_styles=["none"],
        expand=True,
        padding=(0, 1)
    )
    
    table.add_column("NUM", style=f"bold {RED_PALETTE['primary']}", justify="center", width=7, no_wrap=True)
    table.add_column("CATEGORY", style=f"bold {RED_PALETTE['accent']}", width=16, no_wrap=True)
    table.add_column("MODULE", style="bold white", width=26, no_wrap=True)
    table.add_column("DESCRIPTION", style=RED_PALETTE['text_dim'])

    for mod in MODULES:
        num_tag = f"[{RED_PALETTE['tag']}][{mod['id'].zfill(2)}][/{RED_PALETTE['tag']}]"
        table.add_row(
            num_tag,
            mod["category"],
            mod["name"],
            mod["desc"]
        )

    table.add_section()
    table.add_row(
        f"[{RED_PALETTE['tag']}][99][/{RED_PALETTE['tag']}]",
        "PROJECT",
        "GitHub Repository",
        "Star & view project source code"
    )
    table.add_row(
        f"[{RED_PALETTE['tag']}][00][/{RED_PALETTE['tag']}]",
        "SYSTEM",
        "Exit Application",
        "Terminate ScanFlow session"
    )

    console.print(table)
    console.print()

def start_tui():
    options_map = {mod["id"]: mod["target"] for mod in MODULES}
    options_map.update({mod["id"].zfill(2): mod["target"] for mod in MODULES})

    while True:
        render_main_menu()
        prompt_str = f"[bold {RED_PALETTE['primary']}]scanflow[/bold {RED_PALETTE['primary']}][dim]@[/dim][bold {RED_PALETTE['accent']}]core[/bold {RED_PALETTE['accent']}] [bold white]#[/bold white] "
        choice = console.input(prompt_str).strip()

        if choice in ("0", "00", "exit", "quit", "q"):
            console.print(f"\n[{RED_PALETTE['primary']}][*] Terminating ScanFlow session. Goodbye![/]")
            sys.exit(0)
        elif choice == "99":
            console.print(f"\n[{RED_PALETTE['warning']}][*] Opening https://github.com/s1z1-balance/ScanFlow...[/]")
            webbrowser.open_new("https://github.com/s1z1-balance/ScanFlow")
            console.input("\n[dim]Press Enter to return to menu...[/dim]")
        elif choice in options_map:
            module_name, func_name = options_map[choice]
            try:
                module = __import__(module_name, fromlist=[func_name])
                func = getattr(module, func_name)
                func()
            except Exception as e:
                print_error(f"Execution failure in {func_name}: {e}")
                console.input("\n[dim]Press Enter to return to menu...[/dim]")
