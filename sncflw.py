import os
import time
import webbrowser

def menu():
    while True:
        print("\033[H\033[J", end="")
        print("[1] domain to ip (A, AAAA and etc.)    /    [2] ip lookup")
        print("[3] traceroute (tracert)    /    [4] wrapper nmap")
        print("[5] whois lookup    /    [6] SSL/TLS certificate checker")
        print("")
        print("[0] exit")
        print("[99] my github")
        que = input("select option: ")
        
        if que == "1":
            print("\033[H\033[J", end="")
            from funcs import dtip
            print("\033[H\033[J", end="")
            from funcs import dtip
            dtip.dtip()
            break
        elif que == "2":
            print("\033[H\033[J", end="")
            from funcs import iplp
            iplp.ip_lookup()
            break
        elif que == "3":
            print("\033[H\033[J", end="")
            from funcs import tracert
            tracert.tracert()
            break
        elif que == "4":
            print("\033[H\033[J", end="")
            from funcs import wnmap
            wnmap.wnmap()
            break
        elif que == "5":
            print("\033[H\033[J", end="")
            from funcs import whois
            whois.wip()
            break
        elif que == "6":
            print("\033[H\033[J", end="")
            from funcs import ctls
            ctls.ctls()
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