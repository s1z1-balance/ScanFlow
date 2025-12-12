import os
import webbrowser

def menu():
    options = {
        "1": ("funcs.dtip", "dtip"),
        "2": ("funcs.iplp", "ip_lookup"),
        "3": ("funcs.tracert", "tracert"),
        "4": ("funcs.wnmap", "wnmap"),
        "5": ("funcs.whois", "wip"),
        "6": ("funcs.ctls", "ctls"),
    }
    
    while True:
        print("\033[H\033[J", end="")
        print("[1] domain to ip (A, AAAA and etc.)    /    [2] ip lookup")
        print("[3] traceroute (tracert)    /    [4] wrapper nmap")
        print("[5] whois lookup    /    [6] SSL/TLS certificate checker")
        print("")
        print("[0] exit")
        print("[99] my github")
        
        que = input("select option: ")
        
        if que in options:
            print("\033[H\033[J", end="")
            module_name, func_name = options[que]
            module = __import__(module_name, fromlist=[func_name])
            getattr(module, func_name)()
            break
        elif que == "0":
            print("byeeeeeeee")
            os._exit(0)
        elif que == "99":
            print("give a star for the repo")
            webbrowser.open_new("github.com/s1z1-balance/ScanFlow")
            menu()

if __name__ == "__main__":
    menu()