import requests
import json

from rich import print as rprint
from rich.json import JSON

def ip_lookup():
    ip = input("enter ip address: ").strip()
    
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
        data = response.json()
        rprint(JSON(json.dumps(data, ensure_ascii=False)))

    except:
        print("error: invalid ip or no internet")

if __name__ == "__main__":
    ip_lookup()