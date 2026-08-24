import json

def ip_lookup():
    import requests
    from rich import print as rprint
    from rich.json import JSON
    
    while True:
        ip = input("enter ip address (or empty to return): ").strip()
        if not ip:
            return
        
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
            data = response.json()
            rprint(JSON(json.dumps(data, ensure_ascii=False)))

        except Exception as e:
            print(f"error: invalid ip or connection failed ({e})")

        back = input("\nlookup another ip? (y/n): ").lower().strip()
        if back != "y":
            return

if __name__ == "__main__":
    ip_lookup()