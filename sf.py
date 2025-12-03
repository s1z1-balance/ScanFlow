import os


import funcs.dtip

def menu():
    while True:
        print("[1] domain to ip (A, AAAA and etc.)")
        que = input("select option: ")
        if que == "1":
            print("\033[H\033[J", end="")           
            funcs.dtip.dtip()  # вызываем функцию явно
            break
        
if __name__ == "__main__":
    menu()
