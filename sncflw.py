import os
import sys
import webbrowser

def menu():
    options = {
        "1": ("funcs.dtip", "dtip"),
        "2": ("funcs.iplp", "ip_lookup"),
        "3": ("funcs.tracert", "tracert"),
        "4": ("funcs.pscan", "pscan"),
        "5": ("funcs.subdomains", "subdomains"),
        "6": ("funcs.whois", "wip"),
        "7": ("funcs.ctls", "ctls"),
        "8": ("funcs.wnmap", "wnmap"),
    }
    
    while True:
        print("\033[H\033[J", end="")
        print("=== ScanFlow - Network Recon & Security Toolkit ===")
        print("")
        print("[1] domain to ip (DNS records)      /  [2] ip lookup (Geo / ASN)")
        print("[3] traceroute (tracert)            /  [4] fast port scanner (asyncio)")
        print("[5] subdomain finder (OSINT+DNS)    /  [6] whois lookup")
        print("[7] SSL/TLS certificate checker     /  [8] wrapper nmap")
        print("")
        print("[0] exit")
        print("[99] my github")
        print("")
        
        que = input("select option: ").strip()
        
        if que in options:
            print("\033[H\033[J", end="")
            module_name, func_name = options[que]
            try:
                module = __import__(module_name, fromlist=[func_name])
                getattr(module, func_name)()
            except Exception as e:
                print(f"\n[!] error running {func_name}: {e}")
                input("\npress enter to return to menu...")
        elif que == "0":
            print("\nbyeeeeeeee")
            sys.exit(0)
        elif que == "99":
            print("\ngive a star for the repo: https://github.com/s1z1-balance/ScanFlow")
            webbrowser.open_new("https://github.com/s1z1-balance/ScanFlow")
            input("\npress enter to return to menu...")

if __name__ == "__main__":
    menu()