import os


import funcs.dtip
import funcs.iplp
import funcs.tracert

def menu():
    while True:
        print("[1] domain to ip (A, AAAA and etc.)")
        print("[2] ip lookup")
        print("[3] traceroute (tracert)")
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
        
if __name__ == "__main__":
    menu()
