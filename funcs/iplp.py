import requests
import json

from rich import print as rprint
from rich.json import JSON

def ip_lookup():
    from sncflw import menu   

    while True:
        ip = input("enter ip address: ").strip()
        
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
            data = response.json()
            rprint(JSON(json.dumps(data, ensure_ascii=False)))

        except:
            print("error: invalid ip or no internet")

        back = input("\nback to menu? (y/n): ").lower().strip()
        if back == "y":
            print("\033[H\033[J", end="")
            menu()
        else:
            break

if __name__ == "__main__":
    ip_lookup()
