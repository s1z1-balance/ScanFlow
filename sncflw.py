import os
import time
import webbrowser

import funcs.dtip
import funcs.iplp
import funcs.tracert
import funcs.wnmap
import funcs.whois
import funcs.ctls

def menu():
    while True:
        print("[1] domain to ip (A, AAAA and etc.)")
        print("[2] ip lookup")
        print("[3] traceroute (tracert)")
        print("[4] wrapper nmap")
        print("[5] whois lookup")
        print("[6] SSL/TLS certificate checker")
        print("")
        print("[0] exit")
        print("[99] my github")
        que = input("select option: ")
        if que == "1":
            print("\033[H\033[J", end="")           
            funcs.dtip.dtip()
            break
        elif que == "2":
            print("\033[H\033[J", end="")           
            funcs.iplp.ip_lookup()
            break
        elif que == "3":
            print("\033[H\033[J", end="")           
            funcs.tracert.tracert()
            break
        elif que == "4":
            print("\033[H\033[J", end="")           
            funcs.wnmap.wnmap()
            break
        elif que == "5":
            print("\033[H\033[J", end="")           
            funcs.whois.wip()
            break
        elif que == "6":
            print("\033[H\033[J", end="")           
            funcs.ctls.ctls()
            break
        elif que == "0":
            print("byeeeeeeee")
            time.sleep(1)
            break
        elif que == "99":
            print("give a star for the repo")
            webbrowser.open_new("github.com/s1z1-balance/ScanFlow")
            menu()
if __name__ == "__main__":
    menu()
