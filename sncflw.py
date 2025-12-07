import os


import funcs.dtip
import funcs.iplp
import funcs.tracert
import funcs.wnmap
import funcs.whois

def menu():
    while True:
        print("[1] domain to ip (A, AAAA and etc.)")
        print("[2] ip lookup")
        print("[3] traceroute (tracert)")
        print("[4] wrapper nmap")
        print("[5] whois lookup")
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
        
if __name__ == "__main__":
    menu()
